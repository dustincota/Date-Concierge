"""
Venue and venue intelligence database models.
"""

from sqlalchemy import Column, String, Integer, DECIMAL, ForeignKey, DateTime, Text, Float, JSON
from app.types import GUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Venue(Base):
    """Restaurant or venue."""

    __tablename__ = "venues"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    address = Column(Text)
    neighborhood = Column(String, index=True)
    city = Column(String, default="New York")
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))

    # Categorization
    category = Column(String)  # restaurant, bar, cafe, activity
    cuisines = Column(JSON)
    price_level = Column(Integer)  # 1-4 ($-$$$$)
    rating = Column(DECIMAL(2, 1))

    # Booking info
    resy_slug = Column(String)
    opentable_id = Column(String)
    google_place_id = Column(String, index=True)
    yelp_id = Column(String)

    # Contact and hours
    hours = Column(JSON)  # {"monday": {"open": "17:00", "close": "23:00"}, ...}
    phone = Column(String)
    website = Column(String)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    intelligence = relationship("VenueIntelligence", back_populates="venue", uselist=False, cascade="all, delete-orphan")
    session_suggestions = relationship("SessionVenue", back_populates="venue")
    itinerary_stops = relationship("ItineraryStop", back_populates="venue")


class VenueIntelligence(Base):
    """Intelligence data for a venue (scraped from social media, reviews, etc.)."""

    __tablename__ = "venue_intelligence"

    venue_id = Column(GUID, ForeignKey("venues.id", ondelete="CASCADE"), primary_key=True)

    # Structured intelligence (stored as JSON)
    seating_recommendations = Column(JSON)  # List[SeatingRecommendation]
    dish_recommendations = Column(JSON)  # List[DishRecommendation]
    timing_insights = Column(JSON)  # TimingInsight
    commute_insights = Column(JSON)  # CommuteInsight
    vibe_check = Column(JSON)  # VibeCheck
    insider_tips = Column(JSON)  # List[InsiderTip]
    warnings = Column(JSON)

    # Scores
    date_score = Column(DECIMAL(3, 1))  # 0-10
    trending_score = Column(DECIMAL(3, 1))  # 0-10
    intelligence_score = Column(DECIMAL(3, 2))  # 0-1, completeness of data

    # Raw source data
    reddit_data = Column(JSON)
    tiktok_data = Column(JSON)
    google_reviews_summary = Column(JSON)
    resy_reviews_summary = Column(JSON)
    opentable_reviews_summary = Column(JSON)

    # Metadata
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    update_frequency_hours = Column(Integer, default=168)  # Weekly

    # Relationships
    venue = relationship("Venue", back_populates="intelligence")


class IntelligenceJob(Base):
    """Background job for gathering venue intelligence."""

    __tablename__ = "intelligence_jobs"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    venue_id = Column(GUID, ForeignKey("venues.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, default="pending")  # pending, running, completed, failed
    agents_completed = Column(JSON)
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
