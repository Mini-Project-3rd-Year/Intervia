"""Persisted coaching plan endpoint."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.api.v1.interviews import _owned_interview
from app.db.session import get_db
from app.models.features import Interview, InterviewAnswer, InterviewEvaluation, InterviewQuestion
from app.schemas.coaching import CoachingPlanRead
from app.schemas.user import UserRead

router = APIRouter(prefix="/coaching", tags=["coaching"])


@router.get("/{interview_id}/plan", response_model=CoachingPlanRead)
async def get_coaching_plan(
    interview_id: UUID,
    current_user: UserRead = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CoachingPlanRead:
    await _owned_interview(interview_id, current_user.id, db)
    result = await db.execute(
        select(InterviewEvaluation)
        .join(InterviewAnswer, InterviewAnswer.id == InterviewEvaluation.answer_id)
        .join(InterviewQuestion, InterviewQuestion.id == InterviewAnswer.question_id)
        .where(InterviewQuestion.interview_id == interview_id)
    )
    evaluations = list(result.scalars().all())
    overall_score = (
        sum(float(item.clarity) for item in evaluations) / len(evaluations)
        if evaluations
        else 0.0
    )
    focus_areas = ["Use specific examples", "Structure answers with situation, action, and result"]
    return CoachingPlanRead(
        interview_id=interview_id,
        overall_score=round(overall_score, 2),
        strengths=["Completed interview responses"],
        focus_areas=focus_areas,
        next_steps=["Practice one structured answer daily", "Review feedback after each session"],
    )