import json
import uuid
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import MagicMock
from zipfile import ZIP_DEFLATED, ZipFile

import pytest
from docx import Document
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pypdf import PdfWriter
from pypdf.generic import (
    DecodedStreamObject,
    DictionaryObject,
    NameObject,
)

from app.api.deps import get_current_user
from app.api.v1 import resumes as resume_api
from app.core.file_validation import (
    DOCX_MIME_TYPE,
    detect_resume_mime_type,
    validate_resume_bytes,
)
from app.core import file_validation
from app.db.session import get_db
from app.main import app
from app.models.features import Resume
from app.schemas.user import UserRead
from app.services.resume_parser import extract_text_from_file


class InMemoryDb:
    def __init__(self, *, resume=None, fail_commit=None, quota_remaining=True):
        self.resume = resume
        self.fail_commit = fail_commit
        self.quota_remaining = quota_remaining
        self.execute_calls = 0
        self.commit_calls = 0
        self.rollback_calls = 0
        self.added_resume = None

    def add(self, resume):
        self.added_resume = resume

    async def scalar(self, _statement):
        if self.resume is not None and self.resume.user_id != "user-1":
            return None
        return self.resume

    async def execute(self, _statement):
        self.execute_calls += 1
        return SimpleNamespace(
            scalar_one_or_none=lambda: 1 if self.quota_remaining else None
        )

    async def commit(self):
        self.commit_calls += 1
        if self.fail_commit == self.commit_calls:
            raise RuntimeError("database commit failed")

    async def refresh(self, _resume):
        pass

    async def rollback(self):
        self.rollback_calls += 1


def _docx_bytes() -> bytes:
    document = Document()
    document.add_paragraph("Python developer with FastAPI experience.")
    output = BytesIO()
    document.save(output)
    return output.getvalue()


def _text_pdf_bytes() -> bytes:
    writer = PdfWriter()
    page = writer.add_blank_page(width=300, height=144)
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    page[NameObject("/Resources")] = DictionaryObject(
        {
            NameObject("/Font"): DictionaryObject(
                {NameObject("/F1"): font}
            )
        }
    )
    stream = DecodedStreamObject()
    stream.set_data(b"BT /F1 12 Tf 10 100 Td (Python resume) Tj ET")
    page[NameObject("/Contents")] = stream
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def _profile_resume(
    *,
    user_id="user-1",
    raw_text="Python developer with several years of experience.",
    consent=True,
    parsed_profile=None,
):
    return Resume(
        id=uuid.uuid4(),
        user_id=user_id,
        filename="resume.pdf",
        file_url="resumes/resume.pdf",
        mime_type="application/pdf",
        raw_text=raw_text,
        parsed_profile=parsed_profile,
        status="ready",
        ai_processing_consent=consent,
    )


def _configure_client(monkeypatch, db, tmp_path):
    settings = SimpleNamespace(
        LOCAL_STORAGE_PATH=str(tmp_path),
        MAX_UPLOAD_SIZE_MB=10,
        RESUME_DAILY_UPLOAD_LIMIT=10,
        RESUME_DAILY_PROFILE_LIMIT=5,
        RESUME_PROFILE_MAX_CHARS=20000,
        RESUME_PROFILE_TIMEOUT_SECONDS=5,
        GEMINI_API_KEY="test-key",
        LLM_MODEL="test-model",
    )
    monkeypatch.setattr(resume_api, "get_settings", lambda: settings)
    monkeypatch.setitem(
        app.dependency_overrides,
        get_current_user,
        lambda: UserRead(id="user-1", email="candidate@example.com"),
    )

    async def override_db():
        yield db

    monkeypatch.setitem(app.dependency_overrides, get_db, override_db)
    return settings


def test_docx_resume_is_validated_and_parsed(tmp_path):
    content = _docx_bytes()
    validate_resume_bytes(content, DOCX_MIME_TYPE, max_size_bytes=1024 * 1024)

    file_path = tmp_path / "resume.docx"
    file_path.write_bytes(content)

    assert extract_text_from_file(str(file_path), DOCX_MIME_TYPE) == (
        "Python developer with FastAPI experience."
    )


def test_pdf_resume_extracts_real_text(tmp_path):
    file_path = tmp_path / "resume.pdf"
    file_path.write_bytes(_text_pdf_bytes())

    assert extract_text_from_file(str(file_path), "application/pdf") == "Python resume"


def test_resume_validation_rejects_oversized_upload():
    with pytest.raises(HTTPException) as error:
        validate_resume_bytes(b"%PDF-content", "application/pdf", max_size_bytes=4)

    assert error.value.status_code == 413


def test_resume_validation_rejects_fake_docx():
    with pytest.raises(HTTPException) as error:
        validate_resume_bytes(b"PK-not-a-docx", DOCX_MIME_TYPE, max_size_bytes=1024)

    assert error.value.status_code == 400


def test_resume_validation_rejects_non_docx_zip():
    output = BytesIO()
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr("not-a-document.txt", "not a Word document")

    with pytest.raises(HTTPException) as error:
        validate_resume_bytes(output.getvalue(), DOCX_MIME_TYPE, max_size_bytes=1024)

    assert error.value.status_code == 400


def test_resume_validation_rejects_docx_with_too_many_entries(monkeypatch):
    monkeypatch.setattr(file_validation, "MAX_DOCX_ARCHIVE_ENTRIES", 1)

    with pytest.raises(HTTPException) as error:
        validate_resume_bytes(_docx_bytes(), DOCX_MIME_TYPE, max_size_bytes=1024 * 1024)

    assert error.value.status_code == 413


def test_pdf_page_limit_is_enforced(tmp_path, monkeypatch):
    file_path = tmp_path / "resume.pdf"
    file_path.write_bytes(_text_pdf_bytes())

    class TooManyPagesReader:
        def __init__(self, _file_path):
            self.pages = [object()] * 101

    monkeypatch.setattr("app.services.resume_parser.PdfReader", TooManyPagesReader)
    with pytest.raises(ValueError, match="page limit"):
        extract_text_from_file(str(file_path), "application/pdf")


def test_resume_mime_detection_uses_signature_before_missing_mime():
    assert detect_resume_mime_type(_docx_bytes(), "candidate.docx", "") == DOCX_MIME_TYPE


def test_resume_upload_endpoint_stores_relative_key_and_consent(tmp_path, monkeypatch):
    db = InMemoryDb()
    _configure_client(monkeypatch, db, tmp_path)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/resume/upload",
            data={"consent_to_ai_processing": "true"},
            files={"file": ("candidate.docx", _docx_bytes(), "")},
        )

    assert response.status_code == 201
    assert response.json()["status"] == "ready"
    assert db.added_resume.raw_text == "Python developer with FastAPI experience."
    assert db.added_resume.file_url == f"resumes/{db.added_resume.id}.docx"
    assert db.added_resume.ai_processing_consent is True
    assert (tmp_path / "resumes" / f"{db.added_resume.id}.docx").is_file()


def test_resume_upload_requires_ai_consent(tmp_path, monkeypatch):
    db = InMemoryDb()
    _configure_client(monkeypatch, db, tmp_path)
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/resume/upload",
            data={"consent_to_ai_processing": "false"},
            files={"file": ("candidate.docx", _docx_bytes(), DOCX_MIME_TYPE)},
        )

    assert response.status_code == 400
    assert db.execute_calls == 0


def test_resume_upload_parse_failure_removes_file(tmp_path, monkeypatch):
    db = InMemoryDb()
    _configure_client(monkeypatch, db, tmp_path)

    def fail_parse(*_args):
        raise KeyError("malformed document structure")

    monkeypatch.setattr(resume_api, "extract_text_from_file", fail_parse)
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/resume/upload",
            data={"consent_to_ai_processing": "true"},
            files={"file": ("candidate.docx", _docx_bytes(), DOCX_MIME_TYPE)},
        )

    assert response.status_code == 400
    assert list((tmp_path / "resumes").iterdir()) == []
    assert db.added_resume is None


def test_resume_upload_commit_failure_rolls_back_and_removes_file(tmp_path, monkeypatch):
    db = InMemoryDb(fail_commit=2)
    _configure_client(monkeypatch, db, tmp_path)
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.post(
            "/api/v1/resume/upload",
            data={"consent_to_ai_processing": "true"},
            files={"file": ("candidate.docx", _docx_bytes(), DOCX_MIME_TYPE)},
        )

    assert response.status_code == 500
    assert db.rollback_calls == 1
    assert list((tmp_path / "resumes").iterdir()) == []


def test_resume_profile_success_truncates_skills_and_caches(tmp_path, monkeypatch):
    resume = _profile_resume(raw_text="A" * 5000)
    db = InMemoryDb(resume=resume)
    settings = _configure_client(monkeypatch, db, tmp_path)
    skills = [f"skill-{index}" for index in range(25)]
    generate_content = MagicMock(
        return_value=SimpleNamespace(
            text=json.dumps(
                {"name": "Candidate", "skills": skills, "experience_count": 3}
            )
        )
    )
    client = SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))
    client_factory = MagicMock(return_value=client)
    monkeypatch.setattr(resume_api.genai, "Client", client_factory)

    with TestClient(app) as test_client:
        response = test_client.get(f"/api/v1/resume/{resume.id}/profile")

    assert response.status_code == 200
    assert len(response.json()["skills"]) == 20
    assert resume.parsed_profile["name"] == "Candidate"
    assert generate_content.call_args.kwargs["contents"].count("A") >= 5000
    assert generate_content.call_args.kwargs["config"].response_mime_type == "application/json"
    assert settings.RESUME_PROFILE_TIMEOUT_SECONDS == 5


def test_resume_profile_cache_hit_skips_second_gemini_call(tmp_path, monkeypatch):
    resume = _profile_resume()
    db = InMemoryDb(resume=resume)
    _configure_client(monkeypatch, db, tmp_path)
    generate_content = MagicMock(
        return_value=SimpleNamespace(
            text=json.dumps(
                {"name": "Candidate", "skills": ["Python"], "experience_count": 2}
            )
        )
    )
    client = SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))
    client_factory = MagicMock(return_value=client)
    monkeypatch.setattr(resume_api.genai, "Client", client_factory)

    with TestClient(app) as test_client:
        first_response = test_client.get(f"/api/v1/resume/{resume.id}/profile")
        second_response = test_client.get(f"/api/v1/resume/{resume.id}/profile")

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert second_response.json()["skills"] == ["Python"]
    assert generate_content.call_count == 1
    assert db.execute_calls == 1


def test_resume_profile_for_another_user_is_not_found(tmp_path, monkeypatch):
    db = InMemoryDb(resume=_profile_resume(user_id="user-2"))
    _configure_client(monkeypatch, db, tmp_path)

    with TestClient(app) as test_client:
        response = test_client.get(f"/api/v1/resume/{uuid.uuid4()}/profile")

    assert response.status_code == 404


def test_resume_profile_empty_text_returns_unprocessable_entity(tmp_path, monkeypatch):
    resume = _profile_resume(raw_text="")
    db = InMemoryDb(resume=resume)
    _configure_client(monkeypatch, db, tmp_path)

    with TestClient(app) as test_client:
        response = test_client.get(f"/api/v1/resume/{resume.id}/profile")

    assert response.status_code == 422


def test_resume_profile_without_consent_is_forbidden(tmp_path, monkeypatch):
    resume = _profile_resume(consent=False)
    db = InMemoryDb(resume=resume)
    _configure_client(monkeypatch, db, tmp_path)
    client_factory = MagicMock()
    monkeypatch.setattr(resume_api.genai, "Client", client_factory)

    with TestClient(app) as test_client:
        response = test_client.get(f"/api/v1/resume/{resume.id}/profile")

    assert response.status_code == 403
    client_factory.assert_not_called()


def test_resume_profile_invalid_json_returns_bad_gateway(tmp_path, monkeypatch):
    resume = _profile_resume()
    db = InMemoryDb(resume=resume)
    _configure_client(monkeypatch, db, tmp_path)
    client = SimpleNamespace(
        models=SimpleNamespace(
            generate_content=MagicMock(return_value=SimpleNamespace(text="not json"))
        )
    )
    monkeypatch.setattr(resume_api.genai, "Client", MagicMock(return_value=client))

    with TestClient(app) as test_client:
        response = test_client.get(f"/api/v1/resume/{resume.id}/profile")

    assert response.status_code == 502


def test_resume_profile_missing_api_key_returns_service_unavailable(tmp_path, monkeypatch):
    resume = _profile_resume()
    db = InMemoryDb(resume=resume)
    settings = _configure_client(monkeypatch, db, tmp_path)
    settings.GEMINI_API_KEY = ""
    client_factory = MagicMock()
    monkeypatch.setattr(resume_api.genai, "Client", client_factory)

    with TestClient(app) as test_client:
        response = test_client.get(f"/api/v1/resume/{resume.id}/profile")

    assert response.status_code == 503
    client_factory.assert_not_called()


def test_resume_profile_network_failure_returns_bad_gateway(tmp_path, monkeypatch):
    resume = _profile_resume()
    db = InMemoryDb(resume=resume)
    _configure_client(monkeypatch, db, tmp_path)
    generate_content = MagicMock(side_effect=RuntimeError("network unavailable"))
    client = SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))
    monkeypatch.setattr(resume_api.genai, "Client", MagicMock(return_value=client))

    with TestClient(app) as test_client:
        response = test_client.get(f"/api/v1/resume/{resume.id}/profile")

    assert response.status_code == 502


def test_resume_profile_timeout_returns_gateway_timeout(tmp_path, monkeypatch):
    resume = _profile_resume()
    db = InMemoryDb(resume=resume)
    _configure_client(monkeypatch, db, tmp_path)
    generate_content = MagicMock(side_effect=TimeoutError())
    client = SimpleNamespace(models=SimpleNamespace(generate_content=generate_content))
    monkeypatch.setattr(resume_api.genai, "Client", MagicMock(return_value=client))

    with TestClient(app) as test_client:
        response = test_client.get(f"/api/v1/resume/{resume.id}/profile")

    assert response.status_code == 504


def test_resume_profile_daily_quota_stops_gemini_call(tmp_path, monkeypatch):
    resume = _profile_resume()
    db = InMemoryDb(resume=resume, quota_remaining=False)
    _configure_client(monkeypatch, db, tmp_path)
    client_factory = MagicMock()
    monkeypatch.setattr(resume_api.genai, "Client", client_factory)

    with TestClient(app) as test_client:
        response = test_client.get(f"/api/v1/resume/{resume.id}/profile")

    assert response.status_code == 429
    client_factory.assert_not_called()


def test_resume_upload_daily_quota_prevents_storage(tmp_path, monkeypatch):
    db = InMemoryDb(quota_remaining=False)
    _configure_client(monkeypatch, db, tmp_path)
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/resume/upload",
            data={"consent_to_ai_processing": "true"},
            files={"file": ("candidate.docx", _docx_bytes(), DOCX_MIME_TYPE)},
        )

    assert response.status_code == 429
    assert not (tmp_path / "resumes").exists()
