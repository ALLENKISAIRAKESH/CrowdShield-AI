"""Amazon Bedrock-backed Strands Agent for generative explanation and action planning."""

from __future__ import annotations

import datetime
import json
import time
from typing import Any, Dict, List, Optional, Tuple

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from .config import settings
from .schemas import (
    BedrockResponseSchema,
    CrowdScenario,
    DecisionResult,
    DecisionStatus,
    TraceEvent,
)

SYSTEM_PROMPT = """You are CrowdShield AI, an experimental decision-support assistant for simulated crowd-safety scenarios. You are not an emergency service and must not claim to diagnose a real crowd condition.

The structured Strands Decider result is authoritative for the displayed decision label. Do not change, relabel, or fabricate that result. Explain the result using only the scenario facts and decision metadata provided.

Give a concise explanation and a practical checklist of 3 to 5 steps for a trained human operator. If the decision status is low_confidence, unavailable, or error, make uncertainty prominent and recommend human review. Never claim that the system has contacted responders or performed an external action. Do not invent confidence scores, sensor readings, incidents, or measurements.

Respond strictly in valid JSON format matching this schema:
{
  "summary": "Concise factual explanation of the decision based solely on provided facts",
  "recommended_steps": [
    "Suggested human operator action 1",
    "Suggested human operator action 2",
    "Suggested human operator action 3"
  ],
  "human_review_required": true or false,
  "limitations": "Based on simulated inputs; not a certified safety assessment."
}
"""


class BedrockAgent:
    """Invokes Amazon Bedrock to explain the Strands Decider decision and suggest operator steps."""

    def __init__(
        self,
        region_name: str = settings.aws_region,
        model_id: str = settings.bedrock_model_id,
        profile_name: Optional[str] = settings.aws_profile,
    ) -> None:
        self.region_name = region_name
        self.model_id = model_id
        self.profile_name = profile_name
        self._bedrock_client = None

    def _get_client(self):
        if self._bedrock_client is None:
            session = (
                boto3.Session(profile_name=self.profile_name, region_name=self.region_name)
                if self.profile_name
                else boto3.Session(region_name=self.region_name)
            )
            self._bedrock_client = session.client("bedrock-runtime")
        return self._bedrock_client

    def generate_plan(
        self,
        scenario: CrowdScenario,
        decision_result: DecisionResult,
    ) -> Tuple[BedrockResponseSchema, Optional[float], List[TraceEvent], Optional[str]]:
        """Generate explanation and response plan using Bedrock.

        Returns:
            (BedrockResponseSchema, elapsed_ms, trace_events, error_summary)
        """
        trace: List[TraceEvent] = []
        user_prompt = (
            f"SCENARIO FACTS:\n"
            f"- Title: {scenario.label}\n"
            f"- Density Level: {scenario.density_level.value}\n"
            f"- Flow Trend: {scenario.flow_trend.value}\n"
            f"- Exit Status: {scenario.exit_status.value}\n"
            f"- Incident Signal: {scenario.incident_signal.value}\n"
            f"- Operator Notes: {scenario.operator_note or 'None'}\n\n"
            f"STRANDS DECIDER RESULT:\n"
            f"- Decision Label: {decision_result.decision or 'N/A'}\n"
            f"- Calibrated Confidence: {decision_result.confidence or 'N/A'}\n"
            f"- Decision Status: {decision_result.status.value}\n"
            f"- Threshold: {decision_result.threshold}\n\n"
            f"Please synthesize the explanation and operational recommendations according to the schema."
        )

        trace.append(
            TraceEvent(
                timestamp=datetime.datetime.utcnow().isoformat() + "Z",
                stage="bedrock_agent_request",
                message=f"Dispatching context to Amazon Bedrock ({self.model_id})",
                details={
                    "model_id": self.model_id,
                    "region": self.region_name,
                    "decision_label": decision_result.decision,
                },
            )
        )

        start_time = time.perf_counter()
        try:
            client = self._get_client()

            # Handle Anthropic Claude payload via Bedrock Converse or invoke_model
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 800,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": user_prompt}],
                "temperature": 0.2,
            }

            resp = client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json",
            )
            raw_body = json.loads(resp["body"].read().decode("utf-8"))
            elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

            text_output = ""
            if "content" in raw_body and isinstance(raw_body["content"], list):
                text_output = "".join(part.get("text", "") for part in raw_body["content"])
            elif "completion" in raw_body:
                text_output = raw_body["completion"]

            # Parse JSON from model output
            parsed_json = self._extract_json(text_output)
            plan = BedrockResponseSchema(**parsed_json)

            trace.append(
                TraceEvent(
                    timestamp=datetime.datetime.utcnow().isoformat() + "Z",
                    stage="bedrock_agent_response",
                    message="Successfully generated explanation and action checklist from Bedrock",
                    details={"elapsed_ms": elapsed_ms, "steps_count": len(plan.recommended_steps)},
                )
            )
            return plan, elapsed_ms, trace, None

        except (ClientError, BotoCoreError, Exception) as exc:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            err_msg = f"Bedrock invocation failed ({type(exc).__name__}): {exc}"

            trace.append(
                TraceEvent(
                    timestamp=datetime.datetime.utcnow().isoformat() + "Z",
                    stage="bedrock_agent_fallback",
                    message=f"Bedrock service unavailable or error; using safe fallback explanation. ({err_msg})",
                    details={"elapsed_ms": elapsed_ms, "error": err_msg},
                )
            )

            # Generate safe deterministic fallback plan preserving the Decider outcome
            fallback_plan = self._generate_fallback_plan(scenario, decision_result)
            return fallback_plan, elapsed_ms, trace, err_msg

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract and parse JSON safely from model response."""
        text = text.strip()
        # Find first '{' and last '}'
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start : end + 1])
        return json.loads(text)

    def _generate_fallback_plan(
        self, scenario: CrowdScenario, decision_result: DecisionResult
    ) -> BedrockResponseSchema:
        """Deterministic fallback explanation when Bedrock is offline or credentials are missing."""
        if decision_result.status == DecisionStatus.SUCCESS:
            decision = decision_result.decision or "NORMAL"
            if decision == "CRITICAL":
                return BedrockResponseSchema(
                    summary=(
                        f"CRITICAL classification indicated based on high crowd density and "
                        f"exit status ({scenario.exit_status.value}). Immediate human verification required."
                    ),
                    recommended_steps=[
                        "Dispatch stewards to clear obstructed egress routes immediately.",
                        "Halt incoming pedestrian flow toward affected sector.",
                        "Notify event command center and prepare secondary evacuation paths.",
                    ],
                    human_review_required=True,
                    limitations="Generated via deterministic safety fallback (Bedrock offline); simulated data.",
                )
            elif decision == "WARNING":
                return BedrockResponseSchema(
                    summary=(
                        f"WARNING classification indicated. Flow trend is {scenario.flow_trend.value} "
                        f"with {scenario.density_level.value} density. Bottleneck prevention advised."
                    ),
                    recommended_steps=[
                        "Increase monitoring frequency at major transit intersections.",
                        "Verify exit gates remain unlocked and unobstructed.",
                        "Deploy ground team to ease localized crowd bottlenecks.",
                    ],
                    human_review_required=False,
                    limitations="Generated via deterministic safety fallback (Bedrock offline); simulated data.",
                )
            else:
                return BedrockResponseSchema(
                    summary=(
                        f"NORMAL classification indicated. Egress routes are {scenario.exit_status.value} "
                        f"and crowd density is {scenario.density_level.value}."
                    ),
                    recommended_steps=[
                        "Maintain standard scheduled perimeter rounds.",
                        "Monitor ingress/egress transit rates at planned checkpoints.",
                    ],
                    human_review_required=False,
                    limitations="Generated via deterministic safety fallback (Bedrock offline); simulated data.",
                )
        else:
            return BedrockResponseSchema(
                summary=(
                    f"Decision status is '{decision_result.status.value}'. Automated policy evaluation "
                    f"cannot be verified with high confidence. Human operator assessment is mandatory."
                ),
                recommended_steps=[
                    "Conduct immediate direct visual inspection of the area.",
                    "Review recent radio logs for conflicting reports.",
                    "Verify automated sensor connectivity and reporting endpoints.",
                ],
                human_review_required=True,
                limitations="Generated via deterministic safety fallback; simulated data.",
            )
