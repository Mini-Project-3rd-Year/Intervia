from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from supabase import AuthApiError

from app.core.rate_limit import limiter
from app.core.file_validation import validate_pdf_bytes
from app.services.evaluation import score_answer
from app.main import app


def test_security_headers_and_request_id():
    with TestClient(app) as client:
        response = client.get("/api/v1/health", headers={"X-Request-ID": "request-123"})

    assert response.headers["X-Request-ID"] == "request-123"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]


def test_registration_name_is_sanitized():
    payload = {
        "email": "candidate@example.com",
        "password": "Password123!",
        "full_name": "<script>alert(1)</script> Candidate",
    }
    mock_response = MagicMock()
    mock_response.session = MagicMock(access_token="access", refresh_token="refresh")
    mock_response.user = MagicMock(
        id="user-1", email=payload["email"], user_metadata={"full_name": "Candidate"}
    )

    with patch("app.api.v1.auth.get_supabase_client") as mock_client:
        mock_client.return_value.auth.sign_up.return_value = mock_response
        with TestClient(app) as client:
            response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 201
    forwarded = mock_client.return_value.auth.sign_up.call_args.args[0]
    assert forwarded["options"]["data"]["full_name"] == "Candidate"


def test_auth_rate_limit_returns_429_after_ten_requests():
    limiter.reset()
    with patch("app.api.v1.auth.get_supabase_client") as mock_client:
        mock_client.return_value.auth.sign_in_with_password.side_effect = AuthApiError(
            message="Invalid login credentials", code=400, status=400
        )
        with TestClient(app) as client:
            responses = [
                client.post(
                    "/api/v1/auth/login",
                    json={"email": "candidate@example.com", "password": "Password123!"},
                )
                for _ in range(11)
            ]

    assert [response.status_code for response in responses[:10]] == [401] * 10
    assert responses[10].status_code == 429
    limiter.reset()


def test_executable_renamed_to_pdf_is_rejected():
    try:
        validate_pdf_bytes(b"MZ\x90\x00not a pdf", max_size_bytes=1024)
    except Exception as error:
        assert getattr(error, "status_code", None) == 400
    else:
        raise AssertionError("non-PDF content must be rejected")


def test_evaluation_service_scores_short_and_structured_answers():
    short = score_answer("Too short")
    structured = score_answer(
        "This answer explains the situation, action, and result clearly with measurable impact "
        "and context for the decision made by the candidate during the project, including "
        "tradeoffs, collaboration, implementation details, and the final business outcome."
    )

    assert short[0] < structured[0]
    assert short[3] != structured[3]