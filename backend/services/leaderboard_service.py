from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date

from models.user import User, UserStats, DailySessionCount, AnnotationSession, PointTransaction

TOP_N = 10


def _rank(rows, extra):
    # adds rank, user_id, username to each row using a custom extra fields function
    return [{"rank": i + 1, "user_id": r.id, "username": r.username, **extra(r)} for i, r in enumerate(rows)]


class LeaderboardService:

    def get_all(self, db: Session) -> dict:
        return {
            "daily_contributors": self.get_daily_contributors(db),
            "longest_streak": self.get_longest_streak(db),
            "lifetime_points": self.get_lifetime_points(db),
            "weekly_mvp": self.get_weekly_mvp(db),
            "most_consistent": self.get_most_consistent(db),
        }

    def get_daily_contributors(self, db: Session) -> list:
        today = datetime.now(timezone.utc).date()
        rows = (
            db.query(User.id, User.username, DailySessionCount.session_count)
            .join(DailySessionCount, DailySessionCount.user_id == User.id)
            .filter(cast(DailySessionCount.date, Date) == today)
            .order_by(DailySessionCount.session_count.desc())
            .limit(TOP_N).all()
        )
        return _rank(rows, lambda r: {"sessions_today": r.session_count})

    def get_longest_streak(self, db: Session) -> list:
        rows = (
            db.query(User.id, User.username, UserStats.daily_streak)
            .join(UserStats, UserStats.user_id == User.id)
            .order_by(UserStats.daily_streak.desc())
            .limit(TOP_N).all()
        )
        return _rank(rows, lambda r: {"streak_days": r.daily_streak})

    def get_lifetime_points(self, db: Session) -> list:
        rows = (
            db.query(User.id, User.username, UserStats.total_points)
            .join(UserStats, UserStats.user_id == User.id)
            .order_by(UserStats.total_points.desc())
            .limit(TOP_N).all()
        )
        return _rank(rows, lambda r: {"total_points": r.total_points})

    def get_weekly_mvp(self, db: Session) -> list:
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        rows = (
            db.query(User.id, User.username, func.sum(PointTransaction.points).label("weekly_points"))
            .join(PointTransaction, PointTransaction.user_id == User.id)
            .filter(PointTransaction.created_at >= week_ago)
            .group_by(User.id, User.username)
            .order_by(func.sum(PointTransaction.points).desc())
            .limit(TOP_N).all()
        )
        return _rank(rows, lambda r: {"weekly_points": r.weekly_points})

    def get_most_consistent(self, db: Session) -> list:
        total = func.sum(DailySessionCount.session_count)
        days = func.count(DailySessionCount.id)
        rows = (
            db.query(User.id, User.username, total.label("total_sessions"), days.label("active_days"), (total / days).label("avg_sessions"))
            .join(DailySessionCount, DailySessionCount.user_id == User.id)
            .group_by(User.id, User.username)
            .order_by((total / days).desc())
            .limit(TOP_N).all()
        )
        return _rank(rows, lambda r: {"avg_sessions_per_day": round(float(r.avg_sessions), 2), "active_days": r.active_days})


leaderboard_service = LeaderboardService()