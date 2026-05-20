"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "db_application_roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=50), nullable=False, unique=True),
        sa.Column("description", sa.Text()),
    )
    op.create_table(
        "db_application_users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("db_application_roles.id"), nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False, unique=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "db_application_courses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("db_application_users.id")),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("difficulty_level", sa.String(length=30)),
        sa.Column("publish_status", sa.String(length=30), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "db_application_modules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("course_id", sa.Integer(), sa.ForeignKey("db_application_courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("course_id", "order_index", name="uq_module_course_order"),
    )
    op.create_table(
        "db_application_lessons",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("module_id", sa.Integer(), sa.ForeignKey("db_application_modules.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("module_id", "order_index", name="uq_lesson_module_order"),
    )
    op.create_table(
        "db_application_tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lesson_id", sa.Integer(), sa.ForeignKey("db_application_lessons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("statement", sa.Text(), nullable=False),
        sa.Column("difficulty", sa.String(length=30)),
        sa.Column("starter_code", sa.Text()),
        sa.Column("time_limit_ms", sa.Integer(), nullable=False, server_default="5000"),
        sa.Column("memory_limit_mb", sa.Integer(), nullable=False, server_default="128"),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "db_application_test_cases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("db_application_tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("input_data", sa.Text()),
        sa.Column("expected_output", sa.Text()),
        sa.Column("is_hidden", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "db_application_submissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("db_application_users.id"), nullable=False),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("db_application_tasks.id"), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("passed_tests", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_tests", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("execution_time_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text()),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "db_application_progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("db_application_users.id"), nullable=False),
        sa.Column("lesson_id", sa.Integer(), sa.ForeignKey("db_application_lessons.id"), nullable=False),
        sa.Column("completion_percent", sa.SmallInteger(), nullable=False, server_default="0"),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("user_id", "lesson_id", name="uq_progress_user_lesson"),
    )
    op.create_table(
        "db_application_snippets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("db_application_users.id"), nullable=False),
        sa.Column("title", sa.String(length=255)),
        sa.Column("code", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("db_application_snippets")
    op.drop_table("db_application_progress")
    op.drop_table("db_application_submissions")
    op.drop_table("db_application_test_cases")
    op.drop_table("db_application_tasks")
    op.drop_table("db_application_lessons")
    op.drop_table("db_application_modules")
    op.drop_table("db_application_courses")
    op.drop_table("db_application_users")
    op.drop_table("db_application_roles")
