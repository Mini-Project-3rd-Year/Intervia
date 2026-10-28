"""Validation helpers for uploaded files."""

from io import BytesIO
from zipfile import BadZipFile, ZipFile

from fastapi import HTTPException, status


PDF_SIGNATURE = b"%PDF-"
DOCX_SIGNATURE = b"PK"
MAX_DOCX_UNCOMPRESSED_BYTES = 50 * 1024 * 1024
MAX_DOCX_ARCHIVE_ENTRIES = 1000
PDF_MIME_TYPE = "application/pdf"
DOCX_MIME_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def detect_resume_mime_type(content: bytes, filename: str, declared_mime_type: str | None) -> str:
    """Prefer file signatures, falling back to an allowed MIME type or extension."""
    if content.startswith(PDF_SIGNATURE):
        return PDF_MIME_TYPE
    if content.startswith(DOCX_SIGNATURE):
        return DOCX_MIME_TYPE

    suffix = filename.rpartition(".")[2].lower()
    if suffix == "pdf":
        return PDF_MIME_TYPE
    if suffix == "docx":
        return DOCX_MIME_TYPE
    if declared_mime_type in {PDF_MIME_TYPE, DOCX_MIME_TYPE}:
        return declared_mime_type
    return declared_mime_type or ""


def validate_resume_bytes(content: bytes, mime_type: str, *, max_size_bytes: int) -> None:
    """Validate resume size and file signature independently of its filename."""
    if len(content) > max_size_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File is too large.")

    if mime_type == PDF_MIME_TYPE:
        if not content.startswith(PDF_SIGNATURE):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only valid PDF files are accepted.")
        return

    if mime_type == DOCX_MIME_TYPE:
        if not content.startswith(DOCX_SIGNATURE):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only valid DOCX files are accepted.")
        try:
            with ZipFile(BytesIO(content)) as archive:
                entries = archive.infolist()
                if len(entries) > MAX_DOCX_ARCHIVE_ENTRIES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="The DOCX archive contains too many entries.",
                    )
                valid_docx = {
                    "[Content_Types].xml",
                    "word/document.xml",
                }.issubset({entry.filename for entry in entries})
                uncompressed_size = sum(entry.file_size for entry in entries)
        except BadZipFile as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only valid DOCX files are accepted.") from exc
        if not valid_docx:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only valid DOCX files are accepted.")
        if uncompressed_size > MAX_DOCX_UNCOMPRESSED_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="The uncompressed DOCX content is too large.",
            )
        return

    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail="Only PDF and DOCX files are accepted.",
    )