"""
Venue and venue intelligence database models.
"""

from sqlalchemy import Column, String, Integer, DECIMAL, ARRAY, ForeignKey, DateTime, Text, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Venue(Base):
    """Restaurant or venue."""

    __tablename__ = "venues"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    address = Column(Text)
    neighborhood = Column(String, index=True)
    city = Column(String, default="New York")
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))

    # Categorization
    category = Column(String)  # restaurant, bar, cafe, activity
    cuisines = Column(ARRAY(String))
    price_level = Column(Integer)  # 1-4 ($-$$$$)
    rating = Column(DECIMAL(2, 1))

    # Booking info
    resy_slug = Column(String)
    opentable_id = Column(String)
    google_place_id = Column(String, index=True)
    yelp_id = Column(String)

    # Contact and hours
    hours = Column(JSONB)  # {"monday": {"open": "17:00", "close": "23:00"}, ...}
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

    venue_id = Column(UUID(as_uuid=True), ForeignKey("venues.id", ondelete="CASCADE"), primary_key=True)

    # Structured intelligence (stored as JSONB)
    seating_recommendations = Column(JSONB)  # List[SeatingRecommendation]
    dish_recommendations = Column(JSONB)  # List[DishRecommendation]
    timing_insights = Column(JSONB)  # TimingInsight
    commute_insights = Column(JSONB)  # CommuteInsight
    vibe_check = Column(JSONB)  # VibeCheck
    insider_tips = Column(JSONB)  # List[InsiderTip]
    warnings = Column(ARRAY(String))

    # Scores
    date_score = Column(DECIMAL(3, 1))  # 0-10
    trending_score = Column(DECIMAL(3, 1))  # 0-10
    intelligence_score = Column(DECIMAL(3, 2))  # 0-1, completeness of data

    # Raw source data
    reddit_data = Column(JSONB)
    tiktok_data = Column(JSONB)
    google_reviews_summary = Column(JSONB)
    resy_reviews_summary = Column(JSONB)
    opentable_reviews_summary = Column(JSONB)

    # Metadata
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    update_frequency_hours = Column(Integer, default=168)  # Weekly

    # Relationships
    venue = relationship("Venue", back_populates="intelligence")


class IntelligenceJob(Base):
    """Background job for gathering venue intelligence."""

    __tablename__ = "intelligence_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    venue_id = Column(UUID(as_uuid=True), ForeignKey("venues.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, default="pending")  # pending, running, completed, failed
    agents_completed = Column(ARRAY(String))
    error_message = Column(Text)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
