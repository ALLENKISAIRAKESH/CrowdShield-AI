"""Unit tests for result schema validation and serialization."""

import json
from src.crowdshield.schemas import (
    AnalysisResult,
    CrowdScenario,
    DecisionResult,
    DecisionStatus,
    DensityLevel,
    ExitStatus,
    FlowTrend,
    IncidentSignal,
    TraceEvent,
)


def test_analysis_result_serialization():
    """Verify AnalysisResult serializes to valid JSON matching data contract."""
    scenario = CrowdScenario(
        scenario_id="s1",
        label="Serialization Test",
        density_level=DensityLevel.LOW,
        flow_trend=FlowTrend.STABLE,
        exit_status=ExitStatus.CLEAR,
        incident_signal=IncidentSignal.NONE_REPORTED,
    )
    decision = DecisionResult(
        status=DecisionStatus.SUCCESS,
        decision="NORMAL",
        confidence=0.92,
        threshold=0.70,
        elapsed_ms=105.2,
    )
    trace = [
        TraceEvent(
            timestamp="2026-10-23T12:00:00Z",
            stage="test_stage",
            message="Test message",
        )
    ]

    result = AnalysisResult(
        scenario=scenario,
        decision_result=decision,
        explanation="Routine concourse conditions.",
        recommended_steps=["Monitor standard checkpoints"],
        human_review_required=False,
        bedrock_elapsed_ms=320.1,
        total_elapsed_ms=425.3,
        trace=trace,
    )

    json_str = json.dumps(result.model_dump())
    assert json_str
    parsed = json.loads(json_str)
    assert parsed["scenario"]["scenario_id"] == "s1"
    assert parsed["decision_result"]["decision"] == "NORMAL"
    assert parsed["human_review_required"] is False
    assert len(parsed["trace"]) == 1
