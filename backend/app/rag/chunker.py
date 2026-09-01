"""
backend/app/rag/chunker.py
Phase 4 — Resume Chunker

Converts a structured CandidateProfile into a list of text chunk dicts
ready for embedding and storage.

Chunking strategy:
  - One chunk per WorkExperience entry (role, company, bullets, technologies)
  - One chunk per SkillGroup (category + skill names)
  - One chunk per Project (name, description, bullets, technologies)
  - One chunk for education entries (combined)
  - One chunk for the professional summary (if present)

Each chunk is a dict with keys:
  - chunk_text: str          — the text to embed
  - chunk_type: str          — "experience" | "skills" | "projects" | "education" | "summary"
  - metadata_json: dict      — extra context (company, role, skill_category, etc.)
"""

from __future__ import annotations

from app.core.logging import get_logger
from app.schemas.candidate_profile import CandidateProfile

logger = get_logger()

# Minimum characters a chunk must have to be worth embedding.
_MIN_CHUNK_LENGTH = 10


def chunk_resume(profile: CandidateProfile) -> list[dict]:
    """
    Split a CandidateProfile into a flat list of text chunks.

    Args:
        profile: A structured CandidateProfile (from Resume Agent or fixture).

    Returns:
        List of chunk dicts, each with 'chunk_text', 'chunk_type',
        and 'metadata_json' keys.  Only non-empty chunks are included.
    """
    chunks: list[dict] = []

    # ── 1. Professional summary ───────────────────────────────────────────────
    if profile.summary and len(profile.summary.strip()) >= _MIN_CHUNK_LENGTH:
        chunks.append({
            "chunk_text": profile.summary.strip(),
            "chunk_type": "summary",
            "metadata_json": {
                "full_name": profile.full_name,
            },
        })
        logger.debug("Chunker: added summary chunk")

    # ── 2. Work experience — one chunk per entry ──────────────────────────────
    for idx, exp in enumerate(profile.experience):
        text = exp.text.strip()
        if len(text) < _MIN_CHUNK_LENGTH:
            continue
        chunks.append({
            "chunk_text": text,
            "chunk_type": "experience",
            "metadata_json": {
                "company": exp.company,
                "role": exp.role,
                "start_date": exp.start_date,
                "end_date": exp.end_date,
                "technologies": exp.technologies,
                "experience_index": idx,
            },
        })

    logger.debug("Chunker: added %d experience chunks", len(profile.experience))

    # ── 3. Skill groups — one chunk per group ─────────────────────────────────
    for group in profile.skill_groups:
        if not group.skills:
            continue
        text = group.text.strip()
        if len(text) < _MIN_CHUNK_LENGTH:
            continue
        chunks.append({
            "chunk_text": text,
            "chunk_type": "skills",
            "metadata_json": {
                "skill_category": group.category,
                "skills": group.skills,
            },
        })

    # Fallback: if no skill groups but flat skills list is present
    if not profile.skill_groups and profile.skills:
        skills_text = "Skills: " + ", ".join(profile.skills)
        chunks.append({
            "chunk_text": skills_text,
            "chunk_type": "skills",
            "metadata_json": {
                "skill_category": "General",
                "skills": profile.skills,
            },
        })

    logger.debug("Chunker: added %d skill chunks", len(profile.skill_groups) or (1 if profile.skills else 0))

    # ── 4. Projects — one chunk per project ───────────────────────────────────
    for idx, project in enumerate(profile.projects):
        text = project.text.strip()
        if len(text) < _MIN_CHUNK_LENGTH:
            continue
        chunks.append({
            "chunk_text": text,
            "chunk_type": "projects",
            "metadata_json": {
                "project_name": project.name,
                "technologies": project.technologies,
                "url": project.url,
                "project_index": idx,
            },
        })

    logger.debug("Chunker: added %d project chunks", len(profile.projects))

    # ── 5. Education — combined into one chunk ────────────────────────────────
    if profile.education:
        edu_lines = [edu.text for edu in profile.education if edu.text.strip()]
        if edu_lines:
            chunks.append({
                "chunk_text": "Education:\n" + "\n".join(edu_lines),
                "chunk_type": "education",
                "metadata_json": {
                    "institutions": [edu.institution for edu in profile.education],
                },
            })
        logger.debug("Chunker: added education chunk")

    logger.info(
        "Chunker: resume split into %d chunks",
        len(chunks),
        extra={
            "experience": sum(1 for c in chunks if c["chunk_type"] == "experience"),
            "skills": sum(1 for c in chunks if c["chunk_type"] == "skills"),
            "projects": sum(1 for c in chunks if c["chunk_type"] == "projects"),
            "education": sum(1 for c in chunks if c["chunk_type"] == "education"),
            "summary": sum(1 for c in chunks if c["chunk_type"] == "summary"),
        },
    )

    return chunks
