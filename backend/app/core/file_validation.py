"""Validation helpers for uploaded files."""

from io import BytesIO
from zipfile import BadZipFile, ZipFile

from fastapi import HTTPException, status


PDF_SIGNATURE = b"%PDF-"
DOCX_SIGNATURE = b"PK"
MAX_DOCX_UNCOMPRESSED_BYTES = 50 * 1024 * 1024


def validate_pdf_bytes(content: bytes, *, max_size_bytes: int) -> None:
    """Reject oversized or non-PDF content regardless of filename or MIME type."""
    if len(content) > max_size_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File is too large.")
    if not content.startswith(PDF_SIGNATURE):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only valid PDF files are accepted.")


def validate_resume_bytes(content: bytes, mime_type: str, *, max_size_bytes: int) -> None:
    """Validate resume size and file signature independently of its filename."""
    if len(content) > max_size_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File is too large.")

    if mime_type == "application/pdf":
        if not content.startswith(PDF_SIGNATURE):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only valid PDF files are accepted.")
        return

    if mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        if not content.startswith(DOCX_SIGNATURE):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only valid DOCX files are accepted.")
        try:
            with ZipFile(BytesIO(content)) as archive:
                entries = archive.infolist()
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