from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.content import Course, Module
from app.models.user import User
from app.schemas.content import CourseRead

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=list[CourseRead])
def list_courses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Course).options(joinedload(Course.modules))
    if current_user.role.name != "admin":
        query = query.filter(Course.publish_status == "published")
    return query.order_by(Course.id).all()


@router.get("/{course_id}", response_model=CourseRead)
def get_course(course_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    course = (
        db.query(Course)
        .options(joinedload(Course.modules).joinedload(Module.lessons))
        .filter(Course.id == course_id)
        .first()
    )
    if not course or (current_user.role.name != "admin" and course.publish_status != "published"):
        raise HTTPException(status_code=404, detail="Course not found")
    return course
