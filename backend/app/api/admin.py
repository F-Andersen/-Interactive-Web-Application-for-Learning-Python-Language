from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.db.session import get_db
from app.models.content import Course, Lesson, Module, Task, TestCase
from app.models.submission import Submission
from app.models.user import Role, User
from app.schemas.auth import UserRead
from app.schemas.content import (
    CourseCreate,
    CourseRead,
    CourseUpdate,
    LessonCreate,
    LessonRead,
    LessonUpdate,
    ModuleCreate,
    ModuleRead,
    ModuleUpdate,
    TaskCreate,
    TaskRead,
    TaskUpdate,
    TestCaseCreate,
    TestCaseRead,
    TestCaseUpdate,
)
from app.schemas.stats import AdminStats, CourseStats, StatusCount, SubmissionActivity

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_roles("admin"))])


def get_or_404(db: Session, model, item_id: int):
    item = db.get(model, item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    return item


def patch_model(item, payload):
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)


def status_counts(db: Session, user_id: int | None = None) -> list[StatusCount]:
    query = db.query(Submission.status, func.count(Submission.id)).group_by(Submission.status)
    if user_id is not None:
        query = query.filter(Submission.user_id == user_id)
    return [StatusCount(status=status, count=count) for status, count in query.all()]


def recent_submission_rows(db: Session, limit: int = 10) -> list[SubmissionActivity]:
    rows = (
        db.query(Submission, User, Task, Lesson, Module, Course)
        .join(User, User.id == Submission.user_id)
        .join(Task, Task.id == Submission.task_id)
        .join(Lesson, Lesson.id == Task.lesson_id)
        .join(Module, Module.id == Lesson.module_id)
        .join(Course, Course.id == Module.course_id)
        .order_by(Submission.submitted_at.desc())
        .limit(limit)
        .all()
    )
    return [
        SubmissionActivity(
            id=submission.id,
            user_email=user.email,
            username=user.username,
            task_title=task.title,
            course_title=course.title,
            status=submission.status,
            score=submission.score,
            submitted_at=submission.submitted_at,
        )
        for submission, user, task, lesson, module, course in rows
    ]


@router.get("/stats", response_model=AdminStats)
def admin_stats(db: Session = Depends(get_db)):
    submissions_count = db.query(func.count(Submission.id)).scalar() or 0
    accepted_count = db.query(func.count(Submission.id)).filter(Submission.status == "accepted").scalar() or 0
    average_score = int(db.query(func.coalesce(func.avg(Submission.score), 0)).scalar() or 0)
    course_rows = (
        db.query(
            Course.id,
            Course.title,
            Course.publish_status,
            func.count(func.distinct(Module.id)).label("modules_count"),
            func.count(func.distinct(Lesson.id)).label("lessons_count"),
            func.count(func.distinct(Task.id)).label("tasks_count"),
            func.count(func.distinct(Submission.id)).label("submissions_count"),
            func.count(func.distinct(case((Submission.status == "accepted", Submission.id)))).label("accepted_count"),
            func.count(func.distinct(case((Submission.status == "accepted", Submission.user_id)))).label("active_students_count"),
        )
        .outerjoin(Module, Module.course_id == Course.id)
        .outerjoin(Lesson, Lesson.module_id == Module.id)
        .outerjoin(Task, Task.lesson_id == Lesson.id)
        .outerjoin(Submission, Submission.task_id == Task.id)
        .group_by(Course.id)
        .order_by(Course.id)
        .all()
    )
    return AdminStats(
        users_count=db.query(func.count(User.id)).scalar() or 0,
        students_count=db.query(func.count(User.id)).join(Role).filter(Role.name == "student").scalar() or 0,
        admins_count=db.query(func.count(User.id)).join(Role).filter(Role.name == "admin").scalar() or 0,
        blocked_users_count=db.query(func.count(User.id)).filter(User.status == "blocked").scalar() or 0,
        courses_count=db.query(func.count(Course.id)).scalar() or 0,
        published_courses_count=db.query(func.count(Course.id)).filter(Course.publish_status == "published").scalar() or 0,
        lessons_count=db.query(func.count(Lesson.id)).scalar() or 0,
        tasks_count=db.query(func.count(Task.id)).scalar() or 0,
        test_cases_count=db.query(func.count(TestCase.id)).scalar() or 0,
        submissions_count=submissions_count,
        accepted_submissions_count=accepted_count,
        average_score=average_score,
        submissions_by_status=status_counts(db),
        course_stats=[
            CourseStats(
                course_id=row.id,
                title=row.title,
                publish_status=row.publish_status,
                modules_count=row.modules_count,
                lessons_count=row.lessons_count,
                tasks_count=row.tasks_count,
                submissions_count=row.submissions_count,
                accepted_submissions_count=row.accepted_count,
                active_students_count=row.active_students_count,
            )
            for row in course_rows
        ],
        recent_submissions=recent_submission_rows(db),
    )


@router.get("/users", response_model=list[UserRead])
def users(db: Session = Depends(get_db)):
    return db.query(User).order_by(User.id).all()


@router.patch("/users/{user_id}/status", response_model=UserRead)
def update_user_status(user_id: int, status_value: str, db: Session = Depends(get_db)):
    if status_value not in {"active", "blocked", "pending"}:
        raise HTTPException(status_code=400, detail="Unsupported user status")
    user = get_or_404(db, User, user_id)
    user.status = status_value
    db.commit()
    db.refresh(user)
    return user


@router.post("/courses", response_model=CourseRead)
def create_course(payload: CourseCreate, db: Session = Depends(get_db), current_user: User = Depends(require_roles("admin"))):
    course = Course(**payload.model_dump(), created_by=current_user.id)
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("/courses", response_model=list[CourseRead])
def list_admin_courses(db: Session = Depends(get_db)):
    return db.query(Course).order_by(Course.id).all()


@router.patch("/courses/{item_id}", response_model=CourseRead)
def update_course(item_id: int, payload: CourseUpdate, db: Session = Depends(get_db)):
    item = get_or_404(db, Course, item_id)
    patch_model(item, payload)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/courses/{item_id}", status_code=204)
def delete_course(item_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, Course, item_id))
    db.commit()


@router.post("/modules", response_model=ModuleRead)
def create_module(payload: ModuleCreate, db: Session = Depends(get_db)):
    item = Module(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/modules", response_model=list[ModuleRead])
def list_modules(db: Session = Depends(get_db)):
    return db.query(Module).order_by(Module.course_id, Module.order_index).all()


@router.patch("/modules/{item_id}", response_model=ModuleRead)
def update_module(item_id: int, payload: ModuleUpdate, db: Session = Depends(get_db)):
    item = get_or_404(db, Module, item_id)
    patch_model(item, payload)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/modules/{item_id}", status_code=204)
def delete_module(item_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, Module, item_id))
    db.commit()


@router.post("/lessons", response_model=LessonRead)
def create_lesson(payload: LessonCreate, db: Session = Depends(get_db)):
    item = Lesson(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/lessons", response_model=list[LessonRead])
def list_lessons(db: Session = Depends(get_db)):
    return db.query(Lesson).order_by(Lesson.module_id, Lesson.order_index).all()


@router.patch("/lessons/{item_id}", response_model=LessonRead)
def update_lesson(item_id: int, payload: LessonUpdate, db: Session = Depends(get_db)):
    item = get_or_404(db, Lesson, item_id)
    patch_model(item, payload)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/lessons/{item_id}", status_code=204)
def delete_lesson(item_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, Lesson, item_id))
    db.commit()


@router.post("/tasks", response_model=TaskRead)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    item = Task(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/tasks", response_model=list[TaskRead])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(Task).order_by(Task.lesson_id, Task.order_index).all()


@router.patch("/tasks/{item_id}", response_model=TaskRead)
def update_task(item_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    item = get_or_404(db, Task, item_id)
    patch_model(item, payload)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/tasks/{item_id}", status_code=204)
def delete_task(item_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, Task, item_id))
    db.commit()


@router.post("/test-cases", response_model=TestCaseRead)
def create_test_case(payload: TestCaseCreate, db: Session = Depends(get_db)):
    item = TestCase(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/test-cases", response_model=list[TestCaseRead])
def list_test_cases(db: Session = Depends(get_db)):
    return db.query(TestCase).order_by(TestCase.task_id, TestCase.order_index).all()


@router.patch("/test-cases/{item_id}", response_model=TestCaseRead)
def update_test_case(item_id: int, payload: TestCaseUpdate, db: Session = Depends(get_db)):
    item = get_or_404(db, TestCase, item_id)
    patch_model(item, payload)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/test-cases/{item_id}", status_code=204)
def delete_test_case(item_id: int, db: Session = Depends(get_db)):
    db.delete(get_or_404(db, TestCase, item_id))
    db.commit()
