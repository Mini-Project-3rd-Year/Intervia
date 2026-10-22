"""Resume upload and user-scoped CRUD endpoints."""

import asyncio
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID
from zipfile import BadZipFile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from google.genai.errors import APIError
from pydantic import ValidationError
from docx.opc.exceptions import PackageNotFoundError
from pypdf.errors import PdfReadError
from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.file_validation import validate_resume_bytes
from app.core.logging import get_logger
from app.db.session import get_db
from app.models.features import Resume
from app.schemas.resume import ResumeProfileResponse, ResumeRead, ResumeUploadResponse
from app.schemas.user import UserRead
from app.services.resume_parser import DOCX_MIME_TYPE, PDF_MIME_TYPE, extract_text_from_file

router = APIRouter(prefix="/resumes", tags=["resumes"])
resume_intelligence_router = APIRouter(prefix="/resume", tags=["resume"])
logger = get_logger(__name__)


async def _store_resume(
    file: UploadFile,
    *,
    current_user: UserRead,
    db: AsyncSession,
) -> Resume:
    settings = get_settings()
    content = await file.read(settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024 + 1)
    mime_type = file.content_type or ""
    validate_resume_bytes(
        content,
        mime_type,
        max_size_bytes=settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024,
    )

    resume_id = uuid.uuid4()
    extension = ".pdf" if mime_type == PDF_MIME_TYPE else ".docx"
    upload_dir = Path(settings.LOCAL_STORAGE_PATH) / "resumes"
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"{resume_id}{extension}"
    file_path.write_bytes(content)

    try:
        raw_text = await asyncio.to_thread(
            extract_text_from_file,
            str(file_path),
            mime_type,
        )
    except (BadZipFile, OSError, PackageNotFoundError, PdfReadError, ValueError) as exc:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Unable to parse resume content.") from exc

    resume = Resume(
        id=resume_id,
        user_id=current_user.id,
        filename=Path(file.filename or f"resume{extension}").name[:255],
        file_url=str(file_path.resolve()),
        mime_type=mime_type,
        raw_text=raw_text,
        status="ready" if raw_text else "error",
        processed_at=datetime.now(timezone.utc),
    )
    db.add(resume)
    try:
        await db.commit()
    except SQLAlchemyError:
        await db.rollback()
        file_path.unlink(missing_ok=True)
        raise
    await db.refresh(resume)
    return resume


@router.post("", response_model=ResumeRead, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Resume:
    return await _store_resume(file, current_user=current_user, db=db)


@resume_intelligence_router.post(
    "/upload",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_resume_for_intelligence(
    file: UploadFile = File(...),
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResumeUploadResponse:
    resume = await _store_resume(file, current_user=current_user, db=db)
    message = (
        "Resume uploaded and processed successfully."
        if resume.status == "ready"
        else "Upload saved, but no text could be extracted."
    )
    return ResumeUploadResponse(
        resume_id=resume.id,
        filename=resume.filename,
        status=resume.status,
        message=message,
    )


@resume_intelligence_router.get(
    "/{resume_id}/profile",
    response_model=ResumeProfileResponse,
)
async def get_resume_profile(
    resume_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResumeProfileResponse:
    resume = await db.scalar(
        select(Resume).where(
            Resume.id == resume_id,
            Resume.user_id == current_user.id,
        )
    )
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found.")
    if not resume.raw_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Resume text could not be extracted.",
        )
    if resume.parsed_profile is not None:
        return ResumeProfileResponse(resume_id=resume.id, status=resume.status, **resume.parsed_profile)

    settings = get_settings()
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Resume profile extraction is not configured. Set GEMINI_API_KEY.",
        )

    from google import genai

    prompt = f"""Extract key information from this resume text.
Return ONLY valid JSON with this shape:
{{"name": string or null, "skills": string[], "experience_count": integer}}

Resume text:
{resume.raw_text[:3000]}"""

    def extract_profile() -> str:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model=settings.LLM_MODEL,
            contents=prompt,
        )
        return response.text or ""

    try:
        raw_profile = await asyncio.to_thread(extract_profile)
    except APIError as exc:
        logger.error("Resume profile extraction failed", resume_id=str(resume_id), error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resume profile extraction failed.",
        ) from exc

    raw_profile = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", raw_profile, flags=re.IGNORECASE)
    try:
        profile_data = ResumeProfileResponse.model_validate(
            {"resume_id": resume.id, "status": resume.status, **json.loads(raw_profile)}
        )
    except (json.JSONDecodeError, ValidationError) as exc:
        logger.error("Gemini returned an invalid resume profile", resume_id=str(resume_id))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resume profile extraction returned invalid data.",
        ) from exc

    resume.parsed_profile = {
        "name": profile_data.name,
        "skills": profile_data.skills,
        "experience_count": profile_data.experience_count,
    }
    await db.commit()
    return profile_data


@router.get("", response_model=list[ResumeRead])
async def list_resumes(
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Resume]:
    result = await db.execute(
        select(Resume).where(Resume.user_id == current_user.id).order_by(Resume.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{resume_id}", response_model=ResumeRead)
async def get_resume(
    resume_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Resume:
    resume = await db.scalar(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    if resume is None:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    result = await db.execute(
        delete(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Resume not found.")
    await db.commit()