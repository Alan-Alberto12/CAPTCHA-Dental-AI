"""
Leaderboard routes — exposes leaderboard and points endpoints.

Endpoints:
    GET  /leaderboard              — all 5 leaderboard categories
    GET  /leaderboard/me           — current user's points + streak
    POST /leaderboard/session/complete/{session_id} — award points for a completed session
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from services.database import get_db
from services.points_service import points_service
from services.leaderboard_service import leaderboard_service
from models.user import UserStats, AnnotationSession
from api.routes.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("")
def get_leaderboard(db: Session = Depends(get_db)):
    """
    Returns all 5 leaderboard categories.
    Each category has top 10 users ranked by different criteria.
    
    No auth required — leaderboard is public.
    """
    return leaderboard_service.get_all(db)


@router.get("/me")
def get_my_points(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns the current user's total points and daily streak.
    Requires auth — user must be logged in.
    """
    stats = db.query(UserStats).filter(UserStats.user_id == current_user.id).first()

    if stats is None:
        # User hasn't completed any sessions yet
        return {
            "user_id": current_user.id,
            "username": current_user.username,
            "total_points": 0,
            "daily_streak": 0,
        }

    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "total_points": stats.total_points,
        "daily_streak": stats.daily_streak,
    }


@router.post("/session/complete/{session_id}")
def complete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Awards points for a completed session.
    Call this from the frontend when a user finishes a session.
    
    Returns a breakdown of all points awarded.
    """
    # Verify the session exists and belongs to this user
    session = db.query(AnnotationSession).filter(
        AnnotationSession.id == session_id,
        AnnotationSession.user_id == current_user.id,
    ).first()

    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    if not session.is_completed:
        raise HTTPException(status_code=400, detail="Session is not completed yet")

    # Check if points were already awarded for this session
    from models.user import PointTransaction
    already_awarded = db.query(PointTransaction).filter(
        PointTransaction.session_id == session_id,
        PointTransaction.reason == "session_complete",
    ).first()

    if already_awarded:
        raise HTTPException(status_code=400, detail="Points already awarded for this session")

    # Award all applicable points
    result = points_service.award_session_points(db, current_user.id, session_id)

    return {
        "message": "Points awarded successfully",
        "session_id": session_id,
        "total_awarded": result["total_awarded"],
        "breakdown": result["breakdown"],
    }