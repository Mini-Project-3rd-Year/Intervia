"""
backend/app/schemas/candidate_profile.py
Phase 4 — Minimal Pydantic schemas for the RAG chunker.

These schemas define the structured representation of a parsed resume.
Phase 2 (Resume Intelligence) will populate these from the resume agent output.
Phase 5 will persist them to the candidate_profiles table.

Usage:
    from app.schemas.candidate_profile import CandidateProfile
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# ── Work Experience ───────────────────────────────────────────────────────────

class WorkExperience(BaseModel):
    """A single entry in the candidate's work history."""

    company: str = Field(..., description="Company or organisation name")
    role: str = Field(..., description="Job title / role")
    start_date: str | None = Field(None, description="Start date, free-form string (e.g. 'Jan 2022')")
    end_date: str | None = Field(None, description="End date or 'Present'")
    location: str | None = Field(None)
    bullets: list[str] = Field(
        default_factory=list,
        description="Achievement/responsibility bullet points",
    )
    technologies: list[str] = Field(
        default_factory=list,
        description="Technologies / tools mentioned for this role",
    )

    @property
    def text(self) -> str:
        """Human-readable text suitable for embedding."""
        lines = [f"{self.role} at {self.company}"]
        if self.start_date or self.end_date:
            period = f"{self.start_date or '?'} – {self.end_date or 'Present'}"
            lines.append(period)
        if self.location:
            lines.append(self.location)
        lines.extend(self.bullets)
        if self.technologies:
            lines.append("Technologies: " + ", ".join(self.technologies))
        return "\n".join(lines)


# ── Project ───────────────────────────────────────────────────────────────────

class Project(BaseModel):
    """A project the candidate built or contributed to."""

    name: str
    description: str = ""
    technologies: list[str] = Field(default_factory=list)
    url: str | None = None
    bullets: list[str] = Field(default_factory=list)

    @property
    def text(self) -> str:
        lines = [f"Project: {self.name}"]
        if self.description:
            lines.append(self.description)
        lines.extend(self.bullets)
        if self.technologies:
            lines.append("Technologies: " + ", ".join(self.technologies))
        if self.url:
            lines.append(f"URL: {self.url}")
        return "\n".join(lines)


# ── Skill Group ───────────────────────────────────────────────────────────────

class SkillGroup(BaseModel):
    """
    A named group of skills (e.g. 'Programming Languages', 'Cloud Platforms').
    If no grouping exists in the resume, a single group named 'Skills' is used.
    """

    category: str = Field(..., description="Skill category name")
    skills: list[str] = Field(..., description="Individual skill names")

    @property
    def text(self) -> str:
        return f"{self.category}: {', '.join(self.skills)}"


# ── Education ─────────────────────────────────────────────────────────────────

class Education(BaseModel):
    institution: str
    degree: str | None = None
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    gpa: str | None = None

    @property
    def text(self) -> str:
        parts = []
        if self.degree and self.field_of_study:
            parts.append(f"{self.degree} in {self.field_of_study}")
        elif self.degree:
            parts.append(self.degree)
        parts.append(f"at {self.institution}")
        if self.start_date or self.end_date:
            parts.append(f"({self.start_date or '?'} – {self.end_date or 'Present'})")
        if self.gpa:
            parts.append(f"GPA: {self.gpa}")
        return " ".join(parts)


# ── Candidate Profile (root) ──────────────────────────────────────────────────

class CandidateProfile(BaseModel):
    """
    Structured representation of a parsed resume.

    Produced by the Resume Agent (Phase 2) and consumed by:
      - RAG chunker (Phase 4) → embeddings
      - Interview Planner (Phase 6) → interview strategy
      - Skill Verification Agent (Phase 10) → skill tests
    """

    # Identity
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin_url: str | None = None
    github_url: str | None = None
    summary: str | None = Field(
        None, description="Professional summary / objective statement"
    )

    # Structured sections
    experience: list[WorkExperience] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    skill_groups: list[SkillGroup] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)

    # Flat skill list (convenience — may be derived from skill_groups)
    skills: list[str] = Field(
        default_factory=list,
        description="Flat list of all skills (union of skill_groups)",
    )

    # Raw resume text (for fallback)
    raw_text: str | None = None

    # Arbitrary extra data from the resume agent
    extra: dict[str, Any] = Field(default_factory=dict)
