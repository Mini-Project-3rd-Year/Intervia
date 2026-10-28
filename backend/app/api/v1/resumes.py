"""Resume upload and user-scoped CRUD endpoints."""

import asyncio
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from google import genai
from google.genai.errors import APIError
from google.genai import types
from pydantic import ValidationError
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.file_validation import detect_resume_mime_type, validate_resume_bytes
from app.core.logging import get_logger
from app.db.session import get_db
from app.models.features import Resume, ResumeUsage
from app.schemas.resume import ResumeProfileResponse, ResumeRead, ResumeUploadResponse
from app.schemas.user import UserRead
from app.services.resume_parser import extract_text_from_file

router = APIRouter(prefix="/resumes", tags=["resumes"])
resume_intelligence_router = APIRouter(prefix="/resume", tags=["resume"])
logger = get_logger(__name__)

PROFILE_RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "name": {"type": "STRING", "nullable": True},
        "skills": {"type": "ARRAY", "items": {"type": "STRING"}},
        "experience_count": {"type": "INTEGER"},
    },
    "required": ["name", "skills", "experience_count"],
}


async def _remove_upload(file_path: Path) -> None:
    try:
        await asyncio.to_thread(file_path.unlink, missing_ok=True)
    except OSError as exc:
        logger.error("Could not remove failed resume upload", path=str(file_path), error=str(exc))


async def _consume_daily_quota(
    db: AsyncSession,
    *,
    user_id: str,
    usage_column: str,
    limit: int,
) -> None:
    usage_date = datetime.now(timezone.utc).date()
    usage_value = getattr(ResumeUsage, usage_column)
    statement = (
        pg_insert(ResumeUsage)
        .values(user_id=user_id, usage_date=usage_date, **{usage_column: 1})
        .on_conflict_do_update(
            index_elements=[ResumeUsage.user_id, ResumeUsage.usage_date],
            set_={usage_column: usage_value + 1},
            where=usage_value < limit,
        )
        .returning(usage_value)
    )
    result = await db.execute(statement)
    if result.scalar_one_or_none() is None:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Daily resume usage limit reached. Try again tomorrow.",
        )
    await db.commit()


async def _store_resume(
    file: UploadFile,
    *,
    current_user: UserRead,
    db: AsyncSession,
    ai_processing_consent: bool = False,
) -> Resume:
    settings = get_settings()
    content = await file.read(settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024 + 1)
    mime_type = detect_resume_mime_type(
        content,
        file.filename or "",
        file.content_type,
    )
    await asyncio.to_thread(
        validate_resume_bytes,
        content,
        mime_type,
        max_size_bytes=settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024,
    )
    await _consume_daily_quota(
        db,
        user_id=current_user.id,
        usage_column="uploads",
        limit=settings.RESUME_DAILY_UPLOAD_LIMIT,
    )

    resume_id = uuid.uuid4()
    extension = ".pdf" if mime_type == "application/pdf" else ".docx"
    upload_dir = Path(settings.LOCAL_STORAGE_PATH) / "resumes"
    file_path = upload_dir / f"{resume_id}{extension}"
    try:
        await asyncio.to_thread(upload_dir.mkdir, parents=True, exist_ok=True)
        await asyncio.to_thread(file_path.write_bytes, content)
    except OSError as exc:
        await _remove_upload(file_path)
        logger.error("Resume upload could not be stored", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to store the uploaded resume.",
        ) from exc

    try:
        raw_text = await asyncio.to_thread(
            extract_text_from_file,
            str(file_path),
            mime_type,
        )
    except Exception as exc:
        await _remove_upload(file_path)
        logger.warning("Resume parsing failed", mime_type=mime_type, error=str(exc))
        raise HTTPException(status_code=400, detail="Unable to parse resume content.") from exc

    resume = Resume(
        id=resume_id,
        user_id=current_user.id,
        filename=Path(file.filename or f"resume{extension}").name[:255],
        file_url=f"resumes/{file_path.name}",
        mime_type=mime_type,
        raw_text=raw_text,
        status="ready" if raw_text else "error",
        processed_at=datetime.now(timezone.utc).replace(tzinfo=None),
        ai_processing_consent=ai_processing_consent,
    )
    db.add(resume)
    try:
        await db.commit()
    except Exception:
        try:
            await db.rollback()
        except Exception as rollback_error:
            logger.error("Resume transaction rollback failed", error=str(rollback_error))
        await _remove_upload(file_path)
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
    consent_to_ai_processing: bool = Form(...),
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResumeUploadResponse:
    if not consent_to_ai_processing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consent is required before resume content can be sent to Gemini.",
        )
    resume = await _store_resume(
        file,
        current_user=current_user,
        db=db,
        ai_processing_consent=True,
    )
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
    if not resume.ai_processing_consent:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Consent is required before resume content can be sent to Gemini.",
        )
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

    prompt = f"""Extract the candidate's full name, skills, and work experience from the resume.
Count each distinct professional job or internship role once in experience_count.
Do not count projects, education, or multiple bullet points from the same role as separate jobs.
Include skills supported by the entire supplied resume text.

Resume text (may be truncated at {settings.RESUME_PROFILE_MAX_CHARS} characters):
{resume.raw_text[:settings.RESUME_PROFILE_MAX_CHARS]}"""

    await _consume_daily_quota(
        db,
        user_id=current_user.id,
        usage_column="profile_extractions",
        limit=settings.RESUME_DAILY_PROFILE_LIMIT,
    )

    def extract_profile() -> str:
        client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
            http_options=types.HttpOptions(
                timeout=settings.RESUME_PROFILE_TIMEOUT_SECONDS * 1000,
            ),
        )
        response = client.models.generate_content(
            model=settings.LLM_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=PROFILE_RESPONSE_SCHEMA,
            ),
        )
        return response.text or ""

    try:
        raw_profile = await asyncio.wait_for(
            asyncio.to_thread(extract_profile),
            timeout=settings.RESUME_PROFILE_TIMEOUT_SECONDS,
        )
    except (TimeoutError, httpx.TimeoutException) as exc:
        logger.error("Resume profile extraction timed out", resume_id=str(resume_id))
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Resume profile extraction timed out. Please retry.",
        ) from exc
    except APIError as exc:
        logger.error("Resume profile extraction failed", resume_id=str(resume_id), error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resume profile extraction failed.",
        ) from exc
    except Exception as exc:
        logger.error("Resume profile extraction failed", resume_id=str(resume_id), error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resume profile extraction failed.",
        ) from exc

    try:
        payload = json.loads(raw_profile)
        if not isinstance(payload, dict):
            raise ValueError("Gemini profile response must be a JSON object.")
        if isinstance(payload.get("skills"), list):
            payload["skills"] = payload["skills"][:20]
        profile_data = ResumeProfileResponse.model_validate(
            {"resume_id": resume.id, "status": resume.status, **payload}
        )
    except (json.JSONDecodeError, ValidationError, ValueError) as exc:
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