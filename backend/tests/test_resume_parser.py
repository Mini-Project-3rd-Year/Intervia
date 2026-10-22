from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile
from types import SimpleNamespace

import pytest
from docx import Document
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app.api.deps import get_current_user
from app.api.v1 import resumes as resume_api
from app.core.file_validation import validate_resume_bytes
from app.db.session import get_db
from app.main import app
from app.schemas.user import UserRead
from app.services.resume_parser import DOCX_MIME_TYPE, extract_text_from_file


def _docx_bytes() -> bytes:
    document = Document()
    document.add_paragraph("Python developer with FastAPI experience.")
    output = BytesIO()
    document.save(output)
    return output.getvalue()


def test_docx_resume_is_validated_and_parsed(tmp_path):
    content = _docx_bytes()
    validate_resume_bytes(content, DOCX_MIME_TYPE, max_size_bytes=1024 * 1024)

    file_path = tmp_path / "resume.docx"
    file_path.write_bytes(content)

    assert extract_text_from_file(str(file_path), DOCX_MIME_TYPE) == (
        "Python developer with FastAPI experience."
    )


def test_pdf_resume_is_parsed(tmp_path):
    output = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.write(output)
    file_path = tmp_path / "resume.pdf"
    file_path.write_bytes(output.getvalue())

    assert extract_text_from_file(str(file_path), "application/pdf") == ""


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


def test_resume_upload_endpoint_stores_and_parses_docx(tmp_path, monkeypatch):
    class InMemoryDb:
        resume = None

        def add(self, resume):
            self.resume = resume

        async def commit(self):
            pass

        async def refresh(self, resume):
            pass

    db = InMemoryDb()
    monkeypatch.setattr(
        resume_api,
        "get_settings",
        lambda: SimpleNamespace(
            LOCAL_STORAGE_PATH=str(tmp_path),
            MAX_UPLOAD_SIZE_MB=10,
            GEMINI_API_KEY="",
        ),
    )
    monkeypatch.setitem(
        app.dependency_overrides,
        get_current_user,
        lambda: UserRead(id="user-1", email="candidate@example.com"),
    )

    async def override_db():
        yield db

    monkeypatch.setitem(app.dependency_overrides, get_db, override_db)
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/resume/upload",
            files={"file": ("candidate.docx", _docx_bytes(), DOCX_MIME_TYPE)},
        )

    assert response.status_code == 201
    assert response.json()["status"] == "ready"
    assert db.resume.raw_text == "Python developer with FastAPI experience."
    assert (tmp_path / "resumes" / f"{db.resume.id}.docx").is_file()
