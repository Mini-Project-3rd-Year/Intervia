"""Deterministic evaluation service used until an LLM evaluator is configured."""


def score_answer(transcript: str) -> tuple[float, float, float, str]:
    words = transcript.split()
    length_score = min(100.0, max(20.0, len(words) * 4.0))
    clarity_score = 90.0 if transcript.strip().endswith((".", "!", "?")) else 70.0
    relevance_score = min(100.0, max(25.0, length_score + 10.0))
    feedback = "Add a concrete example and outcome." if len(words) < 25 else "Clear response; quantify the impact where possible."
    return relevance_score, length_score, clarity_score, feedback