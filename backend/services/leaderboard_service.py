"""
LeaderboardService — queries and ranks users for all 5 leaderboard categories.
Called by the leaderboard API route.
"""

from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date

from models.user import User, UserStats, DailySessionCount, AnnotationSession, PointTransaction


class LeaderboardService:

    TOP_N = 10  # How many users to return per category

    def get_all(self, db: Session) -> dict:
        """
        Returns all 5 leaderboard categories in one call.
        This is what GET /leaderboard returns.
        """
        return {
            "daily_contributors": self.get_daily_contributors(db),
            "longest_streak": self.get_longest_streak(db),
            "lifetime_points": self.get_lifetime_points(db),
            "weekly_mvp": self.get_weekly_mvp(db),
            "most_consistent": self.get_most_consistent(db),
        }

    def get_daily_contributors(self, db: Session) -> list:
        """
        Top users by number of sessions completed today.
        """
        today = datetime.now(timezone.utc).date()

        results = (
            db.query(
                User.id,
                User.username,
                DailySessionCount.session_count,
            )
            .join(DailySessionCount, DailySessionCount.user_id == User.id)
            .filter(cast(DailySessionCount.date, Date) == today)
            .order_by(DailySessionCount.session_count.desc())
            .limit(self.TOP_N)
            .all()
        )

        return [
            {"rank": i + 1, "user_id": r.id, "username": r.username, "sessions_today": r.session_count}
            for i, r in enumerate(results)
        ]

    def get_longest_streak(self, db: Session) -> list:
        """
        Top users by current daily streak (consecutive days active).
        """
        results = (
            db.query(
                User.id,
                User.username,
                UserStats.daily_streak,
            )
            .join(UserStats, UserStats.user_id == User.id)
            .order_by(UserStats.daily_streak.desc())
            .limit(self.TOP_N)
            .all()
        )

        return [
            {"rank": i + 1, "user_id": r.id, "username": r.username, "streak_days": r.daily_streak}
            for i, r in enumerate(results)
        ]

    def get_lifetime_points(self, db: Session) -> list:
        """
        Top users by total lifetime points.
        """
        results = (
            db.query(
                User.id,
                User.username,
                UserStats.total_points,
            )
            .join(UserStats, UserStats.user_id == User.id)
            .order_by(UserStats.total_points.desc())
            .limit(self.TOP_N)
            .all()
        )

        return [
            {"rank": i + 1, "user_id": r.id, "username": r.username, "total_points": r.total_points}
            for i, r in enumerate(results)
        ]

    def get_weekly_mvp(self, db: Session) -> list:
        """
        Top users by points earned this week (last 7 days).
        """
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)

        results = (
            db.query(
                User.id,
                User.username,
                func.sum(PointTransaction.points).label("weekly_points"),
            )
            .join(PointTransaction, PointTransaction.user_id == User.id)
            .filter(PointTransaction.created_at >= week_ago)
            .group_by(User.id, User.username)
            .order_by(func.sum(PointTransaction.points).desc())
            .limit(self.TOP_N)
            .all()
        )

        return [
            {"rank": i + 1, "user_id": r.id, "username": r.username, "weekly_points": r.weekly_points}
            for i, r in enumerate(results)
        ]

    def get_most_consistent(self, db: Session) -> list:
        """
        Top users by average sessions per active day.
        (total sessions / number of days they've been active)
        """
        results = (
            db.query(
                User.id,
                User.username,
                func.sum(DailySessionCount.session_count).label("total_sessions"),
                func.count(DailySessionCount.id).label("active_days"),
                (
                    func.sum(DailySessionCount.session_count) /
                    func.count(DailySessionCount.id)
                ).label("avg_sessions"),
            )
            .join(DailySessionCount, DailySessionCount.user_id == User.id)
            .group_by(User.id, User.username)
            .order_by(
                (func.sum(DailySessionCount.session_count) / func.count(DailySessionCount.id)).desc()
            )
            .limit(self.TOP_N)
            .all()
        )

        return [
            {
                "rank": i + 1,
                "user_id": r.id,
                "username": r.username,
                "avg_sessions_per_day": round(float(r.avg_sessions), 2),
                "active_days": r.active_days,
            }
            for i, r in enumerate(results)
        ]


# Single instance reused across requests
leaderboard_service = LeaderboardService()