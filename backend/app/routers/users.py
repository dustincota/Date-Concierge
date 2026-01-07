"""
User endpoints for registration, login, and profile management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.models.user import User, UserLocation, UserPreferences
from app.schemas.user import (
    User as UserSchema,
    UserCreate,
    UserLogin,
    UserWithDetails,
    UserLocationCreate,
    UserPreferencesCreate,
    Token,
)
from app.services.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
)
from app.config import settings

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        Access token

    Raises:
        HTTPException: If email already registered
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=hashed_password,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id)}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password.

    Args:
        credentials: Login credentials
        db: Database session

    Returns:
        Access token

    Raises:
        HTTPException: If credentials invalid
    """
    user = authenticate_user(db, credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserWithDetails)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user profile with locations and preferences.

    Args:
        current_user: Current authenticated user

    Returns:
        User profile with details
    """
    return current_user


@router.post("/me/locations", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def add_user_location(
    location_data: UserLocationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add a location for the current user.

    Args:
        location_data: Location data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated user
    """
    # If this is set as default, unset other defaults
    if location_data.is_default:
        db.query(UserLocation).filter(
            UserLocation.user_id == current_user.id, UserLocation.is_default == True
        ).update({"is_default": False})

    db_location = UserLocation(
        user_id=current_user.id,
        **location_data.model_dump(),
    )

    db.add(db_location)
    db.commit()
    db.refresh(current_user)

    return current_user


@router.put("/me/preferences", response_model=UserSchema)
def update_user_preferences(
    preferences_data: UserPreferencesCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update user preferences.

    Args:
        preferences_data: Preferences data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated user
    """
    # Check if preferences exist
    existing_prefs = db.query(UserPreferences).filter(
        UserPreferences.user_id == current_user.id
    ).first()

    if existing_prefs:
        # Update existing
        for key, value in preferences_data.model_dump(exclude_unset=True).items():
            setattr(existing_prefs, key, value)
    else:
        # Create new
        db_prefs = UserPreferences(
            user_id=current_user.id,
            **preferences_data.model_dump(),
        )
        db.add(db_prefs)

    db.commit()
    db.refresh(current_user)

    return current_user
