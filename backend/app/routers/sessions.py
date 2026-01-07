"""
Session endpoints for collaborative planning.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import secrets
import string

from app.database import get_db
from app.models.user import User
from app.models.session import PlanningSession, SessionParticipant, SessionVenue, VenueVote
from app.models.venue import Venue
from app.schemas.session import (
    PlanningSession as PlanningSessionSchema,
    PlanningSessionCreate,
    PlanningSessionWithDetails,
    SessionJoinRequest,
    VenueVoteCreate,
    VenueVote as VenueVoteSchema,
    SessionVenueCreate,
    VenueWithVotes,
)
from app.services.auth import get_current_user
from app.services.location_optimizer import LocationOptimizer

router = APIRouter()


def generate_invite_code(length: int = 8) -> str:
    """Generate a random invite code."""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


@router.post("", response_model=PlanningSessionSchema, status_code=status.HTTP_201_CREATED)
def create_session(
    session_data: PlanningSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new planning session.

    Args:
        session_data: Session creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created planning session
    """
    # Generate unique invite code
    invite_code = generate_invite_code()
    while db.query(PlanningSession).filter(PlanningSession.invite_code == invite_code).first():
        invite_code = generate_invite_code()

    # Create session
    db_session = PlanningSession(
        name=session_data.name,
        created_by=current_user.id,
        invite_code=invite_code,
        target_date=session_data.target_date,
        status="draft",
    )

    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    # Add creator as organizer
    organizer = SessionParticipant(
        session_id=db_session.id,
        user_id=current_user.id,
        role="organizer",
    )
    db.add(organizer)
    db.commit()

    return db_session


@router.get("/{session_id}", response_model=PlanningSessionWithDetails)
def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get session details.

    Args:
        session_id: Session ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Session with details

    Raises:
        HTTPException: If session not found or user not participant
    """
    db_session = db.query(PlanningSession).filter(PlanningSession.id == session_id).first()
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    # Check if user is participant
    participant = (
        db.query(SessionParticipant)
        .filter(
            SessionParticipant.session_id == session_id,
            SessionParticipant.user_id == current_user.id,
        )
        .first()
    )

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a participant in this session",
        )

    return db_session


@router.post("/join", response_model=PlanningSessionSchema)
def join_session(
    join_data: SessionJoinRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Join a session using invite code.

    Args:
        join_data: Join request with invite code
        current_user: Current authenticated user
        db: Database session

    Returns:
        Joined session

    Raises:
        HTTPException: If invite code invalid or already joined
    """
    # Find session by invite code
    db_session = (
        db.query(PlanningSession)
        .filter(PlanningSession.invite_code == join_data.invite_code)
        .first()
    )

    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invite code",
        )

    # Check if already participant
    existing = (
        db.query(SessionParticipant)
        .filter(
            SessionParticipant.session_id == db_session.id,
            SessionParticipant.user_id == current_user.id,
        )
        .first()
    )

    if existing:
        return db_session

    # Add as participant
    participant = SessionParticipant(
        session_id=db_session.id,
        user_id=current_user.id,
        role="participant",
        location_id=join_data.location_id,
        preferences_override=join_data.preferences.model_dump() if join_data.preferences else None,
    )

    db.add(participant)
    db.commit()

    # Update merged constraints
    participants = (
        db.query(SessionParticipant)
        .filter(SessionParticipant.session_id == db_session.id)
        .all()
    )
    merged = LocationOptimizer.merge_participant_preferences(participants, db)
    db_session.merged_constraints = merged
    db.commit()
    db.refresh(db_session)

    return db_session


@router.post("/{session_id}/venues", status_code=status.HTTP_201_CREATED)
def suggest_venue(
    session_id: str,
    venue_data: SessionVenueCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Suggest a venue for the session.

    Args:
        session_id: Session ID
        venue_data: Venue suggestion data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: If not participant or venue not found
    """
    # Verify participant
    participant = (
        db.query(SessionParticipant)
        .filter(
            SessionParticipant.session_id == session_id,
            SessionParticipant.user_id == current_user.id,
        )
        .first()
    )

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a participant in this session",
        )

    # Verify venue exists
    venue = db.query(Venue).filter(Venue.id == venue_data.venue_id).first()
    if not venue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Venue not found",
        )

    # Check if already suggested
    existing = (
        db.query(SessionVenue)
        .filter(
            SessionVenue.session_id == session_id,
            SessionVenue.venue_id == venue_data.venue_id,
        )
        .first()
    )

    if existing:
        return {"message": "Venue already suggested"}

    # Add suggestion
    suggestion = SessionVenue(
        session_id=session_id,
        venue_id=venue_data.venue_id,
        suggested_by=current_user.id,
    )

    db.add(suggestion)
    db.commit()

    return {"message": "Venue suggested successfully"}


@router.post("/{session_id}/votes", response_model=VenueVoteSchema, status_code=status.HTTP_201_CREATED)
def cast_vote(
    session_id: str,
    vote_data: VenueVoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cast or update vote on a venue.

    Args:
        session_id: Session ID
        vote_data: Vote data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created/updated vote

    Raises:
        HTTPException: If not participant
    """
    # Verify participant
    participant = (
        db.query(SessionParticipant)
        .filter(
            SessionParticipant.session_id == session_id,
            SessionParticipant.user_id == current_user.id,
        )
        .first()
    )

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a participant in this session",
        )

    # Validate vote value
    if vote_data.vote not in [-1, 0, 1, 2]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vote must be -1 (veto), 0 (neutral), 1 (like), or 2 (love)",
        )

    # Check for existing vote
    existing_vote = (
        db.query(VenueVote)
        .filter(
            VenueVote.session_id == session_id,
            VenueVote.venue_id == vote_data.venue_id,
            VenueVote.user_id == current_user.id,
        )
        .first()
    )

    if existing_vote:
        # Update existing vote
        existing_vote.vote = vote_data.vote
        existing_vote.comment = vote_data.comment
        db.commit()
        db.refresh(existing_vote)
        return existing_vote

    # Create new vote
    db_vote = VenueVote(
        session_id=session_id,
        venue_id=vote_data.venue_id,
        user_id=current_user.id,
        vote=vote_data.vote,
        comment=vote_data.comment,
    )

    db.add(db_vote)
    db.commit()
    db.refresh(db_vote)

    return db_vote


@router.get("/{session_id}/votes", response_model=List[VenueWithVotes])
def get_session_votes(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all votes for venues in the session.

    Args:
        session_id: Session ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of venues with vote information
    """
    # Verify participant
    participant = (
        db.query(SessionParticipant)
        .filter(
            SessionParticipant.session_id == session_id,
            SessionParticipant.user_id == current_user.id,
        )
        .first()
    )

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a participant in this session",
        )

    # Get all suggested venues
    suggestions = (
        db.query(SessionVenue)
        .filter(SessionVenue.session_id == session_id)
        .all()
    )

    results = []
    for suggestion in suggestions:
        venue = suggestion.venue

        # Get votes for this venue
        votes = (
            db.query(VenueVote)
            .filter(
                VenueVote.session_id == session_id,
                VenueVote.venue_id == venue.id,
            )
            .all()
        )

        # Calculate vote summary
        vote_summary = {"veto": 0, "neutral": 0, "like": 0, "love": 0}
        vote_sum = 0
        for vote in votes:
            vote_sum += vote.vote
            if vote.vote == -1:
                vote_summary["veto"] += 1
            elif vote.vote == 0:
                vote_summary["neutral"] += 1
            elif vote.vote == 1:
                vote_summary["like"] += 1
            elif vote.vote == 2:
                vote_summary["love"] += 1

        avg_score = vote_sum / len(votes) if votes else 0

        results.append(
            {
                "venue_id": venue.id,
                "venue_name": venue.name,
                "votes": votes,
                "vote_summary": vote_summary,
                "avg_score": avg_score,
            }
        )

    # Sort by average score (descending)
    results.sort(key=lambda x: x["avg_score"], reverse=True)

    return results


@router.get("/{session_id}/optimal-location")
async def get_optimal_location(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get optimal meeting point for all participants.

    Args:
        session_id: Session ID
        current_user: Current authenticated user
        db: Database session

    Returns:
        Optimal location coordinates and address
    """
    # Verify participant
    participant = (
        db.query(SessionParticipant)
        .filter(
            SessionParticipant.session_id == session_id,
            SessionParticipant.user_id == current_user.id,
        )
        .first()
    )

    if not participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a participant in this session",
        )

    # Get all participants
    participants = (
        db.query(SessionParticipant)
        .filter(SessionParticipant.session_id == session_id)
        .all()
    )

    # Get participant locations
    locations = LocationOptimizer.get_participant_locations(participants, db)

    if not locations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No participant locations available",
        )

    # Find optimal point
    optimal_point = LocationOptimizer.find_optimal_meeting_point(locations)

    # Reverse geocode to get address
    from app.services.geocoding import GeocodingService

    address_info = await GeocodingService.reverse_geocode(
        optimal_point[0], optimal_point[1]
    )

    return {
        "latitude": optimal_point[0],
        "longitude": optimal_point[1],
        "formatted_address": address_info.get("formatted_address") if address_info else None,
        "neighborhood": address_info.get("neighborhood") if address_info else None,
    }
