from datetime import datetime

from pydantic import BaseModel, Field


class SubmissionCreate(BaseModel):
    code: str = Field(min_length=1)


class TestResultRead(BaseModel):
    order_index: int
    status: str
    output: str | None = None
    error: str | None = None
    input_data: str | None = None
    expected_output: str | None = None
    is_hidden: bool


class SubmissionRead(BaseModel):
    id: int
    task_id: int
    status: str
    score: int
    passed_tests: int
    total_tests: int
    execution_time_ms: int
    error_message: str | None = None
    submitted_at: datetime

    model_config = {"from_attributes": True}


class SubmissionResult(SubmissionRead):
    tests: list[TestResultRead] = []
