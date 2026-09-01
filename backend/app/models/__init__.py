"""
backend/app/models/__init__.py
SQLAlchemy ORM model registry.

Import all models here so that:
  1. Alembic's autogenerate can detect them via Base.metadata
  2. Application code has a single import location

Phase 4: ResumeChunk added
Phase 5: User, Resume, CandidateProfile, etc. will be added
"""

from app.models.resume_chunk import ResumeChunk

__all__ = [
    "ResumeChunk",
]
