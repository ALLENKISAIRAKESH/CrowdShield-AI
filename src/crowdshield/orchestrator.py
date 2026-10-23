"""Orchestrator coordinating scenario normalization, Decider evaluation, Bedrock generation, and audit logging."""

from __future__ import annotations

import datetime
import time
from typing import List, Optional

from .bedrock_agent import BedrockAgent
from .config import settings
from .decider_client import CrowdDeciderClient
from .schemas import (
    AnalysisResult,
    CrowdScenario,
    DecisionResult,
    DecisionStatus,
    TraceEvent,
)


class CrowdShieldOrchestrator:
    """End-to-end analysis coordinator implementing the decision-first architecture."""

    def __init__(
        self,
        decider_url: str = settings.strands_decider_url,
        confidence_threshold: float = settings.confidence_threshold,
        bedrock_model_id: str = settings.bedrock_model_id,
        aws_region: str = settings.aws_region,
    ) -> None:
        self.decider_client = CrowdDeciderClient(
            endpoint_url=decider_url,
            threshold=confidence_threshold,
        )
        self.bedrock_agent = BedrockAgent(
            model_id=bedrock_model_id,
            region_name=aws_region,
        )

    def analyze(
        self,
        scenario: CrowdScenario,
        confidence_threshold: Optional[float] = None,
    ) -> AnalysisResult:
        """Execute full end-to-end evaluation pipeline with audit trail."""
        overall_start = time.perf_counter()
        active_threshold = (
            confidence_threshold
            if confidence_threshold is not None
            else self.decider_client.threshold
        )

        trace: List[TraceEvent] = [
            TraceEvent(
                timestamp=datetime.datetime.utcnow().isoformat() + "Z",
                stage="scenario_input",
                message=f"Received scenario '{scenario.label}' for policy evaluation",
                details={
                    "scenario_id": scenario.scenario_id,
                    "density": scenario.density_level.value,
                    "flow": scenario.flow_trend.value,
                    "exit": scenario.exit_status.value,
                    "incident": scenario.incident_signal.value,
                },
            )
        ]

        # 1. Step: Call Strands Decider 2B
        decision_result, decider_trace = self.decider_client.evaluate_scenario(
            scenario=scenario,
            threshold=active_threshold,
        )
        trace.extend(decider_trace)

        # 2. Step: Call Bedrock-backed Strands Agent
        plan, bedrock_elapsed_ms, bedrock_trace, bedrock_error = self.bedrock_agent.generate_plan(
            scenario=scenario,
            decision_result=decision_result,
        )
        trace.extend(bedrock_trace)

        # 3. Step: Completion & review flag
        total_elapsed_ms = round((time.perf_counter() - overall_start) * 1000.0, 2)
        human_review_required = (
            decision_result.status != DecisionStatus.SUCCESS
            or plan.human_review_required
        )

        trace.append(
            TraceEvent(
                timestamp=datetime.datetime.utcnow().isoformat() + "Z",
                stage="completion",
                message="Completed end-to-end crowd policy workflow",
                details={
                    "total_elapsed_ms": total_elapsed_ms,
                    "human_review_required": human_review_required,
                    "decision": decision_result.decision,
                },
            )
        )

        return AnalysisResult(
            scenario=scenario,
            decision_result=decision_result,
            explanation=plan.summary,
            recommended_steps=plan.recommended_steps,
            human_review_required=human_review_required,
            bedrock_elapsed_ms=bedrock_elapsed_ms,
            total_elapsed_ms=total_elapsed_ms,
            trace=trace,
        )
