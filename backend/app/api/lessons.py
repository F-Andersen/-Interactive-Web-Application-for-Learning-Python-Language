from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.content import Course, Lesson, Module
from app.models.user import User
from app.schemas.content import LessonRead

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.get("/{lesson_id}", response_model=LessonRead)
def get_lesson(lesson_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    lesson = db.query(Lesson).options(joinedload(Lesson.tasks)).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    course = db.query(Course).join(Module).filter(Module.id == lesson.module_id).first()
    if current_user.role.name != "admin" and course.publish_status != "published":
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson
