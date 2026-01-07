"""
User and user-related database models.
"""

from sqlalchemy import Column, String, Boolean, Integer, DECIMAL, ARRAY, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base


class User(Base):
    """User account."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    locations = relationship("UserLocation", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    session_participations = relationship("SessionParticipant", back_populates="user")


class UserLocation(Base):
    """User location (can have multiple: home, work, etc.)."""

    __tablename__ = "user_locations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    label = Column(String)  # "home", "work", "partner's place"
    address = Column(Text)
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    neighborhood = Column(String)
    is_default = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="locations")


class UserPreferences(Base):
    """User preferences for date planning."""

    __tablename__ = "user_preferences"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    default_budget_min = Column(Integer)  # 1-4 ($-$$$$)
    default_budget_max = Column(Integer)
    cuisines_loved = Column(ARRAY(String))
    cuisines_avoid = Column(ARRAY(String))
    dietary_restrictions = Column(ARRAY(String))
    vibes = Column(ARRAY(String))  # romantic, adventurous, casual, etc.
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="preferences")
