from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, SmallInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Progress(Base):
    __tablename__ = "db_application_progress"
    __table_args__ = (UniqueConstraint("user_id", "lesson_id", name="uq_progress_user_lesson"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("db_application_users.id"), nullable=False)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("db_application_lessons.id"), nullable=False)
    completion_percent: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="progress_items")
    lesson: Mapped["Lesson"] = relationship(back_populates="progress_items")
