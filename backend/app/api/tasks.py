from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.content import Course, Lesson, Module, Task
from app.models.submission import Submission
from app.models.user import User
from app.schemas.content import TaskRead
from app.schemas.submission import SubmissionCreate, SubmissionRead, SubmissionResult, TestResultRead
from app.services.grader import grade_submission

router = APIRouter(prefix="/tasks", tags=["tasks"])


def visible_task_or_404(task_id: int, db: Session, user: User) -> Task:
    task = db.query(Task).options(joinedload(Task.test_cases), joinedload(Task.lesson).joinedload(Lesson.tasks)).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    course = db.query(Course).join(Module).filter(Module.id == task.lesson.module_id).first()
    if user.role.name != "admin" and course.publish_status != "published":
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = visible_task_or_404(task_id, db, current_user)
    if current_user.role.name != "admin":
        for case in task.test_cases:
            if case.is_hidden:
                case.input_data = None
                case.expected_output = None
    return task


@router.post("/{task_id}/submit", response_model=SubmissionResult)
def submit_task(task_id: int, payload: SubmissionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = visible_task_or_404(task_id, db, current_user)
    submission, tests = grade_submission(db, current_user, task, payload.code)
    result = SubmissionResult.model_validate(submission)
    result.tests = [TestResultRead(**case.__dict__) for case in tests]
    return result


@router.get("/{task_id}/submissions", response_model=list[SubmissionRead])
def list_submissions(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    visible_task_or_404(task_id, db, current_user)
    return (
        db.query(Submission)
        .filter(Submission.task_id == task_id, Submission.user_id == current_user.id)
        .order_by(Submission.submitted_at.desc())
        .limit(30)
        .all()
    )
