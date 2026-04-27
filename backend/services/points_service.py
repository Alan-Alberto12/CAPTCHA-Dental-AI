from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date

from models.user import PointTransaction, UserStats, DailySessionCount, AnnotationSession, Annotation


class PointsService:

    SESSION_COMPLETE = 100
    FIRST_SESSION_TODAY = 50
    THOUGHTFUL_CONSIDERATION = 25
    NO_SKIPS = 50

    STREAK_BONUSES = {2: 20, 3: 30, 7: 100, 30: 500}
    VOLUME_BONUSES = {3: 75, 5: 150, 10: 300}

    def award_session_points(self, db: Session, user_id: int, session_id: int) -> dict:
        awarded = []
        total = 0

        def give(points, reason):
            nonlocal total
            total += self._log(db, user_id, session_id, points, reason)
            awarded.append({"reason": reason, "points": points})

        give(self.SESSION_COMPLETE, "session_complete")

        today_count = self._get_today_session_count(db, user_id)
        if today_count == 1:
            give(self.FIRST_SESSION_TODAY, "first_session_today")

        streak_service.update_streak(db, user_id)

        for threshold, bonus in sorted(self.VOLUME_BONUSES.items()):
            if today_count == threshold:
                give(bonus, f"volume_{threshold}_sessions")

        streak = self._get_streak(db, user_id)
        if streak in self.STREAK_BONUSES:
            give(self.STREAK_BONUSES[streak], f"streak_{streak}_days")

        if self._check_thoughtful(db, session_id):
            give(self.THOUGHTFUL_CONSIDERATION, "thoughtful_consideration")

        if self._check_no_skips(db, session_id):
            give(self.NO_SKIPS, "no_skips")

        self._update_user_stats(db, user_id, total)
        db.commit()

        return {"total_awarded": total, "breakdown": awarded}

    def _log(self, db: Session, user_id: int, session_id: int, points: int, reason: str) -> int:
        db.add(PointTransaction(user_id=user_id, session_id=session_id, points=points, reason=reason))
        return points

    def _get_today_session_count(self, db: Session, user_id: int) -> int:
        today = datetime.now(timezone.utc).date()
        record = (
            db.query(DailySessionCount)
            .filter(DailySessionCount.user_id == user_id, cast(DailySessionCount.date, Date) == today)
            .first()
        )
        if record is None:
            record = DailySessionCount(user_id=user_id, date=datetime.now(timezone.utc), session_count=1)
            db.add(record)
        else:
            record.session_count += 1
        return record.session_count

    def _get_streak(self, db: Session, user_id: int) -> int:
        stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
        return stats.daily_streak if stats else 0

    def _check_thoughtful(self, db: Session, session_id: int) -> bool:
        avg = db.query(func.avg(Annotation.time_spent)).filter(Annotation.session_id == session_id).scalar()
        return avg is not None and avg >= 30.0

    def _check_no_skips(self, db: Session, session_id: int) -> bool:
        return (
            db.query(Annotation)
            .filter(Annotation.session_id == session_id, Annotation.time_spent == None)
            .count() == 0
        )

    def _update_user_stats(self, db: Session, user_id: int, points_to_add: int):
        stats = db.query(UserStats).filter(UserStats.user_id == user_id).first()
        if stats is None:
            db.add(UserStats(user_id=user_id, total_points=points_to_add))
        else:
            stats.total_points += points_to_add


points_service = PointsService()