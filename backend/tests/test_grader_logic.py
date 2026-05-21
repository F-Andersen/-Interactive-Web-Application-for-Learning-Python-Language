from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.content import Task
from app.models.progress import Progress
from app.models.submission import Submission
from app.services.code_runner import RunResult
from app.services.grader import grade_submission


@dataclass
class FakeRunner:
    stdout: str
    status: str = "accepted"
    stderr: str = ""

    def run(self, code: str, input_data: str | None, timeout_ms: int, memory_limit_mb: int) -> RunResult:
        return RunResult(status=self.status, stdout=self.stdout, stderr=self.stderr, execution_time_ms=3)


def test_accepted_submission_updates_progress_and_masks_hidden_cases(db_session: Session, seeded_course: dict[str, object]):
    user = seeded_course["user"]
    task = db_session.get(Task, seeded_course["task"].id)

    submission, results = grade_submission(db_session, user, task, 'print("Hello")', runner=FakeRunner("Hello\n"))

    assert submission.status == "accepted"
    assert submission.passed_tests == 2
    assert submission.score == 100
    assert results[1].is_hidden is True
    assert results[1].input_data is None
    assert results[1].expected_output is None

    progress = db_session.query(Progress).filter_by(user_id=user.id, lesson_id=task.lesson_id).one()
    assert progress.completion_percent == 50
    assert progress.completed_at is None


def test_wrong_answer_is_saved_without_progress(db_session: Session, seeded_course: dict[str, object]):
    user = seeded_course["user"]
    task = db_session.get(Task, seeded_course["task"].id)

    submission, results = grade_submission(db_session, user, task, 'print("Bye")', runner=FakeRunner("Bye\n"))

    assert submission.status == "wrong_answer"
    assert submission.passed_tests == 0
    assert results[0].status == "wrong_answer"
    assert db_session.query(Progress).filter_by(user_id=user.id, lesson_id=task.lesson_id).first() is None
    assert db_session.query(Submission).filter_by(user_id=user.id, task_id=task.id).count() == 1


def test_runtime_error_stops_after_first_failing_case(db_session: Session, seeded_course: dict[str, object]):
    user = seeded_course["user"]
    task = db_session.get(Task, seeded_course["task"].id)

    submission, results = grade_submission(
        db_session,
        user,
        task,
        "raise RuntimeError()",
        runner=FakeRunner("", status="runtime_error", stderr="boom"),
    )

    assert submission.status == "runtime_error"
    assert submission.error_message == "boom"
    assert len(results) == 1
