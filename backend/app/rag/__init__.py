"""
backend/app/rag/__init__.py
Phase 4 — RAG System

Public API for the RAG (Retrieval-Augmented Generation) pipeline.

Modules:
    embedder    — embed_text(), embed_batch()
    chunker     — chunk_resume()
    retriever   — retrieve_resume_context()
    rag_service — embed_and_store_resume(), delete_resume_chunks()
"""

from app.rag.chunker import chunk_resume
from app.rag.embedder import embed_batch, embed_text
from app.rag.rag_service import delete_resume_chunks, embed_and_store_resume
from app.rag.retriever import retrieve_resume_context

__all__ = [
    "chunk_resume",
    "embed_text",
    "embed_batch",
    "retrieve_resume_context",
    "embed_and_store_resume",
    "delete_resume_chunks",
]
