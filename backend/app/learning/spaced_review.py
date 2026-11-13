"""A deterministic, conservative schedule, separate from mastery percentages."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass
class ReviewSchedule:
    consecutive_correct: int = 0
    interval_days: int = 0
    last_review_at: str | None = None
    next_review_at: str | None = None

    def record(self, correct: bool, now: datetime | None = None) -> None:
        now = now or datetime.now(timezone.utc)
        intervals = (1, 3, 7, 14, 30, 60)
        self.consecutive_correct = self.consecutive_correct + 1 if correct else 0
        self.interval_days = intervals[min(self.consecutive_correct, len(intervals)) - 1] if correct else 0
        self.last_review_at = now.isoformat()
        self.next_review_at = (now + (timedelta(days=self.interval_days) if correct else timedelta(minutes=10))).isoformat()

    def due(self, now: datetime | None = None) -> bool:
        return self.next_review_at is None or datetime.fromisoformat(self.next_review_at) <= (now or datetime.now(timezone.utc))
