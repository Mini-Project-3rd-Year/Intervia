"""Small, dependency-free sanitizers for user-provided text."""

from html import unescape
from re import sub


def sanitize_text(value: str, *, max_length: int) -> str:
    """Strip markup/control characters and enforce a bounded text length."""
    value = sub(r"<\s*(script|style)\b[^>]*>.*?<\s*/\s*\1\s*>", "", value, flags=2)
    value = unescape(sub(r"<[^>]*>", "", value))
    value = "".join(character for character in value if character.isprintable() or character in "\n\t")
    return value.strip()[:max_length]