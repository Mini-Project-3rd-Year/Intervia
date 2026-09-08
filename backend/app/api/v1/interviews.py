"""Persisted interview lifecycle endpoints."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.core.sanitization import sanitize_text
from app.services.evaluation import score_answer
from app.models.features import Interview, InterviewAnswer, InterviewEvaluation, InterviewQuestion
from app.schemas.interview import (
    AnswerCreate,
    EvaluationRead,
    InterviewCreate,
    InterviewRead,
    QuestionRead,
)
from app.schemas.user import UserRead

router = APIRouter(prefix="/interviews", tags=["interviews"])


async def _owned_interview(interview_id: UUID, user_id: str, db: AsyncSession) -> Interview:
    interview = await db.scalar(
        select(Interview).where(Interview.id == interview_id, Interview.user_id == user_id)
    )
    if interview is None:
        raise HTTPException(status_code=404, detail="Interview not found.")
    return interview


@router.post("", response_model=InterviewRead, status_code=201)
async def create_interview(
    payload: InterviewCreate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Interview:
    interview = Interview(user_id=current_user.id, **payload.model_dump())
    db.add(interview)
    await db.commit()
    await db.refresh(interview)
    return interview


@router.get("", response_model=list[InterviewRead])
async def list_interviews(
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Interview]:
    result = await db.execute(
        select(Interview).where(Interview.user_id == current_user.id).order_by(Interview.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{interview_id}", response_model=InterviewRead)
async def get_interview(
    interview_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Interview:
    return await _owned_interview(interview_id, current_user.id, db)


@router.patch("/{interview_id}/start", response_model=InterviewRead)
async def start_interview(
    interview_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Interview:
    interview = await _owned_interview(interview_id, current_user.id, db)
    interview.status = "in_progress"
    interview.started_at = datetime.utcnow()
    await db.commit()
    await db.refresh(interview)
    return interview


@router.patch("/{interview_id}/end", response_model=InterviewRead)
async def end_interview(
    interview_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Interview:
    interview = await _owned_interview(interview_id, current_user.id, db)
    interview.status = "completed"
    interview.completed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(interview)
    return interview


@router.get("/{interview_id}/questions", response_model=list[QuestionRead])
async def list_questions(
    interview_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[InterviewQuestion]:
    await _owned_interview(interview_id, current_user.id, db)
    result = await db.execute(
        select(InterviewQuestion)
        .where(InterviewQuestion.interview_id == interview_id)
        .order_by(InterviewQuestion.sequence_number)
    )
    return list(result.scalars().all())


@router.post("/{interview_id}/answers", status_code=201)
async def submit_answer(
    interview_id: UUID,
    payload: AnswerCreate,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    await _owned_interview(interview_id, current_user.id, db)
    question = await db.scalar(
        select(InterviewQuestion)
        .where(InterviewQuestion.interview_id == interview_id)
        .order_by(InterviewQuestion.sequence_number.desc())
    )
    if question is None:
        raise HTTPException(status_code=400, detail="Interview has no question to answer.")
    answer = InterviewAnswer(
        question_id=question.id,
        transcript=sanitize_text(payload.transcript, max_length=20000),
        audio_url=payload.audio_url,
        duration_seconds=payload.duration_seconds,
    )
    db.add(answer)
    await db.commit()
    await db.refresh(answer)
    relevance, technical_accuracy, clarity, feedback = score_answer(answer.transcript or "")
    db.add(
        InterviewEvaluation(
            answer_id=answer.id,
            relevance=relevance,
            technical_accuracy=technical_accuracy,
            clarity=clarity,
            feedback=feedback,
        )
    )
    await db.commit()
    return {"status": "accepted", "answer_id": str(answer.id)}


@router.get("/{interview_id}/evaluation", response_model=list[EvaluationRead])
async def get_evaluation(
    interview_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[InterviewEvaluation]:
    await _owned_interview(interview_id, current_user.id, db)
    result = await db.execute(
        select(InterviewEvaluation)
        .join(InterviewAnswer, InterviewAnswer.id == InterviewEvaluation.answer_id)
        .join(InterviewQuestion, InterviewQuestion.id == InterviewAnswer.question_id)
        .where(InterviewQuestion.interview_id == interview_id)
    )
    return list(result.scalars().all())