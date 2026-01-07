"""
Session schemas for collaborative planning.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID


class ParticipantPreferences(BaseModel):
    """Participant preferences for the session."""

    budget_min: Optional[int] = None
    budget_max: Optional[int] = None
    cuisines_loved: List[str] = []
    cuisines_avoid: List[str] = []
    dietary_restrictions: List[str] = []
    vibes: List[str] = []


class SessionParticipantBase(BaseModel):
    """Base schema for session participant."""

    user_id: UUID
    role: str = "participant"
    location_id: Optional[UUID] = None
    preferences_override: Optional[Dict[str, Any]] = None


class SessionParticipantCreate(BaseModel):
    """Schema for adding a participant to a session."""

    location_id: Optional[UUID] = None
    preferences_override: Optional[Dict[str, Any]] = None


class SessionParticipant(SessionParticipantBase):
    """Schema for session participant response."""

    session_id: UUID
    joined_at: datetime

    class Config:
        from_attributes = True


class PlanningSessionBase(BaseModel):
    """Base schema for planning session."""

    name: str
    target_date: Optional[date] = None


class PlanningSessionCreate(PlanningSessionBase):
    """Schema for creating a planning session."""

    participant_emails: List[EmailStr] = []


class PlanningSession(PlanningSessionBase):
    """Schema for planning session response."""

    id: UUID
    created_by: UUID
    invite_code: str
    status: str
    merged_constraints: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    last_activity: datetime

    class Config:
        from_attributes = True


class PlanningSessionWithDetails(PlanningSession):
    """Schema for planning session with participants and venues."""

    participants: List[SessionParticipant] = []
    # suggested_venues will be populated separately
    # votes will be populated separately

    class Config:
        from_attributes = True


class SessionJoinRequest(BaseModel):
    """Schema for joining a session."""

    invite_code: str
    location_id: Optional[UUID] = None
    preferences: Optional[ParticipantPreferences] = None


class VenueVoteBase(BaseModel):
    """Base schema for venue vote."""

    venue_id: UUID
    vote: int  # -1 (veto), 0 (neutral), 1 (like), 2 (love)
    comment: Optional[str] = None


class VenueVoteCreate(VenueVoteBase):
    """Schema for creating a vote."""

    pass


class VenueVote(VenueVoteBase):
    """Schema for vote response."""

    session_id: UUID
    user_id: UUID
    voted_at: datetime

    class Config:
        from_attributes = True


class SessionVenueBase(BaseModel):
    """Base schema for session venue suggestion."""

    venue_id: UUID


class SessionVenueCreate(SessionVenueBase):
    """Schema for suggesting a venue."""

    pass


class SessionVenue(SessionVenueBase):
    """Schema for session venue response."""

    id: UUID
    session_id: UUID
    suggested_by: UUID
    suggested_at: datetime

    class Config:
        from_attributes = True


class VenueWithVotes(BaseModel):
    """Venue with voting information."""

    venue_id: UUID
    venue_name: str
    votes: List[VenueVote] = []
    vote_summary: Dict[str, int] = {}  # {"love": 2, "like": 1, "neutral": 0, "veto": 0}
    avg_score: float = 0.0

    class Config:
        from_attributes = True


class WebSocketMessage(BaseModel):
    """WebSocket message format."""

    type: str  # vote, suggest_venue, comment, cursor_move, user_joined, user_left
    user_id: Optional[UUID] = None
    venue_id: Optional[UUID] = None
    vote: Optional[int] = None
    comment: Optional[str] = None
    position: Optional[Dict[str, float]] = None
    timestamp: Optional[datetime] = None
    data: Optional[Dict[str, Any]] = None
