"""
WebSocket endpoint for real-time collaboration.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, List
import json
from datetime import datetime
from uuid import UUID

from app.database import get_db
from app.models.session import PlanningSession, SessionParticipant
from app.models.user import User

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for planning sessions."""

    def __init__(self):
        # session_id -> list of (websocket, user_id) tuples
        self.active_connections: Dict[str, List[tuple]] = {}

    async def connect(self, websocket: WebSocket, session_id: str, user_id: str):
        """Connect a user to a session."""
        await websocket.accept()

        if session_id not in self.active_connections:
            self.active_connections[session_id] = []

        self.active_connections[session_id].append((websocket, user_id))

        # Notify others that user joined
        await self.broadcast(
            session_id,
            {
                "type": "user_joined",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
            },
            exclude_user=user_id,
        )

    async def disconnect(self, websocket: WebSocket, session_id: str, user_id: str):
        """Disconnect a user from a session."""
        if session_id in self.active_connections:
            self.active_connections[session_id] = [
                (ws, uid)
                for ws, uid in self.active_connections[session_id]
                if ws != websocket
            ]

            # Notify others that user left
            await self.broadcast(
                session_id,
                {
                    "type": "user_left",
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

    async def broadcast(
        self,
        session_id: str,
        message: dict,
        exclude_user: str = None,
    ):
        """Send message to all users in a session."""
        if session_id not in self.active_connections:
            return

        message_str = json.dumps(message)

        for websocket, user_id in self.active_connections[session_id]:
            if exclude_user and user_id == exclude_user:
                continue

            try:
                await websocket.send_text(message_str)
            except Exception as e:
                print(f"Error sending to {user_id}: {e}")

    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message to a specific user."""
        await websocket.send_json(message)

    def get_active_users(self, session_id: str) -> List[str]:
        """Get list of active user IDs in a session."""
        if session_id not in self.active_connections:
            return []

        return [user_id for _, user_id in self.active_connections[session_id]]


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/session/{session_id}")
async def session_websocket(
    websocket: WebSocket,
    session_id: str,
    token: str,
):
    """
    WebSocket endpoint for real-time session collaboration.

    Query params:
        token: JWT authentication token

    Messages:
        - type: vote
          venue_id: str
          vote: int (-1, 0, 1, 2)
          comment: str (optional)

        - type: suggest_venue
          venue_id: str

        - type: comment
          venue_id: str
          comment: str

        - type: cursor_move (optional fun feature)
          position: {x: float, y: float}
    """
    from app.services.auth import decode_access_token

    # Authenticate user from token
    try:
        token_data = decode_access_token(token)
        user_id = str(token_data.user_id)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Verify user is participant in session
    # Note: We'd normally use Depends(get_db) but WebSocket doesn't support it the same way
    # So we create a db session manually
    from app.database import SessionLocal

    db = SessionLocal()

    try:
        participant = (
            db.query(SessionParticipant)
            .filter(
                SessionParticipant.session_id == session_id,
                SessionParticipant.user_id == user_id,
            )
            .first()
        )

        if not participant:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Connect user
        await manager.connect(websocket, session_id, user_id)

        # Send current active users list
        active_users = manager.get_active_users(session_id)
        await manager.send_personal(
            websocket,
            {
                "type": "active_users",
                "users": active_users,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        # Listen for messages
        try:
            while True:
                data_str = await websocket.receive_text()
                data = json.loads(data_str)

                # Handle different message types
                message_type = data.get("type")

                if message_type == "vote":
                    # Broadcast vote to all participants
                    await manager.broadcast(
                        session_id,
                        {
                            "type": "vote_update",
                            "user_id": user_id,
                            "venue_id": data.get("venue_id"),
                            "vote": data.get("vote"),
                            "comment": data.get("comment"),
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    )

                elif message_type == "suggest_venue":
                    # Broadcast new venue suggestion
                    await manager.broadcast(
                        session_id,
                        {
                            "type": "new_suggestion",
                            "user_id": user_id,
                            "venue_id": data.get("venue_id"),
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    )

                elif message_type == "comment":
                    # Broadcast comment
                    await manager.broadcast(
                        session_id,
                        {
                            "type": "new_comment",
                            "user_id": user_id,
                            "venue_id": data.get("venue_id"),
                            "comment": data.get("comment"),
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    )

                elif message_type == "cursor_move":
                    # Broadcast cursor position (optional fun feature)
                    await manager.broadcast(
                        session_id,
                        {
                            "type": "cursor_update",
                            "user_id": user_id,
                            "position": data.get("position"),
                        },
                        exclude_user=user_id,  # Don't send back to sender
                    )

                elif message_type == "typing":
                    # Broadcast typing indicator
                    await manager.broadcast(
                        session_id,
                        {
                            "type": "user_typing",
                            "user_id": user_id,
                            "venue_id": data.get("venue_id"),
                        },
                        exclude_user=user_id,
                    )

        except WebSocketDisconnect:
            await manager.disconnect(websocket, session_id, user_id)

        except Exception as e:
            print(f"WebSocket error: {e}")
            await manager.disconnect(websocket, session_id, user_id)

    finally:
        db.close()
