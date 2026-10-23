"""Unit tests for the confidence gate policy."""

import pytest
from unittest.mock import patch
from decision_patterns.crowd_policy.decision import CrowdPolicyDecider


def test_confidence_above_threshold():
    """Verify confidence above threshold results in success status."""
    decider = CrowdPolicyDecider()

    mock_resp_body = {
        "answers": {
            "crowd_policy_classification": {
                "choice": "NORMAL",
                "confidence": 0.88,
                "probabilities": {"NORMAL": 0.88, "WARNING": 0.10, "CRITICAL": 0.02},
            }
        },
        "latency_ms": 115.0,
    }

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_resp = mock_urlopen.return_value.__enter__.return_value
        import json
        mock_resp.read.return_value = json.dumps(mock_resp_body).encode("utf-8")

        result = decider.evaluate("Test state", threshold=0.70)
        assert result["status"] == "success"
        assert result["decision"] == "NORMAL"
        assert result["confidence"] == 0.88
        assert result["error_summary"] is None


def test_confidence_below_threshold():
    """Verify confidence below threshold triggers low_confidence status."""
    decider = CrowdPolicyDecider()

    mock_resp_body = {
        "answers": {
            "crowd_policy_classification": {
                "choice": "WARNING",
                "confidence": 0.58,
                "probabilities": {"NORMAL": 0.30, "WARNING": 0.58, "CRITICAL": 0.12},
            }
        },
        "latency_ms": 130.0,
    }

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_resp = mock_urlopen.return_value.__enter__.return_value
        import json
        mock_resp.read.return_value = json.dumps(mock_resp_body).encode("utf-8")

        result = decider.evaluate("Test state", threshold=0.75)
        assert result["status"] == "low_confidence"
        assert result["decision"] == "WARNING"
        assert result["confidence"] == 0.58
        assert "below review threshold" in result["error_summary"]


def test_confidence_boundary_cases():
    """Test exact threshold boundary."""
    decider = CrowdPolicyDecider()

    mock_resp_body = {
        "answers": {
            "crowd_policy_classification": {
                "choice": "CRITICAL",
                "confidence": 0.70,
            }
        },
        "latency_ms": 120.0,
    }

    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_resp = mock_urlopen.return_value.__enter__.return_value
        import json
        mock_resp.read.return_value = json.dumps(mock_resp_body).encode("utf-8")

        # Equal to threshold should succeed
        result = decider.evaluate("Test state", threshold=0.70)
        assert result["status"] == "success"
