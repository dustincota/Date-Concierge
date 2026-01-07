"""
User schemas for request/response validation.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class UserLocationBase(BaseModel):
    """Base schema for user location."""

    label: Optional[str] = None
    address: Optional[str] = None
    latitude: float
    longitude: float
    neighborhood: Optional[str] = None
    is_default: bool = False


class UserLocationCreate(UserLocationBase):
    """Schema for creating a user location."""

    pass


class UserLocation(UserLocationBase):
    """Schema for user location response."""

    id: UUID
    user_id: UUID

    class Config:
        from_attributes = True


class UserPreferencesBase(BaseModel):
    """Base schema for user preferences."""

    default_budget_min: Optional[int] = None
    default_budget_max: Optional[int] = None
    cuisines_loved: List[str] = []
    cuisines_avoid: List[str] = []
    dietary_restrictions: List[str] = []
    vibes: List[str] = []


class UserPreferencesCreate(UserPreferencesBase):
    """Schema for creating user preferences."""

    pass


class UserPreferences(UserPreferencesBase):
    """Schema for user preferences response."""

    user_id: UUID
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    """Base schema for user."""

    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class User(UserBase):
    """Schema for user response."""

    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class UserWithDetails(User):
    """Schema for user with locations and preferences."""

    locations: List[UserLocation] = []
    preferences: Optional[UserPreferences] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for authentication token."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data."""

    user_id: Optional[UUID] = None
