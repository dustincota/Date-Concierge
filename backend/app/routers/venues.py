"""
Venue endpoints for searching and managing venues.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.venue import Venue, VenueIntelligence
from app.models.user import User
from app.schemas.venue import (
    Venue as VenueSchema,
    VenueCreate,
    VenueWithIntelligence,
    VenueIntelligence as VenueIntelligenceSchema,
)
from app.services.auth import get_current_user
from app.services.geocoding import GeocodingService

router = APIRouter()


@router.get("", response_model=List[VenueSchema])
def search_venues(
    neighborhood: Optional[str] = None,
    cuisine: Optional[str] = None,
    price_level: Optional[int] = Query(None, ge=1, le=4),
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    db: Session = Depends(get_db),
):
    """
    Search for venues with filters.

    Args:
        neighborhood: Filter by neighborhood
        cuisine: Filter by cuisine type
        price_level: Filter by price level (1-4)
        min_rating: Minimum rating filter
        db: Database session

    Returns:
        List of venues matching filters
    """
    query = db.query(Venue)

    if neighborhood:
        query = query.filter(Venue.neighborhood.ilike(f"%{neighborhood}%"))

    if cuisine:
        query = query.filter(Venue.cuisines.contains([cuisine]))

    if price_level:
        query = query.filter(Venue.price_level == price_level)

    if min_rating:
        query = query.filter(Venue.rating >= min_rating)

    venues = query.order_by(Venue.rating.desc()).limit(50).all()
    return venues


@router.get("/trending", response_model=List[VenueWithIntelligence])
def get_trending_venues(
    neighborhood: Optional[str] = None,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    Get trending venues based on intelligence data.

    Args:
        neighborhood: Filter by neighborhood
        limit: Number of venues to return
        db: Database session

    Returns:
        List of trending venues with intelligence
    """
    query = db.query(Venue).join(VenueIntelligence)

    if neighborhood:
        query = query.filter(Venue.neighborhood.ilike(f"%{neighborhood}%"))

    venues = (
        query.filter(VenueIntelligence.trending_score.isnot(None))
        .order_by(VenueIntelligence.trending_score.desc())
        .limit(limit)
        .all()
    )

    return venues


@router.get("/{venue_id}", response_model=VenueWithIntelligence)
def get_venue(
    venue_id: str,
    db: Session = Depends(get_db),
):
    """
    Get venue details with intelligence.

    Args:
        venue_id: Venue ID
        db: Database session

    Returns:
        Venue with intelligence data

    Raises:
        HTTPException: If venue not found
    """
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found",
        )

    return venue


@router.post("", response_model=VenueSchema, status_code=status.HTTP_201_CREATED)
async def create_venue(
    venue_data: VenueCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new venue.

    Args:
        venue_data: Venue creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created venue
    """
    # If address provided but no coordinates, geocode it
    if venue_data.address and not (venue_data.latitude and venue_data.longitude):
        geocode_result = await GeocodingService.geocode_address(venue_data.address)
        if geocode_result:
            venue_data.latitude = geocode_result["latitude"]
            venue_data.longitude = geocode_result["longitude"]
            if not venue_data.neighborhood:
                venue_data.neighborhood = geocode_result.get("neighborhood")

    db_venue = Venue(**venue_data.model_dump())
    db.add(db_venue)
    db.commit()
    db.refresh(db_venue)

    return db_venue


@router.get("/{venue_id}/intelligence", response_model=VenueIntelligenceSchema)
def get_venue_intelligence(
    venue_id: str,
    db: Session = Depends(get_db),
):
    """
    Get intelligence data for a venue.

    Args:
        venue_id: Venue ID
        db: Database session

    Returns:
        Venue intelligence data

    Raises:
        HTTPException: If venue or intelligence not found
    """
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found",
        )

    intelligence = (
        db.query(VenueIntelligence)
        .filter(VenueIntelligence.venue_id == venue_id)
        .first()
    )

    if not intelligence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intelligence data not available for this venue",
        )

    # Format the response
    return VenueIntelligenceSchema(
        venue_id=venue.id,
        venue_name=venue.name,
        last_updated=intelligence.last_updated,
        intelligence_score=float(intelligence.intelligence_score or 0),
        seating=intelligence.seating_recommendations or [],
        top_dishes=intelligence.dish_recommendations or [],
        dishes_to_skip=[],
        timing=intelligence.timing_insights,
        commute=intelligence.commute_insights,
        vibe=intelligence.vibe_check,
        insider_tips=intelligence.insider_tips or [],
        warnings=intelligence.warnings or [],
        trending_score=float(intelligence.trending_score or 0),
    )


@router.post("/{venue_id}/intelligence/refresh", status_code=status.HTTP_202_ACCEPTED)
async def refresh_venue_intelligence(
    venue_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Trigger intelligence refresh for a venue.

    Args:
        venue_id: Venue ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Job ID for tracking

    Raises:
        HTTPException: If venue not found
    """
    venue = db.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found",
        )

    # Import here to avoid circular dependency
    from app.tasks.intelligence import gather_venue_intelligence

    # Trigger Celery task
    task = gather_venue_intelligence.delay(str(venue_id))

    return {
        "message": "Intelligence gathering started",
        "job_id": task.id,
        "venue_id": venue_id,
    }


@router.get("/nearby")
async def get_nearby_venues(
    latitude: float,
    longitude: float,
    radius_miles: float = Query(2.0, ge=0.1, le=10),
    db: Session = Depends(get_db),
):
    """
    Get venues near a location.

    Args:
        latitude: Center latitude
        longitude: Center longitude
        radius_miles: Search radius in miles
        db: Database session

    Returns:
        List of nearby venues with distances
    """
    # Simple distance calculation (not using PostGIS for simplicity)
    # In production, use PostGIS for better performance
    from app.services.geocoding import GeocodingService

    venues = db.query(Venue).filter(
        Venue.latitude.isnot(None),
        Venue.longitude.isnot(None),
    ).all()

    nearby = []
    for venue in venues:
        distance = GeocodingService.calculate_distance(
            latitude, longitude,
            float(venue.latitude), float(venue.longitude)
        )
        if distance <= radius_miles:
            nearby.append({
                "venue": venue,
                "distance_miles": round(distance, 2),
            })

    # Sort by distance
    nearby.sort(key=lambda x: x["distance_miles"])

    return nearby[:50]
