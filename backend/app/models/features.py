"""SQLAlchemy models for candidate, job, and interview data."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    file_url: Mapped[str] = mapped_column(Text, default="")
    raw_text: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    resume_id: Mapped[UUID] = mapped_column(ForeignKey("resumes.id"), unique=True)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    skills: Mapped[list] = mapped_column(JSON, default=list)
    projects: Mapped[list] = mapped_column(JSON, default=list)
    experience: Mapped[list] = mapped_column(JSON, default=list)
    education: Mapped[list] = mapped_column(JSON, default=list)
    certifications: Mapped[list] = mapped_column(JSON, default=list)
    achievements: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    role: Mapped[str] = mapped_column(String(255), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text)
    required_skills: Mapped[list] = mapped_column(JSON, default=list)
    preferred_skills: Mapped[list] = mapped_column(JSON, default=list)
    matched_skills: Mapped[list] = mapped_column(JSON, default=list)
    missing_skills: Mapped[list] = mapped_column(JSON, default=list)
    skill_gaps: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    resume_id: Mapped[UUID] = mapped_column(nullable=True)
    job_id: Mapped[UUID] = mapped_column(nullable=True)
    type: Mapped[str] = mapped_column(String(50))
    difficulty: Mapped[int] = mapped_column(Integer, default=5)
    duration: Mapped[int] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="scheduled")
    strategy: Mapped[dict] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    overall_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    interview_id: Mapped[UUID] = mapped_column(ForeignKey("interviews.id"), index=True)
    question: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(100), nullable=True)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=True)
    source: Mapped[str] = mapped_column(String(100), nullable=True)
    sequence_number: Mapped[int] = mapped_column(Integer)
    asked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    question_id: Mapped[UUID] = mapped_column(ForeignKey("interview_questions.id"), index=True)
    transcript: Mapped[str] = mapped_column(Text, nullable=True)
    audio_url: Mapped[str] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class InterviewEvaluation(Base):
    __tablename__ = "interview_evaluations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    answer_id: Mapped[UUID] = mapped_column(ForeignKey("interview_answers.id"), unique=True)
    relevance: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    technical_accuracy: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    clarity: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    feedback: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)