"""
Planning session models for collaborative date planning.
"""

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Date, JSON
from app.types import GUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class PlanningSession(Base):
    """Collaborative planning session."""

    __tablename__ = "planning_sessions"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String)  # "Saturday Night Date"
    created_by = Column(GUID, ForeignKey("users.id"), nullable=False)
    invite_code = Column(String, unique=True, nullable=False, index=True)

    # Planning details
    target_date = Column(Date)
    status = Column(String, default="draft")  # draft, voting, finalizing, confirmed

    # Merged constraints (intersection of all participant preferences)
    merged_constraints = Column(JSON)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    participants = relationship("SessionParticipant", back_populates="session", cascade="all, delete-orphan")
    suggested_venues = relationship("SessionVenue", back_populates="session", cascade="all, delete-orphan")
    votes = relationship("VenueVote", back_populates="session", cascade="all, delete-orphan")
    itinerary = relationship("Itinerary", back_populates="session", uselist=False)


class SessionParticipant(Base):
    """Participant in a planning session."""

    __tablename__ = "session_participants"

    session_id = Column(GUID, ForeignKey("planning_sessions.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role = Column(String, default="participant")  # organizer, participant
    location_id = Column(GUID, ForeignKey("user_locations.id"))
    preferences_override = Column(JSON)  # Session-specific preferences
    joined_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("PlanningSession", back_populates="participants")
    user = relationship("User", back_populates="session_participations")
    location = relationship("UserLocation")


class SessionVenue(Base):
    """Venue suggested for a session."""

    __tablename__ = "session_venues"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    session_id = Column(GUID, ForeignKey("planning_sessions.id", ondelete="CASCADE"), nullable=False)
    venue_id = Column(GUID, ForeignKey("venues.id", ondelete="CASCADE"), nullable=False)
    suggested_by = Column(GUID, ForeignKey("users.id"), nullable=False)
    suggested_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("PlanningSession", back_populates="suggested_venues")
    venue = relationship("Venue", back_populates="session_suggestions")


class VenueVote(Base):
    """Vote on a venue in a session."""

    __tablename__ = "venue_votes"

    session_id = Column(GUID, ForeignKey("planning_sessions.id", ondelete="CASCADE"), primary_key=True)
    venue_id = Column(GUID, ForeignKey("venues.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(GUID, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    vote = Column(Integer, nullable=False)  # -1 (veto), 0 (neutral), 1 (like), 2 (love)
    comment = Column(Text)
    voted_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    session = relationship("PlanningSession", back_populates="votes")
