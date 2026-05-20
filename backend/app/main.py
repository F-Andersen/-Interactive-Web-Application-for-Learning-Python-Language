from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, auth, courses, lessons, progress, tasks
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(courses.router, prefix="/api")
app.include_router(lessons.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(progress.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
