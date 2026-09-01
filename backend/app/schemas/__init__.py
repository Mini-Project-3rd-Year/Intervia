"""schemas/__init__.py — Pydantic request/response schemas"""

from app.schemas.candidate_profile import (
    CandidateProfile,
    Education,
    Project,
    SkillGroup,
    WorkExperience,
)

__all__ = [
    "CandidateProfile",
    "WorkExperience",
    "Project",
    "SkillGroup",
    "Education",
]
