from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.content import Task, TestCase
from app.models.progress import Progress, utcnow
from app.models.submission import Submission
from app.models.user import User
from app.services.code_runner import DockerCodeRunner


@dataclass
class CaseResult:
    order_index: int
    status: str
    output: str | None
    error: str | None
    input_data: str | None
    expected_output: str | None
    is_hidden: bool


def normalize_output(value: str | None) -> str:
    return (value or "").replace("\r\n", "\n").strip()


def update_lesson_progress(db: Session, user: User, task: Task) -> None:
    lesson = task.lesson
    total_tasks = len(lesson.tasks)
    if total_tasks == 0:
        return
    accepted_task_ids = {
        row[0]
        for row in db.query(Submission.task_id)
        .filter(
            Submission.user_id == user.id,
            Submission.status == "accepted",
            Submission.task_id.in_([item.id for item in lesson.tasks]),
        )
        .distinct()
        .all()
    }
    percent = int((len(accepted_task_ids) / total_tasks) * 100)
    progress = db.query(Progress).filter_by(user_id=user.id, lesson_id=lesson.id).first()
    if not progress:
        progress = Progress(user_id=user.id, lesson_id=lesson.id)
        db.add(progress)
    progress.completion_percent = percent
    progress.last_activity_at = utcnow()
    progress.completed_at = utcnow() if percent == 100 else None


def grade_submission(db: Session, user: User, task: Task, code: str, runner=None) -> tuple[Submission, list[CaseResult]]:
    runner = runner or DockerCodeRunner()
    cases: list[TestCase] = list(task.test_cases)
    results: list[CaseResult] = []
    passed = 0
    total_time = 0
    final_status = "accepted"
    error_message: str | None = None

    for case in cases:
        run = runner.run(code, case.input_data, task.time_limit_ms, task.memory_limit_mb)
        total_time += run.execution_time_ms
        expected = normalize_output(case.expected_output)
        actual = normalize_output(run.stdout)
        case_status = run.status
        if run.status == "accepted" and actual != expected:
            case_status = "wrong_answer"
        if case_status == "accepted":
            passed += 1
        elif final_status == "accepted":
            final_status = case_status
            error_message = run.stderr or f"Expected {expected!r}, got {actual!r}"
        results.append(
            CaseResult(
                order_index=case.order_index,
                status=case_status,
                output=None if case.is_hidden else actual,
                error=run.stderr if case_status != "accepted" else None,
                input_data=None if case.is_hidden else case.input_data,
                expected_output=None if case.is_hidden else case.expected_output,
                is_hidden=case.is_hidden,
            )
        )
        if case_status in {"compile_error", "runtime_error", "time_limit"}:
            break

    total = len(cases)
    score = int((passed / total) * 100) if total else 0
    submission = Submission(
        user_id=user.id,
        task_id=task.id,
        code=code,
        status=final_status,
        score=score,
        passed_tests=passed,
        total_tests=total,
        execution_time_ms=total_time,
        error_message=error_message,
    )
    db.add(submission)
    db.flush()
    if final_status == "accepted":
        update_lesson_progress(db, user, task)
    db.commit()
    db.refresh(submission)
    return submission, results
