"""Unit tests for the end-to-end CrowdShieldOrchestrator."""

from unittest.mock import patch
import pytest

from src.crowdshield.orchestrator import CrowdShieldOrchestrator
from src.crowdshield.scenarios import PRESET_SCENARIOS
from src.crowdshield.schemas import BedrockResponseSchema, DecisionStatus, TraceEvent


def test_orchestrator_analyze_success():
    """Verify orchestrator returns SUCCESS when Decider passes threshold."""
    orch = CrowdShieldOrchestrator()
    mock_decider_resp = {
        "status": "success",
        "decision": "NORMAL",
        "confidence": 0.92,
        "threshold": 0.70,
        "elapsed_ms": 45.0,
        "source": "strands-decider-2B",
        "error_summary": None,
        "raw_probabilities": {"NORMAL": 0.92, "WARNING": 0.06, "CRITICAL": 0.02},
    }

    mock_bedrock_schema = BedrockResponseSchema(
        summary="Normal crowd flow observed without distress signals.",
        recommended_steps=[
            "Continue standard monitoring",
            "Maintain open corridor checkpoints",
        ],
        human_review_required=False,
    )

    with patch.object(orch.decider_client.decider, "evaluate", return_value=mock_decider_resp):
        with patch.object(
            orch.bedrock_agent,
            "generate_plan",
            return_value=(mock_bedrock_schema, 110.0, [], None),
        ):
            scenario = PRESET_SCENARIOS["routine_movement"]
            result = orch.analyze(scenario)

            assert result.decision_result.status == DecisionStatus.SUCCESS
            assert result.decision_result.decision == "NORMAL"
            assert result.decision_result.confidence == 0.92
            assert result.human_review_required is False
            assert len(result.recommended_steps) == 2
            assert len(result.trace) >= 4


def test_orchestrator_analyze_low_confidence():
    """Verify orchestrator marks human_review_required when confidence is low."""
    orch = CrowdShieldOrchestrator()
    mock_decider_resp = {
        "status": "low_confidence",
        "decision": "WARNING",
        "confidence": 0.55,
        "threshold": 0.70,
        "elapsed_ms": 50.0,
        "source": "strands-decider-2B",
        "error_summary": "Confidence 0.55 below threshold 0.70",
        "raw_probabilities": {"NORMAL": 0.35, "WARNING": 0.55, "CRITICAL": 0.10},
    }

    mock_bedrock_schema = BedrockResponseSchema(
        summary="Ambiguous movement patterns detected.",
        recommended_steps=[
            "Perform visual verification",
            "Dispatch zone marshal",
        ],
        human_review_required=True,
    )

    with patch.object(orch.decider_client.decider, "evaluate", return_value=mock_decider_resp):
        with patch.object(
            orch.bedrock_agent,
            "generate_plan",
            return_value=(mock_bedrock_schema, 120.0, [], None),
        ):
            scenario = PRESET_SCENARIOS["ambiguous_report"]
            result = orch.analyze(scenario)

            assert result.decision_result.status == DecisionStatus.LOW_CONFIDENCE
            assert result.decision_result.decision == "WARNING"
            assert result.human_review_required is True
            assert len(result.recommended_steps) == 2


def test_orchestrator_analyze_decider_offline_fallback():
    """Verify orchestrator handles offline decider gracefully."""
    orch = CrowdShieldOrchestrator()
    mock_decider_resp = {
        "status": "unavailable",
        "decision": None,
        "confidence": None,
        "threshold": 0.70,
        "elapsed_ms": 15.0,
        "source": "fallback-review",
        "error_summary": "Decider service unreachable at http://127.0.0.1:8099",
        "raw_probabilities": None,
    }

    with patch.object(orch.decider_client.decider, "evaluate", return_value=mock_decider_resp):
        scenario = PRESET_SCENARIOS["blocked_exit"]
        result = orch.analyze(scenario)

        assert result.decision_result.status == DecisionStatus.UNAVAILABLE
        assert result.human_review_required is True
        assert len(result.recommended_steps) >= 1
