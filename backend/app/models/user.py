"""
backend/app/models/user.py
Phase 1 stub — User model placeholder.

The Supabase Auth user is the identity source for Phase 1.
A local user_profiles table will be added in Phase 5 (Database) with:
    - id (UUID PK)
    - supabase_user_id (FK → Supabase Auth UUID)
    - full_name
    - created_at / updated_at

Supabase owns identity; FastAPI/Postgres owns application data.
"""

# Phase 5 will activate SQLAlchemy models.
# from sqlalchemy import Column, DateTime, String
# from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy.orm import DeclarativeBase
# import uuid, datetime

# class UserProfile(Base):
#     __tablename__ = "user_profiles"
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     supabase_user_id = Column(String, unique=True, nullable=False, index=True)
#     full_name = Column(String(100), nullable=True)
#     created_at = Column(DateTime, default=datetime.datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
