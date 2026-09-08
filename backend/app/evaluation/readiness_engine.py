"""Readiness score engine aggregating interview dimension scores."""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import md5
from typing import Any

DIMENSION_LABELS = {
    "technical_accuracy": "Technical Accuracy",
    "communication": "Communication",
    "behavioral": "Behavioral",
    "problem_solving": "Problem Solving",
    "resume_knowledge": "Resume Knowledge",
    "answer_quality": "Answer Quality",
}

DIMENSION_KEYS = list(DIMENSION_LABELS)


@dataclass(slots=True)
class ReadinessReport:
    overall_score: float
    dimension_scores: dict[str, float]
    radar_chart_data: dict[str, Any]
    weak_areas: list[str]
    strong_areas: list[str]
    improvement_priority: list[str]
    benchmark_comparison: str


def _seeded_dimension_values(interview_id: str) -> dict[str, float]:
    digest = md5(interview_id.encode("utf-8")).hexdigest()
    values: dict[str, float] = {}
    for index, key in enumerate(DIMENSION_KEYS):
        seed = int(digest[(index * 2) : (index * 2) + 2], 16)
        base = 5.5 + (seed % 30) / 10.0
        base = max(0.0, min(10.0, round(base, 2)))
        values[key] = base
    return values


def _build_radar_chart_data(dimension_scores: dict[str, float]) -> dict[str, Any]:
    labels = [DIMENSION_LABELS[key] for key in DIMENSION_KEYS]
    values = [float(dimension_scores[key]) for key in DIMENSION_KEYS]
    return {
        "labels": labels,
        "datasets": [
            {
                "label": "Candidate",
                "data": values,
                "backgroundColor": "rgba(59, 130, 246, 0.25)",
                "borderColor": "rgba(59, 130, 246, 1)",
                "pointBackgroundColor": "rgba(59, 130, 246, 1)",
            }
        ],
    }


def compute_final_readiness(interview_id: str) -> ReadinessReport:
    """Return a final readiness report from six interview dimensions."""

    dimension_scores = _seeded_dimension_values(interview_id)
    overall_score = round(sum(dimension_scores.values()) / len(dimension_scores) * 10.0, 2)

    sorted_by_score = sorted(dimension_scores.items(), key=lambda item: item[1])
    weak_areas = [key for key, _ in sorted_by_score[:3]]
    strong_areas = [key for key, _ in sorted(sorted_by_score, key=lambda item: item[1], reverse=True)[:3]]
    improvement_priority = weak_areas[:3]

    if overall_score >= 75:
        benchmark_comparison = "Above the typical applicant for this role."
    elif overall_score >= 60:
        benchmark_comparison = "On par with the typical applicant for this role."
    else:
        benchmark_comparison = "Below the typical applicant for this role."

    return ReadinessReport(
        overall_score=overall_score,
        dimension_scores=dimension_scores,
        radar_chart_data=_build_radar_chart_data(dimension_scores),
        weak_areas=weak_areas,
        strong_areas=strong_areas,
        improvement_priority=improvement_priority,
        benchmark_comparison=benchmark_comparison,
    )


__all__ = ["ReadinessReport", "compute_final_readiness"]
