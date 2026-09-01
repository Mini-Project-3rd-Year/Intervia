"""
backend/tests/test_rag.py
Phase 4 — RAG System Tests

Test strategy:
  - Unit tests for chunk_resume() — no DB, no embedding calls
  - Unit tests for embed_text() / embed_batch() with mocked API clients
  - Integration-style tests for embed_and_store_resume() with mocked embedder
  - Integration-style tests for retrieve_resume_context() with mocked embedder

All external API calls (Google / OpenAI) are replaced with unittest.mock
so tests run without any API keys or live DB connection.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.rag.chunker import chunk_resume
from app.schemas.candidate_profile import (
    CandidateProfile,
    Education,
    Project,
    SkillGroup,
    WorkExperience,
)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture()
def sample_profile() -> CandidateProfile:
    """A realistic CandidateProfile for testing."""
    return CandidateProfile(
        full_name="Jane Doe",
        email="jane@example.com",
        summary=(
            "Software engineer with 5 years of experience building "
            "distributed systems in Python and Go."
        ),
        experience=[
            WorkExperience(
                company="Acme Corp",
                role="Senior Backend Engineer",
                start_date="Jan 2021",
                end_date="Present",
                bullets=[
                    "Designed Kubernetes-based microservices platform serving 10M req/day",
                    "Reduced infrastructure costs by 30% via autoscaling",
                ],
                technologies=["Python", "Kubernetes", "gRPC", "PostgreSQL"],
            ),
            WorkExperience(
                company="StartupXYZ",
                role="Software Engineer",
                start_date="Jun 2019",
                end_date="Dec 2020",
                bullets=[
                    "Built REST APIs using FastAPI and PostgreSQL",
                    "Implemented CI/CD pipeline with GitHub Actions",
                ],
                technologies=["Python", "FastAPI", "PostgreSQL", "Docker"],
            ),
        ],
        skill_groups=[
            SkillGroup(
                category="Programming Languages",
                skills=["Python", "Go", "TypeScript"],
            ),
            SkillGroup(
                category="Cloud & DevOps",
                skills=["AWS", "Kubernetes", "Docker", "Terraform"],
            ),
        ],
        projects=[
            Project(
                name="OpenMetrics",
                description="Open-source observability library for Python microservices",
                technologies=["Python", "Prometheus", "Grafana"],
                bullets=["2k GitHub stars", "Used in production at 10+ companies"],
            ),
        ],
        education=[
            Education(
                institution="State University",
                degree="B.Sc.",
                field_of_study="Computer Science",
                start_date="2015",
                end_date="2019",
                gpa="3.8",
            ),
        ],
    )


@pytest.fixture()
def empty_profile() -> CandidateProfile:
    """A minimal profile with only flat skills (no groups)."""
    return CandidateProfile(
        full_name="John Smith",
        skills=["Python", "SQL"],
    )


# ─────────────────────────────────────────────────────────────────────────────
# Chunker tests — pure Python, no mocks needed
# ─────────────────────────────────────────────────────────────────────────────

class TestChunkResume:
    """Tests for app.rag.chunker.chunk_resume()"""

    def test_returns_list_of_dicts(self, sample_profile: CandidateProfile):
        chunks = chunk_resume(sample_profile)
        assert isinstance(chunks, list)
        assert all(isinstance(c, dict) for c in chunks)

    def test_required_keys_present(self, sample_profile: CandidateProfile):
        chunks = chunk_resume(sample_profile)
        for chunk in chunks:
            assert "chunk_text" in chunk
            assert "chunk_type" in chunk
            assert "metadata_json" in chunk

    def test_chunk_types_are_valid(self, sample_profile: CandidateProfile):
        valid_types = {"experience", "skills", "projects", "education", "summary"}
        chunks = chunk_resume(sample_profile)
        for chunk in chunks:
            assert chunk["chunk_type"] in valid_types

    def test_experience_chunks_count(self, sample_profile: CandidateProfile):
        """Should produce one chunk per WorkExperience entry."""
        chunks = chunk_resume(sample_profile)
        experience_chunks = [c for c in chunks if c["chunk_type"] == "experience"]
        assert len(experience_chunks) == len(sample_profile.experience)

    def test_skill_chunks_count(self, sample_profile: CandidateProfile):
        """Should produce one chunk per SkillGroup."""
        chunks = chunk_resume(sample_profile)
        skill_chunks = [c for c in chunks if c["chunk_type"] == "skills"]
        assert len(skill_chunks) == len(sample_profile.skill_groups)

    def test_project_chunks_count(self, sample_profile: CandidateProfile):
        """Should produce one chunk per Project."""
        chunks = chunk_resume(sample_profile)
        project_chunks = [c for c in chunks if c["chunk_type"] == "projects"]
        assert len(project_chunks) == len(sample_profile.projects)

    def test_education_chunk_present(self, sample_profile: CandidateProfile):
        """Should produce exactly one education chunk (combined)."""
        chunks = chunk_resume(sample_profile)
        edu_chunks = [c for c in chunks if c["chunk_type"] == "education"]
        assert len(edu_chunks) == 1

    def test_summary_chunk_present(self, sample_profile: CandidateProfile):
        """Should include a summary chunk when profile.summary is set."""
        chunks = chunk_resume(sample_profile)
        summary_chunks = [c for c in chunks if c["chunk_type"] == "summary"]
        assert len(summary_chunks) == 1
        assert "Python" in summary_chunks[0]["chunk_text"]

    def test_no_summary_chunk_when_absent(self, empty_profile: CandidateProfile):
        """Should not include a summary chunk if profile.summary is None."""
        chunks = chunk_resume(empty_profile)
        assert not any(c["chunk_type"] == "summary" for c in chunks)

    def test_flat_skills_fallback(self, empty_profile: CandidateProfile):
        """When no skill_groups, flat skills list should produce one skills chunk."""
        chunks = chunk_resume(empty_profile)
        skill_chunks = [c for c in chunks if c["chunk_type"] == "skills"]
        assert len(skill_chunks) == 1
        assert "Python" in skill_chunks[0]["chunk_text"]
        assert "SQL" in skill_chunks[0]["chunk_text"]

    def test_chunk_text_is_non_empty(self, sample_profile: CandidateProfile):
        """Every chunk must have non-empty chunk_text."""
        chunks = chunk_resume(sample_profile)
        for chunk in chunks:
            assert chunk["chunk_text"].strip(), f"Empty chunk_text: {chunk}"

    def test_experience_metadata_contains_company(self, sample_profile: CandidateProfile):
        chunks = chunk_resume(sample_profile)
        exp_chunks = [c for c in chunks if c["chunk_type"] == "experience"]
        companies = [c["metadata_json"]["company"] for c in exp_chunks]
        assert "Acme Corp" in companies
        assert "StartupXYZ" in companies

    def test_experience_text_contains_technologies(self, sample_profile: CandidateProfile):
        chunks = chunk_resume(sample_profile)
        exp_chunks = [c for c in chunks if c["chunk_type"] == "experience"]
        acme_chunk = next(c for c in exp_chunks if c["metadata_json"]["company"] == "Acme Corp")
        assert "Kubernetes" in acme_chunk["chunk_text"]

    def test_project_metadata_contains_name(self, sample_profile: CandidateProfile):
        chunks = chunk_resume(sample_profile)
        proj_chunks = [c for c in chunks if c["chunk_type"] == "projects"]
        names = [c["metadata_json"]["project_name"] for c in proj_chunks]
        assert "OpenMetrics" in names

    def test_empty_profile_produces_at_least_skills_chunk(self, empty_profile):
        chunks = chunk_resume(empty_profile)
        assert len(chunks) >= 1

    def test_fully_empty_profile(self):
        """A completely empty CandidateProfile should produce 0 chunks."""
        chunks = chunk_resume(CandidateProfile())
        assert chunks == []


# ─────────────────────────────────────────────────────────────────────────────
# CandidateProfile schema tests
# ─────────────────────────────────────────────────────────────────────────────

class TestCandidateProfileSchema:
    def test_work_experience_text(self):
        exp = WorkExperience(
            company="Google",
            role="Staff SWE",
            start_date="2020",
            end_date="Present",
            bullets=["Led team of 10"],
            technologies=["Python", "Go"],
        )
        text = exp.text
        assert "Google" in text
        assert "Staff SWE" in text
        assert "Led team of 10" in text
        assert "Python" in text

    def test_project_text(self):
        proj = Project(
            name="MyApp",
            description="A cool app",
            technologies=["React", "FastAPI"],
            bullets=["100k users"],
        )
        assert "MyApp" in proj.text
        assert "React" in proj.text
        assert "100k users" in proj.text

    def test_skill_group_text(self):
        sg = SkillGroup(category="Backend", skills=["Python", "Java"])
        assert "Backend" in sg.text
        assert "Python" in sg.text

    def test_education_text(self):
        edu = Education(
            institution="MIT",
            degree="M.Sc.",
            field_of_study="AI",
            start_date="2020",
            end_date="2022",
        )
        assert "MIT" in edu.text
        assert "AI" in edu.text


# ─────────────────────────────────────────────────────────────────────────────
# Embedder tests — with mocked API clients
# ─────────────────────────────────────────────────────────────────────────────

FAKE_EMBEDDING = [0.1] * 768  # 768-dim fake vector


class TestEmbedder:
    """Tests for app.rag.embedder — external API calls are mocked."""

    @pytest.mark.asyncio
    async def test_embed_text_returns_list_of_floats(self):
        """embed_text() should return a list of floats of length EMBEDDING_DIMENSION."""
        with patch("app.rag.embedder.settings") as mock_settings, \
             patch("app.rag.embedder._embed_google_sync", return_value=[FAKE_EMBEDDING]):
            mock_settings.LLM_PROVIDER = "gemini"
            mock_settings.EMBEDDING_DIMENSION = 768
            mock_settings.GEMINI_API_KEY = "fake-key"

            from app.rag.embedder import embed_text
            result = await embed_text("Hello world")

        assert isinstance(result, list)
        assert len(result) == 768
        assert all(isinstance(v, float) for v in result)

    @pytest.mark.asyncio
    async def test_embed_batch_returns_one_per_input(self):
        """embed_batch() should return one embedding per input text."""
        fake_batch = [FAKE_EMBEDDING, FAKE_EMBEDDING, FAKE_EMBEDDING]
        with patch("app.rag.embedder.settings") as mock_settings, \
             patch("app.rag.embedder._embed_google_sync", return_value=fake_batch):
            mock_settings.LLM_PROVIDER = "gemini"
            mock_settings.EMBEDDING_DIMENSION = 768
            mock_settings.GEMINI_API_KEY = "fake-key"

            from app.rag.embedder import embed_batch
            result = await embed_batch(["text1", "text2", "text3"])

        assert len(result) == 3
        assert all(len(e) == 768 for e in result)

    @pytest.mark.asyncio
    async def test_embed_batch_raises_on_empty_input(self):
        """embed_batch([]) should raise ValueError."""
        from app.rag.embedder import embed_batch

        with pytest.raises(ValueError, match="empty list"):
            await embed_batch([])

    @pytest.mark.asyncio
    async def test_embed_text_unsupported_provider(self):
        """embed_text() should raise ValueError for unknown providers."""
        with patch("app.rag.embedder.settings") as mock_settings:
            mock_settings.LLM_PROVIDER = "anthropic"
            mock_settings.EMBEDDING_DIMENSION = 768

            from app.rag.embedder import embed_batch

            with pytest.raises(ValueError, match="Unsupported LLM_PROVIDER"):
                await embed_batch(["text"])


# ─────────────────────────────────────────────────────────────────────────────
# RAG service tests — with mocked embedder + in-memory DB
# ─────────────────────────────────────────────────────────────────────────────

class TestEmbedAndStoreResume:
    """Tests for app.rag.rag_service.embed_and_store_resume()"""

    @pytest.mark.asyncio
    async def test_raises_when_no_chunks(self):
        """Should raise ValueError if the profile produces no chunks."""
        from app.rag.rag_service import embed_and_store_resume

        empty_profile = CandidateProfile()  # all empty
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock()
        mock_db.flush = AsyncMock()

        with patch("app.rag.rag_service.chunk_resume", return_value=[]):
            with pytest.raises(ValueError, match="No chunks"):
                await embed_and_store_resume(
                    user_id=str(uuid.uuid4()),
                    resume_id=str(uuid.uuid4()),
                    profile=empty_profile,
                    db=mock_db,
                )

    @pytest.mark.asyncio
    async def test_stores_correct_number_of_chunks(self, sample_profile: CandidateProfile):
        """Should persist one ResumeChunk row per chunk returned by chunker."""
        from app.rag.rag_service import embed_and_store_resume

        chunks = chunk_resume(sample_profile)
        fake_embeddings = [FAKE_EMBEDDING] * len(chunks)

        mock_db = AsyncMock()
        mock_db.add = MagicMock()  # sync
        mock_db.execute = AsyncMock()
        mock_db.flush = AsyncMock()

        with patch("app.rag.rag_service.embed_batch", return_value=fake_embeddings):
            result = await embed_and_store_resume(
                user_id=str(uuid.uuid4()),
                resume_id=str(uuid.uuid4()),
                profile=sample_profile,
                db=mock_db,
            )

        assert len(result) == len(chunks)
        assert mock_db.add.call_count == len(chunks)

    @pytest.mark.asyncio
    async def test_chunk_types_match_profile(self, sample_profile: CandidateProfile):
        """Each stored chunk should have the correct chunk_type."""
        from app.rag.rag_service import embed_and_store_resume

        expected_chunks = chunk_resume(sample_profile)
        fake_embeddings = [FAKE_EMBEDDING] * len(expected_chunks)

        mock_db = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.execute = AsyncMock()
        mock_db.flush = AsyncMock()

        with patch("app.rag.rag_service.embed_batch", return_value=fake_embeddings):
            result = await embed_and_store_resume(
                user_id=str(uuid.uuid4()),
                resume_id=str(uuid.uuid4()),
                profile=sample_profile,
                db=mock_db,
            )

        result_types = {c.chunk_type for c in result}
        assert "experience" in result_types
        assert "skills" in result_types

    @pytest.mark.asyncio
    async def test_user_id_is_set_on_all_chunks(self, sample_profile: CandidateProfile):
        """All stored chunks should have the correct user_id."""
        from app.rag.rag_service import embed_and_store_resume

        user_id = uuid.uuid4()
        expected_chunks = chunk_resume(sample_profile)
        fake_embeddings = [FAKE_EMBEDDING] * len(expected_chunks)

        mock_db = AsyncMock()
        mock_db.add = MagicMock()
        mock_db.execute = AsyncMock()
        mock_db.flush = AsyncMock()

        with patch("app.rag.rag_service.embed_batch", return_value=fake_embeddings):
            result = await embed_and_store_resume(
                user_id=str(user_id),
                resume_id=str(uuid.uuid4()),
                profile=sample_profile,
                db=mock_db,
            )

        for chunk in result:
            assert chunk.user_id == user_id


# ─────────────────────────────────────────────────────────────────────────────
# RAG API endpoint tests
# ─────────────────────────────────────────────────────────────────────────────

class TestRagEndpoint:
    """Tests for GET /api/v1/rag/test"""

    @pytest.fixture()
    def client(self):
        from fastapi.testclient import TestClient

        from app.main import app

        with TestClient(app) as c:
            yield c

    def test_endpoint_returns_403_in_production(self, client):
        """The debug endpoint should return 403 when DEBUG=false."""
        with patch("app.api.v1.rag.settings") as mock_settings:
            mock_settings.DEBUG = False
            response = client.get(
                "/api/v1/rag/test",
                params={"user_id": str(uuid.uuid4()), "query": "Python"},
            )
        assert response.status_code == 403

    def test_endpoint_requires_user_id(self, client):
        """Missing user_id should return 422."""
        response = client.get("/api/v1/rag/test", params={"query": "Python"})
        assert response.status_code == 422

    def test_endpoint_requires_query(self, client):
        """Missing query should return 422."""
        response = client.get(
            "/api/v1/rag/test",
            params={"user_id": str(uuid.uuid4())},
        )
        assert response.status_code == 422

    def test_endpoint_returns_structured_response(self, client):
        """With mocked retrieval, response should match RagTestResponse schema."""
        from app.models.resume_chunk import ResumeChunk as RC

        fake_chunk = RC(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            resume_id=uuid.uuid4(),
            chunk_text="Python and Kubernetes experience at Acme Corp",
            chunk_type="experience",
            embedding=FAKE_EMBEDDING,
            metadata_json={"company": "Acme Corp"},
        )

        uid = str(uuid.uuid4())

        with patch("app.api.v1.rag.retrieve_resume_context", new_callable=AsyncMock) as mock_retrieve, \
             patch("app.api.v1.rag.settings") as mock_settings:
            mock_settings.DEBUG = True
            mock_retrieve.return_value = [fake_chunk]

            response = client.get(
                "/api/v1/rag/test",
                params={"user_id": uid, "query": "Python experience", "top_k": 1},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "Python experience"
        assert data["user_id"] == uid
        assert data["returned"] == 1
        assert len(data["chunks"]) == 1
        assert data["chunks"][0]["chunk_type"] == "experience"
        assert "Python" in data["chunks"][0]["chunk_text"]
