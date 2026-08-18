"""
backend/app/core/supabase_client.py
Supabase client singleton for Intervia backend.
Uses SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY from settings.
"""

from functools import lru_cache
from supabase import Client, create_client
from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """
    Return a cached Supabase client for backend use.
    Uses the SERVICE_ROLE_KEY to call admin Auth endpoints such as get_user.
    This client must never be exposed to the browser.
    """
    settings = get_settings()
    return create_client(
        supabase_url=settings.SUPABASE_URL,
        supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY,
    )
