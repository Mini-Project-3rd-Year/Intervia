"""Validation helpers for uploaded files."""

from fastapi import HTTPException, status


PDF_SIGNATURE = b"%PDF-"


def validate_pdf_bytes(content: bytes, *, max_size_bytes: int) -> None:
    """Reject oversized or non-PDF content regardless of filename or MIME type."""
    if len(content) > max_size_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File is too large.")
    if not content.startswith(PDF_SIGNATURE):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only valid PDF files are accepted.")