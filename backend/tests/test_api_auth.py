from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.session import get_db
from app.main import app
from app.models.user import Role, User


def test_register_login_and_me_flow(db_session: Session):
    student_role = Role(name="student", description="Student")
    db_session.add(student_role)
    db_session.commit()

    def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app)
        register_response = client.post(
            "/api/auth/register",
            json={"username": "newbie", "email": "newbie@example.com", "password": "secret123"},
        )
        assert register_response.status_code == 201
        assert register_response.json()["role"]["name"] == "student"
        assert "password_hash" not in register_response.json()

        login_response = client.post(
            "/api/auth/login",
            json={"login": "newbie@example.com", "password": "secret123"},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        me_response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_response.status_code == 200
        assert me_response.json()["email"] == "newbie@example.com"
    finally:
        app.dependency_overrides.clear()


def test_blocked_user_cannot_login(db_session: Session):
    role = Role(name="student", description="Student")
    db_session.add(role)
    db_session.flush()
    user = User(
        role_id=role.id,
        username="blocked",
        email="blocked@example.com",
        password_hash=get_password_hash("secret123"),
        status="blocked",
    )
    db_session.add(user)
    db_session.commit()

    def override_db():
        yield db_session

    app.dependency_overrides[get_db] = override_db
    try:
        client = TestClient(app)
        response = client.post(
            "/api/auth/login",
            json={"login": "blocked@example.com", "password": "secret123"},
        )
        assert response.status_code == 403
        assert response.json()["detail"] == "User is not active"
    finally:
        app.dependency_overrides.clear()
