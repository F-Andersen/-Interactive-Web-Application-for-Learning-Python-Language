# Interactive Web Application for Learning Python Language

MVP навчальної вебсистеми для вивчення Python: курси, модулі, уроки, практичні задачі, Monaco Editor у браузері, автоматична перевірка коду, JWT-авторизація, ролі й прогрес студента.

## Stack

- Frontend: React 18, Vite, TypeScript, React Router, Axios, `@monaco-editor/react`.
- Backend: FastAPI, SQLAlchemy 2.0, Alembic, Pydantic, JWT, passlib/bcrypt.
- Database: PostgreSQL 16.
- Infrastructure: Docker Compose, окремі контейнери `db`, `api`, `frontend`.
- Code execution: backend запускає Python-рішення через Docker runner image `python:3.12-slim`.

## Structure

```text
diploms/
├── docker-compose.yml
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic/
│   └── app/
│       ├── api/
│       ├── core/
│       ├── db/
│       ├── models/
│       ├── schemas/
│       ├── services/
│       └── scripts/seed.py
└── frontend/
    ├── Dockerfile
    ├── package.json
    └── src/
```

## Run

```bash
docker compose up --build
```

Then open:

- Frontend: <http://localhost:5173>
- Backend docs: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health>
- PostgreSQL is exposed on host port `55432` to avoid common local `5432` conflicts; inside Docker Compose services use `db:5432`.

## Migrations

In another terminal:

```bash
docker compose exec api alembic upgrade head
```

## Seed Data

```bash
docker compose exec api python -m app.scripts.seed
```

Seed creates roles `student`, `admin`, `manager`, `developer`, two users, a published course “Основи Python”, modules, lessons, tasks and visible/hidden test cases.

## Test Logins

- Admin: `admin@example.com` / `admin123`
- Student: `student@example.com` / `student123`

## API

Auth:

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

Courses and learning:

- `GET /api/courses`
- `GET /api/courses/{course_id}`
- `GET /api/lessons/{lesson_id}`
- `GET /api/tasks/{task_id}`
- `POST /api/tasks/{task_id}/submit`
- `GET /api/tasks/{task_id}/submissions`

Progress:

- `GET /api/progress/me`
- `GET /api/progress/me/stats`
- `GET /api/progress/course/{course_id}`

Admin:

- `GET /api/admin/stats`
- `CRUD /api/admin/courses`
- `CRUD /api/admin/modules`
- `CRUD /api/admin/lessons`
- `CRUD /api/admin/tasks`
- `CRUD /api/admin/test-cases`
- `GET /api/admin/users`
- `PATCH /api/admin/users/{user_id}/status?status_value=blocked`

## Sandbox Notes

Submissions are executed in a short-lived Docker container with:

- `--network none` for no network access;
- CPU limit `--cpus 1`;
- memory limit from task settings, default `128m`;
- subprocess timeout from task settings, default `5000 ms`;
- source mounted read-only into `/workspace`.

Hidden test cases are used by the grader, but their `input_data` and `expected_output` are not returned to students.

## Tests

Backend has small tests for auth helpers and grader output normalization:

```bash
docker compose exec api pytest
```

## Typical Local Flow

```bash
docker compose up --build
docker compose exec api alembic upgrade head
docker compose exec api python -m app.scripts.seed
```

Login as the student, open “Основи Python”, solve “Hello, World!” with:

```python
print("Hello, World!")
```

An accepted submission updates lesson progress.
