from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class JobAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=20, max_length=20000)
    resume_id: UUID | None = None


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: str | None
    required_skills: list
    preferred_skills: list
    matched_skills: list
    missing_skills: list
    skill_gaps: list
    created_at: datetime
