from datetime import datetime

from pydantic import BaseModel, Field


class TestCaseRead(BaseModel):
    id: int
    task_id: int
    input_data: str | None = None
    expected_output: str | None = None
    is_hidden: bool
    order_index: int

    model_config = {"from_attributes": True}


class TestCaseCreate(BaseModel):
    task_id: int
    input_data: str | None = ""
    expected_output: str = ""
    is_hidden: bool = False
    order_index: int = 0


class TestCaseUpdate(BaseModel):
    input_data: str | None = None
    expected_output: str | None = None
    is_hidden: bool | None = None
    order_index: int | None = None


class TaskBase(BaseModel):
    title: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    difficulty: str | None = "easy"
    starter_code: str | None = ""
    time_limit_ms: int = 5000
    memory_limit_mb: int = 128
    order_index: int = 0


class TaskCreate(TaskBase):
    lesson_id: int


class TaskUpdate(BaseModel):
    title: str | None = None
    statement: str | None = None
    difficulty: str | None = None
    starter_code: str | None = None
    time_limit_ms: int | None = None
    memory_limit_mb: int | None = None
    order_index: int | None = None


class TaskRead(TaskBase):
    id: int
    lesson_id: int
    test_cases: list[TestCaseRead] = []

    model_config = {"from_attributes": True}


class LessonBase(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)
    order_index: int = 0


class LessonCreate(LessonBase):
    module_id: int


class LessonUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    order_index: int | None = None


class LessonRead(LessonBase):
    id: int
    module_id: int
    tasks: list[TaskRead] = []

    model_config = {"from_attributes": True}


class ModuleBase(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None
    order_index: int = 0


class ModuleCreate(ModuleBase):
    course_id: int


class ModuleUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    order_index: int | None = None


class ModuleRead(ModuleBase):
    id: int
    course_id: int
    lessons: list[LessonRead] = []

    model_config = {"from_attributes": True}


class CourseBase(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None
    difficulty_level: str | None = "beginner"
    publish_status: str = "draft"


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    difficulty_level: str | None = None
    publish_status: str | None = None


class CourseRead(CourseBase):
    id: int
    created_by: int | None = None
    created_at: datetime
    updated_at: datetime
    modules: list[ModuleRead] = []

    model_config = {"from_attributes": True}
