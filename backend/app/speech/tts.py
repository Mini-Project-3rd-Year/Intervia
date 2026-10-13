"""
backend/app/speech/tts.py
Text-to-speech generation service for interview questions using gTTS.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional
from uuid import uuid4

from app.core.config import get_settings

logger = logging.getLogger(__name__)

try:
    from gtts import gTTS

    _GTTS_AVAILABLE = True
except ImportError:
    gTTS = None  # type: ignore[assignment]
    _GTTS_AVAILABLE = False


def get_audio_storage_dir() -> Path:
    """Return the resolved storage directory for generated audio files."""
    return get_settings().storage_path / "audio"


def generate_question_audio(
    text: str,
    output_dir: Optional[Path] = None,
) -> Optional[str]:
    """
    Generate an English speech MP3 file from text using gTTS.

    Saves the file to `uploads/audio/<uuid>.mp3` and returns the URL
    path `/static/audio/<filename>.mp3`.

    Returns `None` if text is empty, gTTS is not installed, or any
    generation/file system error occurs, ensuring caller flows never crash.
    """
    if not text or not text.strip():
        logger.warning("Empty text received; skipping speech generation")
        return None

    if not _GTTS_AVAILABLE or gTTS is None:
        logger.warning(
            "gTTS package is not installed; text-to-speech generation is disabled"
        )
        return None

    target_dir = output_dir if output_dir is not None else get_audio_storage_dir()

    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid4().hex}.mp3"
        filepath = target_dir / filename

        tts = gTTS(text=text.strip(), lang="en")
        tts.save(str(filepath))

        return f"/static/audio/{filename}"
    except Exception as exc:
        logger.warning(
            "Failed to generate speech audio for question: %s",
            exc,
            exc_info=True,
        )
        return None
