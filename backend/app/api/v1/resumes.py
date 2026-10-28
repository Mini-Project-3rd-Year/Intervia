"""Resume upload and user-scoped CRUD endpoints."""

from io import BytesIO
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pypdf import PdfReader
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.file_validation import validate_pdf_bytes
from app.db.session import get_db
from app.models.features import Resume
from app.schemas.resume import ResumeRead
from app.schemas.user import UserRead

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("", response_model=ResumeRead, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Resume:
    settings = get_settings()
    content = await file.read(settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024 + 1)
    validate_pdf_bytes(content, max_size_bytes=settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024)

    try:
        reader = PdfReader(BytesIO(content))
        raw_text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Unable to parse PDF content.") from exc

    resume = Resume(
        user_id=current_user.id,
        filename=file.filename or "resume.pdf",
        raw_text=raw_text,
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    return resume


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