from app.agents.communication_agent.agent import CommunicationAgent
from app.evaluation.readiness_engine import ReadinessReport, compute_final_readiness


def test_communication_agent_calculates_wpm_and_fillers():
    transcript = (
        "I would say um that the project was very good and we learned a lot from it because "
        "the team collaborated well and delivered results. You know, we improved our process, "
        "like communication and basically quality across the sprint."
    )
    agent = CommunicationAgent()
    metrics = agent.analyze(transcript, duration_seconds=120)

    expected_wpm = len(agent._detect_fillers(transcript.lower()))
    assert metrics.wpm == len(transcript.split()) / (120 / 60)
    assert metrics.filler_word_count >= 4
    assert "um" in metrics.filler_word_list
    assert "you know" in metrics.filler_word_list
    assert "like" in metrics.filler_word_list
    assert "basically" in metrics.filler_word_list
    assert 0 <= metrics.clarity_score <= 10


def test_readiness_report_has_six_dimensions_and_radar_shape():
    report = ReadinessReport(
        overall_score=72.5,
        dimension_scores={
            "technical_accuracy": 7.2,
            "communication": 8.0,
            "behavioral": 6.9,
            "problem_solving": 7.4,
            "resume_knowledge": 6.8,
            "answer_quality": 7.6,
        },
        radar_chart_data={
            "labels": [
                "Technical Accuracy",
                "Communication",
                "Behavioral",
                "Problem Solving",
                "Resume Knowledge",
                "Answer Quality",
            ],
            "datasets": [{"label": "Candidate", "data": [7.2, 8.0, 6.9, 7.4, 6.8, 7.6]}],
        },
        weak_areas=["behavioral"],
        strong_areas=["communication"],
        improvement_priority=["behavioral", "resume_knowledge", "problem_solving"],
        benchmark_comparison="Above the typical applicant.",
    )

    assert len(report.dimension_scores) == 6
    assert len(report.radar_chart_data["labels"]) == 6
    assert all(0.0 <= value <= 10.0 for value in report.radar_chart_data["datasets"][0]["data"])
    assert report.radar_chart_data["datasets"][0]["data"][0] == 7.2


def test_compute_final_readiness_uses_expected_dimensions():
    report = compute_final_readiness("interview-123")

    assert set(report.dimension_scores.keys()) == {
        "technical_accuracy",
        "communication",
        "behavioral",
        "problem_solving",
        "resume_knowledge",
        "answer_quality",
    }
    assert 0 <= report.overall_score <= 100
    assert len(report.radar_chart_data["labels"]) == 6
    assert all(0.0 <= value <= 10.0 for value in report.radar_chart_data["datasets"][0]["data"])
