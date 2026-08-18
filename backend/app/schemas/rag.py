"""
backend/app/schemas/rag.py
Phase 4 — Pydantic schemas for the RAG system.

CandidateProfile is the structured resume representation used throughout
the system. The RAG schemas describe indexing requests and retrieval responses.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Candidate profile schema (structured resume)
# ---------------------------------------------------------------------------

class WorkExperience(BaseModel):
    """One role / position entry from the resume."""
    company: str = ""
    role: str = ""
    duration: str = ""                          # e.g. "2021-01 – 2023-06"
    responsibilities: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)


class Project(BaseModel):
    """One project entry from the resume."""
    name: str = ""
    description: str = ""
    technologies: List[str] = Field(default_factory=list)
    contribution: str = ""
    impact: str = ""


class Education(BaseModel):
    """One education or certification entry."""
    institution: str = ""
    degree: str = ""
    field: str = ""
    year: str = ""
    is_certification: bool = False


class CandidateProfile(BaseModel):
    """
    Structured representation of a parsed resume.
    Produced by Phase 2 ResumeAgent and consumed by Phase 4 RAG.
    """
    user_id: str = ""
    resume_id: str = ""
    full_name: str = ""
    summary: str = ""
    skills: List[str] = Field(default_factory=list)
    experience: List[WorkExperience] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# RAG internal data model
# ---------------------------------------------------------------------------

class ResumeChunkData(BaseModel):
    """In-memory representation of a resume chunk (before DB persist)."""
    user_id: str
    resume_id: str
    chunk_text: str
    chunk_type: str                             # experience | skills | project | education | summary
    chunk_index: int
    embedding: Optional[List[float]] = None
    metadata_json: Dict[str, Any] = Field(default_factory=dict)


class RetrievedChunk(BaseModel):
    """One chunk returned from semantic retrieval, with similarity score."""
    id: str
    user_id: str
    resume_id: str
    chunk_text: str
    chunk_type: str
    chunk_index: int
    metadata_json: Dict[str, Any] = Field(default_factory=dict)
    similarity: float = 0.0


# ---------------------------------------------------------------------------
# API request/response schemas
# ---------------------------------------------------------------------------

class IndexResumeRequest(BaseModel):
    """Payload for POST /api/v1/rag/index."""
    resume_id: str = Field(..., description="Resume UUID to index.")
    profile: CandidateProfile


class RAGQueryRequest(BaseModel):
    """Payload for POST /api/v1/rag/retrieve."""
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(5, ge=1, le=20)
    resume_id: Optional[str] = None            # optional filter


class RAGRetrievalResponse(BaseModel):
    chunks: List[RetrievedChunk]
    total: int


class RAGIndexResponse(BaseModel):
    resume_id: str
    chunks_created: int
    status: str                                 # "indexed" | "failed"
    message: str = ""


class RAGTestResponse(BaseModel):
    """Response for GET /api/v1/rag/test (dev-only)."""
    query: str
    top_k: int
    chunks: List[RetrievedChunk]
