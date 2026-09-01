"""app/api/v1/__init__.py — API v1 router assembly"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.core.config import get_settings

_settings = get_settings()

# All v1 routers are registered here
api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)   # Phase 1: Authentication

# Phase 4: RAG debug endpoint (dev only — guarded by DEBUG check inside the route)
from app.api.v1.rag import router as rag_router  # noqa: E402

api_v1_router.include_router(rag_router)

# Future routers (uncomment as phases are completed):
# from app.api.v1.resumes import router as resume_router
# from app.api.v1.jobs import router as job_router
# from app.api.v1.interviews import router as interview_router
# from app.api.v1.evaluations import router as evaluation_router
# from app.api.v1.coaching import router as coaching_router
# from app.api.v1.users import router as user_router
# api_v1_router.include_router(resume_router)
# api_v1_router.include_router(job_router)
# api_v1_router.include_router(interview_router)
# api_v1_router.include_router(evaluation_router)
# api_v1_router.include_router(coaching_router)
# api_v1_router.include_router(user_router)

