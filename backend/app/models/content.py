from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Course(Base):
    __tablename__ = "db_application_courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("db_application_users.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    difficulty_level: Mapped[str | None] = mapped_column(String(30))
    publish_status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    creator: Mapped["User"] = relationship(back_populates="courses")
    modules: Mapped[list["Module"]] = relationship(back_populates="course", cascade="all, delete-orphan", order_by="Module.order_index")


class Module(Base):
    __tablename__ = "db_application_modules"
    __table_args__ = (UniqueConstraint("course_id", "order_index", name="uq_module_course_order"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("db_application_courses.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    course: Mapped[Course] = relationship(back_populates="modules")
    lessons: Mapped[list["Lesson"]] = relationship(back_populates="module", cascade="all, delete-orphan", order_by="Lesson.order_index")


class Lesson(Base):
    __tablename__ = "db_application_lessons"
    __table_args__ = (UniqueConstraint("module_id", "order_index", name="uq_lesson_module_order"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("db_application_modules.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    module: Mapped[Module] = relationship(back_populates="lessons")
    tasks: Mapped[list["Task"]] = relationship(back_populates="lesson", cascade="all, delete-orphan", order_by="Task.order_index")
    progress_items: Mapped[list["Progress"]] = relationship(back_populates="lesson")


class Task(Base):
    __tablename__ = "db_application_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("db_application_lessons.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    statement: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[str | None] = mapped_column(String(30))
    starter_code: Mapped[str | None] = mapped_column(Text)
    time_limit_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=5000)
    memory_limit_mb: Mapped[int] = mapped_column(Integer, nullable=False, default=128)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    lesson: Mapped[Lesson] = relationship(back_populates="tasks")
    test_cases: Mapped[list["TestCase"]] = relationship(back_populates="task", cascade="all, delete-orphan", order_by="TestCase.order_index")
    submissions: Mapped[list["Submission"]] = relationship(back_populates="task")


class TestCase(Base):
    __tablename__ = "db_application_test_cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("db_application_tasks.id", ondelete="CASCADE"), nullable=False)
    input_data: Mapped[str | None] = mapped_column(Text)
    expected_output: Mapped[str | None] = mapped_column(Text)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    task: Mapped[Task] = relationship(back_populates="test_cases")
