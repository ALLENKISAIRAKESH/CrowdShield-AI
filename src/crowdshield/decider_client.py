"""Client adapter connecting CrowdScenario domain objects to Strands Decider."""

from __future__ import annotations

import datetime
from typing import Tuple

from decision_patterns.crowd_policy.decision import CrowdPolicyDecider
from .config import settings
from .schemas import CrowdScenario, DecisionResult, DecisionStatus, TraceEvent


class CrowdDeciderClient:
    """Manages evaluation of CrowdScenario instances with Decider and audit trace emission."""

    def __init__(
        self,
        endpoint_url: str = settings.strands_decider_url,
        threshold: float = settings.confidence_threshold,
        timeout: float = settings.timeout_seconds,
    ) -> None:
        self.decider = CrowdPolicyDecider(
            url=endpoint_url,
            timeout=timeout,
            default_threshold=threshold,
        )
        self.threshold = threshold

    def evaluate_scenario(
        self, scenario: CrowdScenario, threshold: float | None = None
    ) -> Tuple[DecisionResult, list[TraceEvent]]:
        """Evaluate a scenario and return typed DecisionResult plus trace events."""
        active_threshold = threshold if threshold is not None else self.threshold
        state_text = scenario.to_state_summary()

        trace: list[TraceEvent] = [
            TraceEvent(
                timestamp=datetime.datetime.utcnow().isoformat() + "Z",
                stage="decider_request",
                message=f"Dispatching scenario '{scenario.label}' to Strands Decider 2B",
                details={
                    "endpoint": self.decider.url,
                    "state_preview": state_text,
                    "threshold": active_threshold,
                },
            )
        ]

        raw_result = self.decider.evaluate(state_text=state_text, threshold=active_threshold)

        decision_status = DecisionStatus(raw_result["status"])
        decision_result = DecisionResult(
            status=decision_status,
            decision=raw_result["decision"],
            confidence=raw_result["confidence"],
            threshold=raw_result["threshold"],
            elapsed_ms=raw_result["elapsed_ms"],
            source=raw_result["source"],
            error_summary=raw_result["error_summary"],
            raw_probabilities=raw_result["raw_probabilities"],
        )

        trace.append(
            TraceEvent(
                timestamp=datetime.datetime.utcnow().isoformat() + "Z",
                stage="decider_response",
                message=(
                    f"Decider response: decision='{decision_result.decision}', "
                    f"confidence={decision_result.confidence}, status='{decision_result.status.value}'"
                ),
                details={
                    "latency_ms": decision_result.elapsed_ms,
                    "source": decision_result.source,
                    "probabilities": decision_result.raw_probabilities,
                },
            )
        )

        # Confidence gate trace
        if decision_status == DecisionStatus.SUCCESS:
            trace.append(
                TraceEvent(
                    timestamp=datetime.datetime.utcnow().isoformat() + "Z",
                    stage="confidence_gate",
                    message=(
                        f"Confidence {decision_result.confidence:.3f} >= threshold "
                        f"{active_threshold:.3f}: Proceeding to agent explanation"
                    ),
                    details={"action": "PROCEED", "threshold": active_threshold},
                )
            )
        elif decision_status == DecisionStatus.LOW_CONFIDENCE:
            trace.append(
                TraceEvent(
                    timestamp=datetime.datetime.utcnow().isoformat() + "Z",
                    stage="confidence_gate",
                    message=(
                        f"Confidence {decision_result.confidence:.3f} < threshold "
                        f"{active_threshold:.3f}: Automated gate triggered escalation to human review"
                    ),
                    details={"action": "REQUIRE_HUMAN_REVIEW", "threshold": active_threshold},
                )
            )
        else:
            trace.append(
                TraceEvent(
                    timestamp=datetime.datetime.utcnow().isoformat() + "Z",
                    stage="confidence_gate",
                    message=f"Decider returned non-success state: {decision_result.error_summary}",
                    details={"action": "FALLBACK_REVIEW", "error": decision_result.error_summary},
                )
            )

        return decision_result, trace
