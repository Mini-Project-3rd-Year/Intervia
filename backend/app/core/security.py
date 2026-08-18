"""
backend/app/core/security.py
Phase 1 - Supabase token validation.

Supabase owns all identity and credentials.
This module validates Supabase-issued access tokens via the Supabase API.
We do NOT create local JWTs or hash passwords here.
"""

import logging

from fastapi import HTTPException, status
from supabase import AuthApiError

from app.core.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)


def validate_supabase_token(token: str):
    """
    Validate a Supabase access token by calling supabase.auth.get_user().

    Args:
        token: The JWT access token issued by Supabase Auth.

    Returns:
        The authenticated Supabase User object.

    Raises:
        HTTPException 401: If the token is invalid, expired, or verification fails.
    """
    try:
        client = get_supabase_client()
        response = client.auth.get_user(token)
        if response is None or response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return response.user
    except AuthApiError as exc:
        logger.warning("Supabase auth validation failed: %s", exc.message)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unexpected error during token validation: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
