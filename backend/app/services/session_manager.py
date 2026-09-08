"""In-memory state management for active interview sessions."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field


@dataclass
class InterviewState:
    interview_id: str
    user_id: str
    question_index: int = 0
    questions: list[dict[str, object]] = field(default_factory=list)
    answers: list[dict[str, str]] = field(default_factory=list)
    status: str = "active"


PersistSession = Callable[[InterviewState], Awaitable[None] | None]


class SessionManager:
    def __init__(self, persist_session: PersistSession | None = None) -> None:
        self._sessions: dict[str, InterviewState] = {}
        self._persist_session = persist_session

    def create_session(
        self,
        interview_id: str,
        user_id: str,
        questions: list[dict[str, object]] | None = None,
    ) -> InterviewState:
        session = InterviewState(
            interview_id=interview_id,
            user_id=user_id,
            questions=questions or default_questions(),
        )
        self._sessions[interview_id] = session
        return session

    def get_session(self, interview_id: str) -> InterviewState | None:
        return self._sessions.get(interview_id)

    async def close_session(self, interview_id: str) -> InterviewState | None:
        session = self._sessions.pop(interview_id, None)
        if session is None:
            return None

        session.status = "closed"
        if self._persist_session is not None:
            result = self._persist_session(session)
            if result is not None:
                await result
        return session


def default_questions() -> list[dict[str, object]]:
    return [
        {
            "text": "Tell me about yourself and your recent experience.",
            "question_id": "intro-1",
            "section": "introduction",
            "difficulty": 5,
        },
        {
            "text": "What is a challenging problem you solved, and how did you approach it?",
            "question_id": "behavioral-1",
            "section": "behavioral",
            "difficulty": 5,
        },
    ]


session_manager = SessionManager()