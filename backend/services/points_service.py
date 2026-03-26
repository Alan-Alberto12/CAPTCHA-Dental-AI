"""
PointsService — handles all point calculations and awards.
Called whenever a session is completed.
"""

from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date

from models.user import PointTransaction, UserStats, DailySessionCount, AnnotationSession, Annotation


class PointsService:

    # --- Point values (matches the spec exactly) ---
    SESSION_COMPLETE = 100
    FIRST_SESSION_TODAY = 50
    THOUGHTFUL_CONSIDERATION = 25  # avg 30s+ per image
    NO_SKIPS = 50

    STREAK_BONUSES = {
        2: 20,
        3: 30,
        7: 100,
        30: 500,
    }

    VOLUME_BONUSES = {
        3: 75,
        5: 150,
        10: 300,
    }

    def award_session_points(self, db: Session, user_id: int, session_id: int) -> dict:
        """
        Main entry point — call this when a session is completed.
        Calculates all applicable points and updates the database.

        Returns a dict summarizing what was awarded.
        """
        awarded = []
        total = 0

        # 1. Base session completion points
        total += self._log(db, user_id, session_id, self.SESSION_COMPLETE, "session_complete")
        awarded.append({"reason": "session_complete", "points": self.SESSION_COMPLETE})

        # 2. First session of the day bonus
        today_count = self._get_today_session_count(db, user_id)
        if today_count == 1:
            # This is the first session today
            total += self._log(db, user_id, session_id, self.FIRST_SESSION_TODAY, "first_session_today")
            awarded.append({"reason": "first_session_today", "points": self.FIRST_SESSION_TODAY})

        # Update streak before checking streak bonus
        streak_service.update_streak(db, user_id)

        # 3. Volume bonuses (3, 5, 10 sessions in a day)
        # Only award at exact thresholds to avoid double-awarding
        for threshold, bonus in sorted(self.VOLUME_BONUSES.items()):
            if today_count == threshold:
                total += self._log(db, user_id, session_id, bonus, f"volume_{threshold}")
                awarded.append({"reason": f"volume_{threshold}_sessions", "points": bonus})

        # 4. Streak bonus
        streak = self._get_streak(db, user_id)
        if streak in self.STREAK_BONUSES:
            bonus = self.STREAK_BONUSES[streak]
            total += self._log(db, user_id, session_id, bonus, f"streak_{streak}")
            awarded.append({"reason": f"streak_{streak}_days", "points": bonus})

        # 5. Thoughtful consideration (avg 30s+ per image)
        if self._check_thoughtful(db, session_id):
            total += self._log(db, user_id, session_id, self.THOUGHTFUL_CONSIDERATION, "thoughtful")
            awarded.append({"reason": "thoughtful_consideration", "points": self.THOUGHTFUL_CONSIDERATION})

        # 6. No skips bonus
        if self._check_no_skips(db, session_id):
            total += self._log(db, user_id, session_id, self.NO_SKIPS, "no_skips")
            awarded.append({"reason": "no_skips", "points": self.NO_SKIPS})

        # 7. Update total points in UserStats
        self._update_user_stats(db, user_id, total)

        db.commit()

        return {"total_awarded": total, "breakdown": awarded}

    # --- Private helpers ---

    def _log(self, db: Session, user_id: int, session_id: int, points: int, reason: str) -> int:
        """Insert a row into point_transactions and return the points value."""
        tx = PointTransaction(
            user_id=user_id,
            session_id=session_id,
            points=points,
            reason=reason,
        )
        db.add(tx)
        return points

    def _get_today_session_count(self, db: Session, user_id: int) -> int:
        """Returns how many sessions the user has completed today."""
        today = datetime.now(timezone.utc).date()
        record = (
            db.query(DailySessionCount)
            .filter(
                DailySessionCount.user_id == user_id,
                cast(DailySessionCount.date, Date) == today,
            )
            .first()
        )
        if record is None:
            # First session today — create the record
            record = DailySessionCount(user_id=user_id, date=datetime.now(timezone.utc), session_count=1)
            db.add(record)
        else:
            record.session_count += 1
        return record.session_count

    def _get_streak(self, db: Session, user_id: int) -> int:
        """Returns the user's current daily streak from UserStats."""
        stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
        if stats is None:
            return 0
        return stats.daily_streak

    def _check_thoughtful(self, db: Session, session_id: int) -> bool:
        """
        Returns True if the average time_spent per annotation in this session is >= 30 seconds.
        """
        result = (
            db.query(func.avg(Annotation.time_spent))
            .filter(Annotation.session_id == session_id)
            .scalar()
        )
        return result is not None and result >= 30.0

    def _check_no_skips(self, db: Session, session_id: int) -> bool:
        """
        Returns True if no annotations in this session have null time_spent.
        (null time_spent = user skipped that image)
        """
        skipped = (
            db.query(Annotation)
            .filter(
                Annotation.session_id == session_id,
                Annotation.time_spent == None,
            )
            .count()
        )
        return skipped == 0

    def _update_user_stats(self, db: Session, user_id: int, points_to_add: int):
        """Adds points to the user's total in UserStats. Creates the row if it doesn't exist."""
        stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
        if stats is None:
            stats = UserStats(user_id=user_id, total_points=points_to_add)
            db.add(stats)
        else:
            stats.total_points += points_to_add


# Single instance reused across requests
points_service = PointsService()