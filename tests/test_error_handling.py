"""Unit tests for Decider and Bedrock error states and graceful degradation."""

from unittest.mock import patch
import urllib.error
from decision_patterns.crowd_policy.decision import CrowdPolicyDecider
from src.crowdshield.bedrock_agent import BedrockAgent
from src.crowdshield.schemas import (
    CrowdScenario,
    DecisionResult,
    DecisionStatus,
    DensityLevel,
    ExitStatus,
    FlowTrend,
    IncidentSignal,
)


def test_decider_service_unavailable():
    """Verify clean 'unavailable' status when Decider server is unreachable."""
    decider = CrowdPolicyDecider(url="http://127.0.0.1:9999")

    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("Connection refused")):
        result = decider.evaluate("Test state")
        assert result["status"] == "unavailable"
        assert result["decision"] is None
        assert "unreachable" in result["error_summary"].lower()


def test_decider_malformed_response():
    """Verify clean 'error' status when Decider response is missing required fields."""
    decider = CrowdPolicyDecider()

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_resp = mock_urlopen.return_value.__enter__.return_value
        import json
        # Missing choice and confidence
        mock_resp.read.return_value = json.dumps({"answers": {"crowd_policy_classification": {}}}).encode("utf-8")

        result = decider.evaluate("Test state")
        assert result["status"] == "error"
        assert "Malformed response" in result["error_summary"]


def test_bedrock_agent_fallback_on_client_error():
    """Verify BedrockAgent produces deterministic fallback when AWS client throws error."""
    agent = BedrockAgent()
    scenario = CrowdScenario(
        scenario_id="err_test",
        label="Test Fallback",
        density_level=DensityLevel.HIGH,
        flow_trend=FlowTrend.DETERIORATING,
        exit_status=ExitStatus.BLOCKED,
        incident_signal=IncidentSignal.CONFIRMED_BY_OPERATOR,
    )
    decision = DecisionResult(
        status=DecisionStatus.SUCCESS,
        decision="CRITICAL",
        confidence=0.85,
        threshold=0.70,
    )

    with patch.object(agent, "_get_client", side_effect=Exception("AWS credentials missing")):
        plan, elapsed_ms, trace, err = agent.generate_plan(scenario, decision)
        assert plan is not None
        assert len(plan.recommended_steps) >= 3
        assert plan.human_review_required is True
        assert "simulated data" in plan.limitations.lower()
        assert err is not None
