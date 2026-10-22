"""Extract plain text from PDF and DOCX resume files."""

from pathlib import Path

from docx import Document
from pypdf import PdfReader


PDF_MIME_TYPE = "application/pdf"
DOCX_MIME_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def extract_text_from_file(file_path: str, mime_type: str) -> str:
    """Extract text from a supported resume file."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    if mime_type == PDF_MIME_TYPE:
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    if mime_type == DOCX_MIME_TYPE:
        document = Document(str(path))
        paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
        return "\n".join(paragraphs)
    raise ValueError(f"Unsupported file type: {mime_type}")
