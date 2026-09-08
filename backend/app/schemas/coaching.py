from uuid import UUID

from pydantic import BaseModel


class CoachingPlanRead(BaseModel):
    interview_id: UUID
    overall_score: float
    strengths: list[str]
    focus_areas: list[str]
    next_steps: list[str]