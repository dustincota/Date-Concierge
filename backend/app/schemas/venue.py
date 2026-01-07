"""
Venue schemas for request/response validation.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class VenueBase(BaseModel):
    """Base schema for venue."""

    name: str
    address: Optional[str] = None
    neighborhood: Optional[str] = None
    city: str = "New York"
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    category: Optional[str] = None
    cuisines: List[str] = []
    price_level: Optional[int] = None
    rating: Optional[Decimal] = None


class VenueCreate(VenueBase):
    """Schema for creating a venue."""

    google_place_id: Optional[str] = None
    resy_slug: Optional[str] = None
    opentable_id: Optional[str] = None
    yelp_id: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    hours: Optional[Dict[str, Any]] = None


class Venue(VenueBase):
    """Schema for venue response."""

    id: UUID
    google_place_id: Optional[str] = None
    resy_slug: Optional[str] = None
    opentable_id: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    hours: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SeatingRecommendation(BaseModel):
    """Where to sit at a venue."""

    spot: str
    why: str
    how_to_request: str
    best_for: List[str]
    source: str
    source_url: Optional[str] = None
    mentions: int
    confidence: float


class DishRecommendation(BaseModel):
    """What to order."""

    item: str
    category: str
    description: Optional[str] = None
    price: Optional[float] = None
    mentions: int
    sentiment: float
    must_try: bool
    pro_tips: List[str] = []
    pairings: List[str] = []
    avoid_if: List[str] = []
    sources: List[Dict[str, str]] = []
    photos: List[str] = []


class TimingInsight(BaseModel):
    """When to go."""

    best_times: List[Dict[str, str]]
    avoid_times: List[Dict[str, str]]
    typical_wait_times: Dict[str, int]
    sweet_spot: str
    reservation_difficulty: str
    advance_booking_days: int
    walk_in_friendly: bool
    best_for_walk_in: Optional[str] = None


class CommuteInsight(BaseModel):
    """How to get there."""

    address: str
    neighborhood: str
    nearest_subway: Optional[str] = None
    subway_walk_minutes: Optional[int] = None
    best_transit_route: Optional[str] = None
    parking_situation: Optional[str] = None
    parking_tips: Optional[str] = None
    nearby_garages: List[Dict[str, Any]] = []
    rideshare_dropoff: Optional[str] = None
    rideshare_pickup: Optional[str] = None
    surge_warning: Optional[str] = None
    from_manhattan: Optional[str] = None
    from_williamsburg: Optional[str] = None


class VibeCheck(BaseModel):
    """What's it actually like."""

    noise_level: str
    noise_notes: Optional[str] = None
    lighting: str
    music: str
    crowd_type: List[str]
    age_range: str
    dress_code: str
    date_score: float
    first_date: bool
    anniversary: bool
    casual_date: bool
    impressive_date: bool
    double_date: bool
    vibe_tags: List[str]
    not_great_for: List[str] = []


class InsiderTip(BaseModel):
    """Specific actionable tip."""

    tip: str
    category: str
    source: str
    source_url: Optional[str] = None
    upvotes: int = 0


class VenueIntelligence(BaseModel):
    """Complete intelligence package for a venue."""

    venue_id: UUID
    venue_name: str
    last_updated: datetime
    intelligence_score: float
    seating: List[SeatingRecommendation] = []
    top_dishes: List[DishRecommendation] = []
    dishes_to_skip: List[DishRecommendation] = []
    timing: Optional[TimingInsight] = None
    commute: Optional[CommuteInsight] = None
    vibe: Optional[VibeCheck] = None
    insider_tips: List[InsiderTip] = []
    warnings: List[str] = []
    good_to_know: List[str] = []
    trending_score: Optional[float] = None
    reddit_sentiment: Optional[float] = None
    recent_buzz: List[str] = []

    class Config:
        from_attributes = True


class VenueWithIntelligence(Venue):
    """Venue with intelligence data."""

    intelligence: Optional[VenueIntelligence] = None

    class Config:
        from_attributes = True


class IntelligenceJobStatus(BaseModel):
    """Status of an intelligence gathering job."""

    id: UUID
    venue_id: UUID
    status: str
    agents_completed: List[str] = []
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
