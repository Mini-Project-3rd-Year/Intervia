"""Communication analytics for interview transcripts."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable

FILLER_PHRASES = (
    "you know",
    "um",
    "uh",
    "like",
    "basically",
)


@dataclass(slots=True)
class CommunicationMetrics:
    transcript: str
    duration_seconds: int
    word_count: int
    wpm: float
    filler_word_count: int
    filler_word_list: list[str] = field(default_factory=list)
    pause_count: int = 0
    avg_sentence_length: float = 0.0
    vocabulary_richness: float = 0.0
    clarity_score: float = 0.0


class CommunicationAgent:
    """Compute communication metrics from an interview transcript."""

    filler_words = FILLER_PHRASES

    def analyze(self, transcript: str, duration_seconds: int) -> CommunicationMetrics:
        cleaned = (transcript or "").strip()
        duration = max(int(duration_seconds), 1)
        words = re.findall(r"\b[\w']+\b", cleaned.lower())
        word_count = len(words)
        wpm = word_count / (duration / 60.0)

        filler_word_list = self._detect_fillers(cleaned.lower())
        filler_word_count = len(filler_word_list)

        pause_count = len(re.findall(r"(?:\.\.\.|…|—|,\s+|;\s+)", cleaned))

        sentences = re.split(r"(?<=[.!?])\s+", cleaned)
        sentence_count = max(len([s for s in sentences if s.strip()]), 1)
        avg_sentence_length = word_count / sentence_count if word_count else 0.0

        unique_words = set(words)
        vocabulary_richness = len(unique_words) / word_count if word_count else 0.0

        clarity_score = self._score_clarity(wpm, filler_word_count, avg_sentence_length, vocabulary_richness)

        return CommunicationMetrics(
            transcript=cleaned,
            duration_seconds=duration,
            word_count=word_count,
            wpm=wpm,
            filler_word_count=filler_word_count,
            filler_word_list=filler_word_list,
            pause_count=pause_count,
            avg_sentence_length=avg_sentence_length,
            vocabulary_richness=vocabulary_richness,
            clarity_score=clarity_score,
        )

    def _detect_fillers(self, text: str) -> list[str]:
        matches: list[str] = []
        for filler in self.filler_words:
            pattern = re.compile(rf"\b{re.escape(filler)}\b")
            count = len(pattern.findall(text))
            if count:
                matches.extend([filler] * count)
        return matches

    def _score_clarity(
        self,
        wpm: float,
        filler_word_count: int,
        avg_sentence_length: float,
        vocabulary_richness: float,
    ) -> float:
        score = 7.0
        score += min(2.0, max(0.0, (wpm - 120.0) / 80.0))
        score -= min(3.0, filler_word_count * 0.4)
        score += min(1.0, max(0.0, avg_sentence_length / 22.0 - 0.7))
        score += min(1.0, max(0.0, (vocabulary_richness - 0.35) * 2.0))
        score = max(0.0, min(10.0, round(score, 2)))
        return score
