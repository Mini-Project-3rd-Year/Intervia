from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.main import app
from app.services.session_manager import SessionManager


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_websocket_rejects_missing_token(client: TestClient):
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws/interview/interview-1"):
            pass

    assert exc_info.value.code == 1008


def test_websocket_starts_and_advances_interview(client: TestClient):
    user = SimpleNamespace(id="user-1")
    with patch("app.api.v1.ws_interview.validate_supabase_token", return_value=user):
        with client.websocket_connect("/ws/interview/interview-2?token=valid") as websocket:
            first_question = websocket.receive_json()
            assert first_question["type"] == "question"
            assert first_question["question_id"] == "intro-1"

            websocket.send_json(
                {
                    "type": "answer",
                    "text": "I build reliable backend services.",
                    "question_id": first_question["question_id"],
                }
            )
            next_question = websocket.receive_json()

    assert next_question["type"] == "question"
    assert next_question["question_id"] == "behavioral-1"


def test_disconnect_persists_partial_session(client: TestClient):
    persisted = []

    async def persist(session):
        persisted.append(session)

    manager = SessionManager(persist_session=persist)
    user = SimpleNamespace(id="user-2")
    with patch("app.api.v1.ws_interview.session_manager", manager):
        with patch("app.api.v1.ws_interview.validate_supabase_token", return_value=user):
            with client.websocket_connect("/ws/interview/interview-3?token=valid") as websocket:
                websocket.receive_json()
                websocket.close()

    assert len(persisted) == 1
    assert persisted[0].interview_id == "interview-3"
    assert persisted[0].status == "closed"