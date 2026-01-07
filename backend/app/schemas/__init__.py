"""
Pydantic schemas for request/response validation.
"""

from app.schemas.user import (
    User,
    UserCreate,
    UserLogin,
    UserWithDetails,
    UserLocation,
    UserLocationCreate,
    UserPreferences,
    UserPreferencesCreate,
    Token,
    TokenData,
)
from app.schemas.venue import (
    Venue,
    VenueCreate,
    VenueWithIntelligence,
    VenueIntelligence,
    SeatingRecommendation,
    DishRecommendation,
    TimingInsight,
    CommuteInsight,
    VibeCheck,
    InsiderTip,
    IntelligenceJobStatus,
)
from app.schemas.session import (
    PlanningSession,
    PlanningSessionCreate,
    PlanningSessionWithDetails,
    SessionParticipant,
    SessionParticipantCreate,
    SessionJoinRequest,
    VenueVote,
    VenueVoteCreate,
    SessionVenue,
    SessionVenueCreate,
    VenueWithVotes,
    WebSocketMessage,
)
from app.schemas.itinerary import (
    Itinerary,
    ItineraryCreate,
    ItineraryWithStops,
    ItineraryStop,
    ItineraryStopCreate,
    Reservation,
    ReservationCreate,
)

__all__ = [
    # User schemas
    "User",
    "UserCreate",
    "UserLogin",
    "UserWithDetails",
    "UserLocation",
    "UserLocationCreate",
    "UserPreferences",
    "UserPreferencesCreate",
    "Token",
    "TokenData",
    # Venue schemas
    "Venue",
    "VenueCreate",
    "VenueWithIntelligence",
    "VenueIntelligence",
    "SeatingRecommendation",
    "DishRecommendation",
    "TimingInsight",
    "CommuteInsight",
    "VibeCheck",
    "InsiderTip",
    "IntelligenceJobStatus",
    # Session schemas
    "PlanningSession",
    "PlanningSessionCreate",
    "PlanningSessionWithDetails",
    "SessionParticipant",
    "SessionParticipantCreate",
    "SessionJoinRequest",
    "VenueVote",
    "VenueVoteCreate",
    "SessionVenue",
    "SessionVenueCreate",
    "VenueWithVotes",
    "WebSocketMessage",
    # Itinerary schemas
    "Itinerary",
    "ItineraryCreate",
    "ItineraryWithStops",
    "ItineraryStop",
    "ItineraryStopCreate",
    "Reservation",
    "ReservationCreate",
]
