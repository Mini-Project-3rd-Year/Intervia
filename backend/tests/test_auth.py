"""
backend/tests/test_auth.py
Phase 1 - Authentication endpoint tests.

All Supabase calls are mocked with unittest.mock.patch.
Tests run without a real Supabase project.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

# ---------------------------------------------------------------------------
# Helpers — build mock Supabase objects
# ---------------------------------------------------------------------------

def _mock_user(
    uid: str = "test-uuid-1234",
    email: str = "test@example.com",
    full_name: str = "Test User",
):
    user = MagicMock()
    user.id = uid
    user.email = email
    user.user_metadata = {"full_name": full_name}
    return user


def _mock_session(access_token: str = "mock-access-token", refresh_token: str = "mock-refresh-token"):
    session = MagicMock()
    session.access_token = access_token
    session.refresh_token = refresh_token
    return session


def _mock_auth_response(user=None, session=None):
    resp = MagicMock()
    resp.user = user or _mock_user()
    resp.session = session or _mock_session()
    return resp


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    """Synchronous test client for FastAPI."""
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Register tests
# ---------------------------------------------------------------------------

class TestRegister:

    def test_register_success(self, client: TestClient):
        """Valid registration returns 201 with access_token, refresh_token, and user."""
        mock_resp = _mock_auth_response()
        with patch("app.api.v1.auth.get_supabase_client") as mock_sb:
            mock_sb.return_value.auth.sign_up.return_value = mock_resp

            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": "test@example.com",
                    "password": "Test1234!",
                    "full_name": "Test User",
                },
            )

        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "test@example.com"
        assert data["user"]["id"] == "test-uuid-1234"

    def test_register_duplicate_email(self, client: TestClient):
        """Duplicate email registration returns 400."""
        from supabase import AuthApiError

        with patch("app.api.v1.auth.get_supabase_client") as mock_sb:
            mock_sb.return_value.auth.sign_up.side_effect = AuthApiError(
                message="User already registered", code=400, status=400
            )

            response = client.post(
                "/api/v1/auth/register",
                json={
                    "email": "existing@example.com",
                    "password": "Test1234!",
                    "full_name": "Existing User",
                },
            )

        assert response.status_code == 400

    def test_register_missing_fields(self, client: TestClient):
        """Registration without required fields returns 422."""
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com"},  # missing password + full_name
        )
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# Login tests
# ---------------------------------------------------------------------------

class TestLogin:

    def test_login_success(self, client: TestClient):
        """Valid credentials return 200 with the same TokenResponse shape."""
        mock_resp = _mock_auth_response()
        with patch("app.api.v1.auth.get_supabase_client") as mock_sb:
            mock_sb.return_value.auth.sign_in_with_password.return_value = mock_resp

            response = client.post(
                "/api/v1/auth/login",
                json={"email": "test@example.com", "password": "Test1234!"},
            )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "test@example.com"

    def test_login_wrong_password(self, client: TestClient):
        """Wrong credentials return 401."""
        from supabase import AuthApiError

        with patch("app.api.v1.auth.get_supabase_client") as mock_sb:
            mock_sb.return_value.auth.sign_in_with_password.side_effect = AuthApiError(
                message="Invalid login credentials", code=400, status=400
            )

            response = client.post(
                "/api/v1/auth/login",
                json={"email": "test@example.com", "password": "WrongPass!"},
            )

        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Refresh test
# ---------------------------------------------------------------------------

class TestRefresh:

    def test_refresh_token(self, client: TestClient):
        """Valid refresh token returns a new access token."""
        mock_resp = _mock_auth_response(
            session=_mock_session(access_token="new-access-token")
        )
        with patch("app.api.v1.auth.get_supabase_client") as mock_sb:
            mock_sb.return_value.auth.refresh_session.return_value = mock_resp

            response = client.post(
                "/api/v1/auth/refresh",
                json={"refresh_token": "mock-refresh-token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == "new-access-token"


# ---------------------------------------------------------------------------
# /auth/me tests
# ---------------------------------------------------------------------------

class TestMe:

    def test_me_no_token(self, client: TestClient):
        """Request without Authorization header returns 401."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_me_valid_token(self, client: TestClient):
        """Valid token returns 200 with user id, email, and full_name."""
        mock_user = _mock_user()
        mock_get_user = MagicMock()
        mock_get_user.user = mock_user

        with patch("app.core.security.get_supabase_client") as mock_sb:
            mock_sb.return_value.auth.get_user.return_value = mock_get_user

            response = client.get(
                "/api/v1/auth/me",
                headers={"Authorization": "Bearer mock-access-token"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-uuid-1234"
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
