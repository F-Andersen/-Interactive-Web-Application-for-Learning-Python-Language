from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.content import Course, Lesson, Module, Task
from app.models.progress import Progress
from app.models.submission import Submission
from app.models.user import User
from app.schemas.progress import CourseProgressRead, ProgressRead
from app.schemas.stats import StatusCount, StudentStats, SubmissionActivity

router = APIRouter(prefix="/progress", tags=["progress"])


def serialize_progress(item: Progress) -> ProgressRead:
    return ProgressRead(
        id=item.id,
        lesson_id=item.lesson_id,
        completion_percent=item.completion_percent,
        last_activity_at=item.last_activity_at,
        completed_at=item.completed_at,
        lesson_title=item.lesson.title if item.lesson else None,
        course_title=item.lesson.module.course.title if item.lesson and item.lesson.module else None,
    )


def serialize_recent_submissions(db: Session, user_id: int, limit: int = 8) -> list[SubmissionActivity]:
    rows = (
        db.query(Submission, Task, Lesson, Module, Course)
        .join(Task, Task.id == Submission.task_id)
        .join(Lesson, Lesson.id == Task.lesson_id)
        .join(Module, Module.id == Lesson.module_id)
        .join(Course, Course.id == Module.course_id)
        .filter(Submission.user_id == user_id)
        .order_by(Submission.submitted_at.desc())
        .limit(limit)
        .all()
    )
    return [
        SubmissionActivity(
            id=submission.id,
            user_email="",
            username="",
            task_title=task.title,
            course_title=course.title,
            status=submission.status,
            score=submission.score,
            submitted_at=submission.submitted_at,
        )
        for submission, task, lesson, module, course in rows
    ]


@router.get("/me", response_model=list[ProgressRead])
def my_progress(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = db.query(Progress).filter(Progress.user_id == current_user.id).order_by(Progress.last_activity_at.desc()).all()
    return [serialize_progress(item) for item in items]


@router.get("/me/stats", response_model=StudentStats)
def my_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    progress_items = db.query(Progress).filter(Progress.user_id == current_user.id).all()
    submissions_count = db.query(func.count(Submission.id)).filter(Submission.user_id == current_user.id).scalar() or 0
    accepted_count = (
        db.query(func.count(Submission.id))
        .filter(Submission.user_id == current_user.id, Submission.status == "accepted")
        .scalar()
        or 0
    )
    solved_tasks = (
        db.query(func.count(func.distinct(Submission.task_id)))
        .filter(Submission.user_id == current_user.id, Submission.status == "accepted")
        .scalar()
        or 0
    )
    status_rows = (
        db.query(Submission.status, func.count(Submission.id))
        .filter(Submission.user_id == current_user.id)
        .group_by(Submission.status)
        .all()
    )
    average_score = (
        db.query(func.coalesce(func.avg(Submission.score), 0))
        .filter(Submission.user_id == current_user.id)
        .scalar()
        or 0
    )
    return StudentStats(
        lessons_started=len(progress_items),
        lessons_completed=len([item for item in progress_items if item.completion_percent == 100]),
        average_completion_percent=int(sum(item.completion_percent for item in progress_items) / len(progress_items)) if progress_items else 0,
        submissions_count=submissions_count,
        accepted_submissions_count=accepted_count,
        solved_tasks_count=solved_tasks,
        average_score=int(average_score),
        submissions_by_status=[StatusCount(status=status, count=count) for status, count in status_rows],
        recent_submissions=serialize_recent_submissions(db, current_user.id),
    )


@router.get("/course/{course_id}", response_model=CourseProgressRead)
def course_progress(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    lesson_ids = [row[0] for row in db.query(Lesson.id).join(Module).filter(Module.course_id == course_id).all()]
    items = db.query(Progress).filter(Progress.user_id == current_user.id, Progress.lesson_id.in_(lesson_ids)).all()
    total = len(lesson_ids)
    percent = int(sum(item.completion_percent for item in items) / total) if total else 0
    return CourseProgressRead(course_id=course_id, completion_percent=percent, lessons=[serialize_progress(item) for item in items])
