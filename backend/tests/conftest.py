from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base
from app.models import Course, Lesson, Module, Role, Task, TestCase, User


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def seeded_course(db_session: Session) -> dict[str, object]:
    student_role = Role(name="student", description="Student")
    admin_role = Role(name="admin", description="Admin")
    db_session.add_all([student_role, admin_role])
    db_session.flush()

    user = User(
        role_id=student_role.id,
        username="student",
        email="student@example.com",
        password_hash="hash",
    )
    admin = User(
        role_id=admin_role.id,
        username="admin",
        email="admin@example.com",
        password_hash="hash",
    )
    db_session.add_all([user, admin])
    db_session.flush()

    course = Course(
        created_by=admin.id,
        title="Test Python",
        description="Course",
        difficulty_level="beginner",
        publish_status="published",
    )
    db_session.add(course)
    db_session.flush()
    module = Module(course_id=course.id, title="Basics", order_index=1)
    db_session.add(module)
    db_session.flush()
    lesson = Lesson(module_id=module.id, title="Output", content="Use print().", order_index=1)
    db_session.add(lesson)
    db_session.flush()
    task = Task(
        lesson_id=lesson.id,
        title="Hello",
        statement="Print hello.",
        starter_code='print("")',
        order_index=1,
    )
    second_task = Task(
        lesson_id=lesson.id,
        title="Echo",
        statement="Echo input.",
        starter_code="print(input())",
        order_index=2,
    )
    db_session.add_all([task, second_task])
    db_session.flush()
    db_session.add_all(
        [
            TestCase(task_id=task.id, input_data="", expected_output="Hello", is_hidden=False, order_index=1),
            TestCase(task_id=task.id, input_data="", expected_output="Hello", is_hidden=True, order_index=2),
            TestCase(task_id=second_task.id, input_data="Python\n", expected_output="Python", is_hidden=False, order_index=1),
        ]
    )
    db_session.commit()
    return {
        "user": user,
        "admin": admin,
        "course": course,
        "module": module,
        "lesson": lesson,
        "task": task,
        "second_task": second_task,
    }
