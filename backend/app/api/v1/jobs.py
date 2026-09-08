"""Persisted job-description analysis endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.sanitization import sanitize_text
from app.db.session import get_db
from app.models.features import JobDescription
from app.schemas.job import JobAnalyzeRequest, JobRead
from app.schemas.user import UserRead

router = APIRouter(prefix="/jobs", tags=["jobs"])

KNOWN_SKILLS = (
    "python", "fastapi", "django", "javascript", "typescript", "react",
    "postgresql", "sql", "redis", "docker", "kubernetes", "aws", "git",
)


@router.post("/analyze", response_model=JobRead, status_code=201)
async def analyze_job(
    payload: JobAnalyzeRequest,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JobDescription:
    text = sanitize_text(payload.text, max_length=20000)
    lower_text = text.lower()
    required = [skill for skill in KNOWN_SKILLS if skill in lower_text]
    role = text.splitlines()[0][:255] if text.splitlines() else None
    job = JobDescription(
        user_id=current_user.id,
        role=role,
        raw_text=text,
        required_skills=required,
        preferred_skills=[],
        matched_skills=[],
        missing_skills=required,
        skill_gaps=[f"{skill} proficiency" for skill in required],
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job