"""
Itinerary schemas for date planning.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, date, time
from uuid import UUID


class ReservationBase(BaseModel):
    """Base schema for reservation."""

    venue_id: UUID
    date: date
    time: time
    party_size: int
    platform: Optional[str] = None


class ReservationCreate(ReservationBase):
    """Schema for creating a reservation."""

    pass


class Reservation(ReservationBase):
    """Schema for reservation response."""

    id: UUID
    itinerary_stop_id: Optional[UUID] = None
    confirmation_number: Optional[str] = None
    status: str
    booking_link: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ItineraryStopBase(BaseModel):
    """Base schema for itinerary stop."""

    venue_id: UUID
    stop_order: int
    arrival_time: Optional[time] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    seating_request: Optional[str] = None
    order_recommendations: List[str] = []


class ItineraryStopCreate(ItineraryStopBase):
    """Schema for creating an itinerary stop."""

    backup_venue_id: Optional[UUID] = None


class ItineraryStop(ItineraryStopBase):
    """Schema for itinerary stop response."""

    id: UUID
    itinerary_id: UUID
    backup_venue_id: Optional[UUID] = None
    travel_from_previous: Optional[Dict[str, Any]] = None
    reservation: Optional[Reservation] = None

    class Config:
        from_attributes = True


class ItineraryBase(BaseModel):
    """Base schema for itinerary."""

    title: str
    date: date


class ItineraryCreate(ItineraryBase):
    """Schema for creating an itinerary."""

    session_id: UUID
    stops: List[ItineraryStopCreate] = []


class Itinerary(ItineraryBase):
    """Schema for itinerary response."""

    id: UUID
    session_id: Optional[UUID] = None
    weather_data: Optional[Dict[str, Any]] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ItineraryWithStops(Itinerary):
    """Schema for itinerary with stops."""

    stops: List[ItineraryStop] = []

    class Config:
        from_attributes = True
