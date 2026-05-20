from datetime import datetime

from pydantic import BaseModel


class ProgressRead(BaseModel):
    id: int
    lesson_id: int
    completion_percent: int
    last_activity_at: datetime
    completed_at: datetime | None = None
    lesson_title: str | None = None
    course_title: str | None = None


class CourseProgressRead(BaseModel):
    course_id: int
    completion_percent: int
    lessons: list[ProgressRead]
