"""
backend/app/models/interview.py
SQLAlchemy models for interview session, question, answer, and evaluation.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym

from app.db.base import Base


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(String(36), index=True)
    resume_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)
    job_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)

    # Physical column 'type' (e.g. 'technical', 'hr', 'mixed', 'pressure')
    # Synonym 'mode' for new API compatibility
    type: Mapped[str] = mapped_column(String(50))
    mode = synonym("type")

    # Candidate's targeted job role (e.g. 'Frontend Developer')
    role: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    difficulty: Mapped[int] = mapped_column(Integer, default=5)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="active")
    strategy: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    overall_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    questions: Mapped[list["InterviewQuestion"]] = relationship(
        "InterviewQuestion",
        back_populates="interview",
        order_by="InterviewQuestion.sequence_number",
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs):
        if "mode" in kwargs and "type" not in kwargs:
            kwargs["type"] = kwargs.pop("mode")
        super().__init__(**kwargs)


class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    interview_id: Mapped[UUID] = mapped_column(ForeignKey("interviews.id"), index=True)

    # Physical column 'question' | Synonym 'text'
    question: Mapped[str] = mapped_column(Text)
    text = synonym("question")

    # Physical column 'category' | Synonym 'question_type'
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    question_type = synonym("category")

    difficulty: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Physical column 'sequence_number' | Synonym 'order_index'
    sequence_number: Mapped[int] = mapped_column(Integer, default=0)
    order_index = synonym("sequence_number")

    # Text-to-speech generated question audio
    audio_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    asked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    interview: Mapped["Interview"] = relationship("Interview", back_populates="questions")
    answer: Mapped[Optional["InterviewAnswer"]] = relationship(
        "InterviewAnswer",
        back_populates="question",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs):
        if "text" in kwargs and "question" not in kwargs:
            kwargs["question"] = kwargs.pop("text")
        if "question_type" in kwargs and "category" not in kwargs:
            kwargs["category"] = kwargs.pop("question_type")
        if "order_index" in kwargs and "sequence_number" not in kwargs:
            kwargs["sequence_number"] = kwargs.pop("order_index")
        super().__init__(**kwargs)


class InterviewAnswer(Base):
    __tablename__ = "interview_answers"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    question_id: Mapped[UUID] = mapped_column(ForeignKey("interview_questions.id"), index=True)

    # Physical column 'transcript' | Synonym 'answer_text'
    transcript: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    answer_text = synonym("transcript")

    # Candidate spoken audio URL
    audio_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Evaluation fields
    score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    strengths: Mapped[list] = mapped_column(JSON, default=list)
    improvements: Mapped[list] = mapped_column(JSON, default=list)

    submitted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    question: Mapped["InterviewQuestion"] = relationship("InterviewQuestion", back_populates="answer")
    evaluation: Mapped[Optional["InterviewEvaluation"]] = relationship(
        "InterviewEvaluation",
        back_populates="answer",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __init__(self, **kwargs):
        if "answer_text" in kwargs and "transcript" not in kwargs:
            kwargs["transcript"] = kwargs.pop("answer_text")
        super().__init__(**kwargs)


class InterviewEvaluation(Base):
    __tablename__ = "interview_evaluations"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    answer_id: Mapped[UUID] = mapped_column(ForeignKey("interview_answers.id"), unique=True)
    relevance: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    technical_accuracy: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    clarity: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    feedback: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    answer: Mapped["InterviewAnswer"] = relationship("InterviewAnswer", back_populates="evaluation")
