"""Reusable policy decision runner and confidence gate for Strands Decider 2B."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Optional, Tuple

from .question_definition import POLICY_QUESTION_NAME, get_crowd_policy_question


class DeciderUnavailableError(RuntimeError):
    """Raised when the Strands Decider endpoint cannot be reached."""


class CrowdPolicyDecider:
    """Invokes Strands Decider 2B for typed policy classification with threshold gating."""

    def __init__(
        self,
        url: str = "http://127.0.0.1:8099",
        timeout: float = 30.0,
        default_threshold: float = 0.70,
    ) -> None:
        self.url = url.rstrip("/")
        self.timeout = timeout
        self.default_threshold = default_threshold

    def check_health(self) -> Dict[str, Any]:
        """Check if Strands Decider service is healthy."""
        req = urllib.request.Request(f"{self.url}/health")
        try:
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            raise DeciderUnavailableError(
                f"Strands Decider server unreachable at {self.url}: {exc}"
            ) from exc

    def evaluate(
        self,
        state_text: str,
        threshold: Optional[float] = None,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """Send state to Strands Decider, extract choice and confidence, and apply confidence gate.

        Returns a standardized dictionary:
        {
            "status": "success" | "low_confidence" | "unavailable" | "error",
            "decision": str | None,
            "confidence": float | None,
            "threshold": float,
            "elapsed_ms": float | None,
            "source": str,
            "error_summary": str | None,
            "raw_probabilities": dict[str, float] | None,
        }
        """
        active_threshold = threshold if threshold is not None else self.default_threshold
        question = get_crowd_policy_question()

        payload = {
            "state": state_text,
            "model": "strands-decider-2B-qwen3.5-v1-2610",
            "questions": {
                POLICY_QUESTION_NAME: question
            },
        }

        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.url}/v1/systemone",
            data=body,
            headers={"Content-Type": "application/json"},
        )

        start_time = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
            elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        except urllib.error.URLError as url_err:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return {
                "status": "unavailable",
                "decision": None,
                "confidence": None,
                "threshold": active_threshold,
                "elapsed_ms": elapsed_ms,
                "source": "fallback-review",
                "error_summary": f"Decider service unreachable at {self.url} ({url_err.reason})",
                "raw_probabilities": None,
            }
        except Exception as exc:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return {
                "status": "error",
                "decision": None,
                "confidence": None,
                "threshold": active_threshold,
                "elapsed_ms": elapsed_ms,
                "source": "fallback-review",
                "error_summary": f"Unexpected error during Decider call: {exc}",
                "raw_probabilities": None,
            }

        # Parse response safely
        try:
            answers = resp_data.get("answers", {})
            ans = answers.get(POLICY_QUESTION_NAME, {})
            decision = ans.get("choice")
            confidence = ans.get("confidence")
            probabilities = ans.get("probabilities")

            if decision is None or confidence is None:
                return {
                    "status": "error",
                    "decision": decision,
                    "confidence": confidence,
                    "threshold": active_threshold,
                    "elapsed_ms": elapsed_ms,
                    "source": "strands-decider-2B",
                    "error_summary": "Malformed response: missing choice or confidence field",
                    "raw_probabilities": probabilities,
                }

            # Enforce confidence gate
            if float(confidence) < active_threshold:
                return {
                    "status": "low_confidence",
                    "decision": str(decision),
                    "confidence": float(confidence),
                    "threshold": active_threshold,
                    "elapsed_ms": elapsed_ms,
                    "source": "strands-decider-2B",
                    "error_summary": (
                        f"Confidence {confidence:.3f} is below review threshold "
                        f"{active_threshold:.3f}. Escalation to human review required."
                    ),
                    "raw_probabilities": probabilities,
                }

            return {
                "status": "success",
                "decision": str(decision),
                "confidence": float(confidence),
                "threshold": active_threshold,
                "elapsed_ms": elapsed_ms,
                "source": "strands-decider-2B",
                "error_summary": None,
                "raw_probabilities": probabilities,
            }
        except Exception as parse_err:
            return {
                "status": "error",
                "decision": None,
                "confidence": None,
                "threshold": active_threshold,
                "elapsed_ms": elapsed_ms,
                "source": "strands-decider-2B",
                "error_summary": f"Failed to parse Decider output: {parse_err}",
                "raw_probabilities": None,
            }
