from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Submission(Base):
    __tablename__ = "db_application_submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("db_application_users.id"), nullable=False)
    task_id: Mapped[int] = mapped_column(ForeignKey("db_application_tasks.id"), nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    passed_tests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    execution_time_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    user: Mapped["User"] = relationship(back_populates="submissions")
    task: Mapped["Task"] = relationship(back_populates="submissions")
