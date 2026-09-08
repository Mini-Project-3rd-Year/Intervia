"""Authenticated WebSocket transport for live interview sessions."""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.agents.interviewer import interviewer_graph
from app.core.security import validate_supabase_token
from app.services.session_manager import InterviewState, session_manager

logger = logging.getLogger(__name__)
router = APIRouter(tags=["interview"])


def _user_id(user: object) -> str:
    return str(getattr(user, "id", ""))


async def _send_question(websocket: WebSocket, session: InterviewState) -> None:
    result = interviewer_graph.invoke(
        {
            "questions": session.questions,
            "question_index": session.question_index,
            "question": None,
            "complete": False,
        }
    )
    if result["complete"]:
        session.status = "completed"
        await websocket.send_json(
            {
                "type": "interview_end",
                "redirect": f"/results/{session.interview_id}",
            }
        )
        return

    question = result["question"]
    await websocket.send_json({"type": "question", **question})


@router.websocket("/ws/interview/{interview_id}")
async def interview_websocket(websocket: WebSocket, interview_id: str) -> None:
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="Authentication required")
        return

    try:
        user = validate_supabase_token(token)
    except Exception:
        await websocket.close(
            code=1008,
            reason="Invalid or expired authentication token",
        )
        return

    await websocket.accept()
    session = session_manager.get_session(interview_id)
    if session is None:
        session = session_manager.create_session(interview_id, _user_id(user))
    elif session.user_id != _user_id(user):
        await websocket.close(code=1008, reason="Interview access denied")
        return

    try:
        await _send_question(websocket, session)
        while session.status == "active":
            message = await websocket.receive_json()
            message_type = message.get("type")

            if message_type == "answer":
                text = message.get("text")
                if not isinstance(text, str) or not text.strip():
                    await websocket.send_json(
                        {"type": "error", "detail": "Answer text is required."}
                    )
                    continue

                session.answers.append(
                    {
                        "text": text,
                        "question_id": str(
                            message.get("question_id")
                            or session.questions[session.question_index]["question_id"]
                        ),
                    }
                )
                session.question_index += 1
                await _send_question(websocket, session)
            elif message_type == "audio_chunk":
                if not isinstance(message.get("data"), str):
                    await websocket.send_json(
                        {"type": "error", "detail": "Audio data is required."}
                    )
            else:
                await websocket.send_json(
                    {"type": "error", "detail": "Unsupported message type."}
                )
    except WebSocketDisconnect:
        logger.info("Interview WebSocket disconnected", extra={"interview_id": interview_id})
    except (json.JSONDecodeError, ValueError):
        await websocket.send_json({"type": "error", "detail": "Invalid JSON message."})
    finally:
        if session_manager.get_session(interview_id) is session:
            await session_manager.close_session(interview_id)