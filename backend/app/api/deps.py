"""
backend/app/api/deps.py
Phase 1 - FastAPI dependencies for authentication.

get_current_user() is the standard dependency injected into every
protected endpoint. It validates the Supabase Bearer token and returns
a UserRead containing the Supabase user id, email, and full_name.

Usage in any protected route:
    @router.get("/protected")
    async def protected(current_user: UserRead = Depends(get_current_user)):
        # current_user.id scopes all DB queries
        ...
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import validate_supabase_token
from app.schemas.user import UserRead

# OAuth2 Bearer scheme — expects 'Authorization: Bearer <token>'
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> UserRead:
    """
    FastAPI dependency: validate the Supabase Bearer token and return UserRead.

    Raises HTTPException 401 when:
    - No Authorization header is present
    - Token is invalid or expired
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Provide 'Authorization: Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    supabase_user = validate_supabase_token(credentials.credentials)

    return UserRead(
        id=str(supabase_user.id),
        email=supabase_user.email or "",
        full_name=(supabase_user.user_metadata or {}).get("full_name"),
    )
