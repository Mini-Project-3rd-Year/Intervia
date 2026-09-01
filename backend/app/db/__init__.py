"""
backend/app/db/__init__.py
Phase 4 — Database layer activated for RAG system.
Phase 5 will complete the full schema with all core tables.
"""

from app.db.session import Base, engine, get_db

__all__ = ["Base", "engine", "get_db"]
