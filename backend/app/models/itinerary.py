"""
Itinerary and reservation models.
"""

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Date, Time
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class Itinerary(Base):
    """Complete date itinerary."""

    __tablename__ = "itineraries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("planning_sessions.id"), unique=True)
    title = Column(String)
    date = Column(Date, nullable=False)
    weather_data = Column(JSONB)  # Weather forecast for the date
    status = Column(String, default="draft")  # draft, confirmed, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    session = relationship("PlanningSession", back_populates="itinerary")
    stops = relationship("ItineraryStop", back_populates="itinerary", cascade="all, delete-orphan", order_by="ItineraryStop.stop_order")


class ItineraryStop(Base):
    """Individual stop in an itinerary (venue visit)."""

    __tablename__ = "itinerary_stops"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    itinerary_id = Column(UUID(as_uuid=True), ForeignKey("itineraries.id", ondelete="CASCADE"), nullable=False)
    venue_id = Column(UUID(as_uuid=True), ForeignKey("venues.id"), nullable=False)
    stop_order = Column(Integer, nullable=False)  # 1, 2, 3...

    # Timing
    arrival_time = Column(Time)
    duration_minutes = Column(Integer)

    # Intelligence-based recommendations
    notes = Column(Text)
    seating_request = Column(String)  # "Request patio table 12"
    order_recommendations = Column(ARRAY(String))  # ["Cacio e Pepe", "Orange Wine"]

    # Backup
    backup_venue_id = Column(UUID(as_uuid=True), ForeignKey("venues.id"))

    # Travel from previous stop
    travel_from_previous = Column(JSONB)  # {"mode": "walk", "duration_minutes": 15, "instructions": "..."}

    # Relationships
    itinerary = relationship("Itinerary", back_populates="stops")
    venue = relationship("Venue", foreign_keys=[venue_id], back_populates="itinerary_stops")
    backup_venue = relationship("Venue", foreign_keys=[backup_venue_id])
    reservation = relationship("Reservation", back_populates="itinerary_stop", uselist=False)


class Reservation(Base):
    """Restaurant reservation."""

    __tablename__ = "reservations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    itinerary_stop_id = Column(UUID(as_uuid=True), ForeignKey("itinerary_stops.id", ondelete="CASCADE"))
    venue_id = Column(UUID(as_uuid=True), ForeignKey("venues.id"), nullable=False)

    # Reservation details
    date = Column(Date, nullable=False)
    time = Column(Time, nullable=False)
    party_size = Column(Integer, nullable=False)

    # Platform
    platform = Column(String)  # resy, opentable, direct
    confirmation_number = Column(String)
    status = Column(String, default="pending")  # pending, confirmed, cancelled
    booking_link = Column(String)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    itinerary_stop = relationship("ItineraryStop", back_populates="reservation")
