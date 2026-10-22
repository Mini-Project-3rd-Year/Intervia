from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ResumeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    raw_text: str | None
    created_at: datetime


class ResumeUploadResponse(BaseModel):
    resume_id: UUID
    filename: str
    status: str
    message: str


class ResumeProfileResponse(BaseModel):
    resume_id: UUID
    name: str | None = None
    skills: list[str] = Field(default_factory=list, max_length=20)
    experience_count: int = Field(default=0, ge=0)
    status: str