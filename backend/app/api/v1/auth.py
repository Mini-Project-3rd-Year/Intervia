"""
backend/app/api/v1/auth.py
Phase 1 - Authentication routes.

All credential operations are delegated to Supabase Auth.
FastAPI never receives, stores, or processes user passwords beyond
forwarding them to the Supabase API.

Routes:
    POST /api/v1/auth/register  - Create user in Supabase Auth
    POST /api/v1/auth/login     - Sign in with email + password
    POST /api/v1/auth/refresh   - Refresh Supabase access token
    POST /api/v1/auth/logout    - Invalidate session in Supabase
    GET  /api/v1/auth/me        - Return current authenticated user
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from supabase import AuthApiError

from app.api.deps import get_current_user
from app.core.supabase_client import get_supabase_client
from app.schemas.user import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserRead,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


def _build_token_response(session, supabase_user) -> TokenResponse:
    """Build a TokenResponse from a Supabase session + user."""
    return TokenResponse(
        access_token=session.access_token,
        refresh_token=session.refresh_token,
        token_type="bearer",
        user=UserRead(
            id=str(supabase_user.id),
            email=supabase_user.email or "",
            full_name=(supabase_user.user_metadata or {}).get("full_name"),
        ),
    )


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a user in Supabase Auth and returns access + refresh tokens.",
)
async def register(payload: RegisterRequest) -> TokenResponse:
    """
    POST /api/v1/auth/register

    Delegates user creation entirely to Supabase Auth.
    Passwords are forwarded directly and never stored by FastAPI.
    """
    client = get_supabase_client()
    try:
        response = client.auth.sign_up(
            {
                "email": payload.email,
                "password": payload.password,
                "options": {
                    "data": {"full_name": payload.full_name}
                },
            }
        )
    except AuthApiError as exc:
        logger.warning("Registration failed for %s: %s", payload.email, exc.message)
        # Map common Supabase errors to clean HTTP responses
        if "already registered" in exc.message.lower() or "already been registered" in exc.message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists.",
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed. Please check your details and try again.",
        ) from exc

    if response.session is None:
        # Email confirmation is enabled in Supabase — user must confirm email first
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="Registration successful. Please check your email to confirm your account.",
        )

    return _build_token_response(response.session, response.user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with email and password",
    description="Authenticates via Supabase Auth. Returns access + refresh tokens.",
)
async def login(payload: LoginRequest) -> TokenResponse:
    """
    POST /api/v1/auth/login

    Verifies credentials via Supabase Auth sign_in_with_password.
    Returns Supabase-issued JWT — no local tokens created.
    """
    client = get_supabase_client()
    try:
        response = client.auth.sign_in_with_password(
            {"email": payload.email, "password": payload.password}
        )
    except AuthApiError as exc:
        logger.warning("Login failed for %s: %s", payload.email, exc.message)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if response.session is None or response.user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login failed.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return _build_token_response(response.session, response.user)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Exchanges a valid Supabase refresh token for a new access token.",
)
async def refresh_token(payload: RefreshRequest) -> TokenResponse:
    """
    POST /api/v1/auth/refresh

    Uses the Supabase refresh token to issue a new access token.
    """
    client = get_supabase_client()
    try:
        response = client.auth.refresh_session(payload.refresh_token)
    except AuthApiError as exc:
        logger.warning("Token refresh failed: %s", exc.message)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    if response.session is None or response.user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return _build_token_response(response.session, response.user)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout current user",
    description="Invalidates the Supabase session. The client must discard stored tokens.",
)
async def logout(current_user: UserRead = Depends(get_current_user)) -> None:
    """
    POST /api/v1/auth/logout

    Signs out the user in Supabase Auth, invalidating the session server-side.
    """
    client = get_supabase_client()
    try:
        client.auth.sign_out()
    except AuthApiError as exc:
        logger.warning("Logout error for user %s: %s", current_user.id, exc.message)
        # Logout is best-effort; don't fail the client even if Supabase call fails.


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current authenticated user",
    description=(
        "Protected endpoint. Returns the Supabase identity of the authenticated user. "
        "Requires Authorization: Bearer <access_token>."
    ),
)
async def get_me(current_user: UserRead = Depends(get_current_user)) -> UserRead:
    """
    GET /api/v1/auth/me

    Returns the authenticated user's identity. Used to:
    - Verify a token is valid (200 = valid, 401 = invalid/expired)
    - Surface user info to the frontend after session restore
    """
    return current_user
