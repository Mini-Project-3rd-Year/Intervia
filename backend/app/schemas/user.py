"""
backend/app/schemas/user.py
Phase 1 - Pydantic schemas for authentication.

UserRead is the safe public representation of a Supabase user.
It must never expose passwords, tokens, or internal secrets.
"""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.core.sanitization import sanitize_text


class UserRead(BaseModel):
    """Safe public representation of an authenticated user.
    Built from the Supabase Auth User object.
    Never exposes passwords, tokens, or secrets.
    """
    id: str = Field(..., description="Supabase user UUID — used to scope all application data.")
    email: str = Field(..., description="User email address.")
    full_name: str | None = Field(None, description="Display name from Supabase user_metadata.")

    model_config = {"from_attributes": True}


class RegisterRequest(BaseModel):
    """Payload for POST /api/v1/auth/register."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters.")
    full_name: str = Field(..., min_length=1, max_length=100)

    @model_validator(mode="after")
    def sanitize_full_name(self) -> "RegisterRequest":
        self.full_name = sanitize_text(self.full_name, max_length=100)
        if not self.full_name:
            raise ValueError("full_name must contain text")
        return self


class LoginRequest(BaseModel):
    """Payload for POST /api/v1/auth/login."""
    email: EmailStr
    password: str = Field(..., min_length=1)


class RefreshRequest(BaseModel):
    """Payload for POST /api/v1/auth/refresh."""
    refresh_token: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Response returned after successful register or login."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserRead
