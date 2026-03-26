"""
StreakService — updates a user's daily streak when they complete a session.

Logic:
- If user was active yesterday → increment streak
- If user was active today already → streak unchanged (don't double count)
- If user missed a day → reset streak to 1
"""

from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import cast, Date, func

from models.user import UserStats, DailySessionCount


class StreakService:

    def update_streak(self, db: Session, user_id: int) -> int:
        """
        Call this when a session is completed.
        Updates the user's daily_streak in UserStats.
        Returns the new streak value.
        """
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)

        stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()

        if stats is None:
            # First ever session — create stats row with streak of 1
            stats = UserStats(user_id=user_id, daily_streak=1, last_active=datetime.now(timezone.utc))
            db.add(stats)
            db.flush()
            return 1

        last_active_date = stats.last_active.date() if stats.last_active else None

        if last_active_date == today:
            # Already completed a session today — streak unchanged
            return stats.daily_streak

        elif last_active_date == yesterday:
            # Active yesterday — extend the streak
            stats.daily_streak += 1

        else:
            # Missed at least one day — reset streak to 1
            stats.daily_streak = 1

        # Update last_active to now
        stats.last_active = datetime.now(timezone.utc)

        return stats.daily_streak


# Single instance reused across requests
streak_service = StreakService()