from datetime import datetime

from pydantic import BaseModel


class StatusCount(BaseModel):
    status: str
    count: int


class SubmissionActivity(BaseModel):
    id: int
    user_email: str
    username: str
    task_title: str
    course_title: str | None = None
    status: str
    score: int
    submitted_at: datetime


class CourseStats(BaseModel):
    course_id: int
    title: str
    publish_status: str
    modules_count: int
    lessons_count: int
    tasks_count: int
    submissions_count: int
    accepted_submissions_count: int
    active_students_count: int


class AdminStats(BaseModel):
    users_count: int
    students_count: int
    admins_count: int
    blocked_users_count: int
    courses_count: int
    published_courses_count: int
    lessons_count: int
    tasks_count: int
    test_cases_count: int
    submissions_count: int
    accepted_submissions_count: int
    average_score: int
    submissions_by_status: list[StatusCount]
    course_stats: list[CourseStats]
    recent_submissions: list[SubmissionActivity]


class StudentStats(BaseModel):
    lessons_started: int
    lessons_completed: int
    average_completion_percent: int
    submissions_count: int
    accepted_submissions_count: int
    solved_tasks_count: int
    average_score: int
    submissions_by_status: list[StatusCount]
    recent_submissions: list[SubmissionActivity]
