from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class InterviewCreate(BaseModel):
    type: str = Field("mixed", min_length=2, max_length=50)
    difficulty: int = Field(5, ge=1, le=10)
    duration: int | None = Field(None, ge=1, le=240)
    resume_id: UUID | None = None
    job_id: UUID | None = None


class InterviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type: str
    difficulty: int
    duration: int | None
    status: str
    resume_id: UUID | None
    job_id: UUID | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime



class QuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    question: str
    category: str | None
    difficulty: int | None
    sequence_number: int



class AnswerCreate(BaseModel):
    transcript: str = Field(..., min_length=1, max_length=20000)
    audio_url: str | None = None
    duration_seconds: int | None = Field(None, ge=0, le=3600)


class EvaluationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    answer_id: UUID
    relevance: float
    technical_accuracy: float
    clarity: float
    feedback: str
