from collections.abc import AsyncIterator, Iterator
from sqlite3 import Connection, connect

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def test_db() -> Iterator[Connection]:
    connection = connect(":memory:")
    try:
        yield connection
    finally:
        connection.close()


@pytest_asyncio.fixture
async def test_client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def sample_user() -> dict[str, str]:
    return {"id": "user-1", "email": "candidate@example.com", "full_name": "Candidate"}


@pytest.fixture
def sample_resume() -> dict[str, str]:
    return {"id": "resume-1", "user_id": "user-1", "filename": "resume.pdf"}


@pytest.fixture
def sample_interview() -> dict[str, str]:
    return {"id": "interview-1", "user_id": "user-1", "status": "scheduled"}