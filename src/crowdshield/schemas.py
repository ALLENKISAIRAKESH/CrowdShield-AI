"""Domain models and schemas for CrowdShield AI."""

from __future__ import annotations

from enum import Enum
from typing import Any, List, Optional
from pydantic import BaseModel, Field, field_validator


class DensityLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class FlowTrend(str, Enum):
    STABLE = "stable"
    INCREASING = "increasing"
    DETERIORATING = "deteriorating"
    UNKNOWN = "unknown"


class ExitStatus(str, Enum):
    CLEAR = "clear"
    PARTIALLY_OBSTRUCTED = "partially_obstructed"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


class IncidentSignal(str, Enum):
    NONE_REPORTED = "none_reported"
    POSSIBLE = "possible"
    CONFIRMED_BY_OPERATOR = "confirmed_by_operator"
    UNKNOWN = "unknown"


class DecisionCategory(str, Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class DecisionStatus(str, Enum):
    SUCCESS = "success"
    LOW_CONFIDENCE = "low_confidence"
    UNAVAILABLE = "unavailable"
    ERROR = "error"


class CrowdScenario(BaseModel):
    """Normalized scenario facts provided by an operator or preset."""

    scenario_id: str = Field(..., description="Unique scenario identifier")
    label: str = Field(..., description="Human-readable scenario title")
    density_level: DensityLevel = Field(default=DensityLevel.MODERATE)
    flow_trend: FlowTrend = Field(default=FlowTrend.STABLE)
    exit_status: ExitStatus = Field(default=ExitStatus.CLEAR)
    incident_signal: IncidentSignal = Field(default=IncidentSignal.NONE_REPORTED)
    operator_note: str = Field(default="", max_length=500, description="Optional brief operator notes")
    simulated: bool = Field(default=True, description="Always true for prototype data")

    @field_validator("operator_note")
    @classmethod
    def sanitize_note(cls, value: str) -> str:
        # Strip leading/trailing whitespace and avoid control characters
        cleaned = value.strip()
        if len(cleaned) > 500:
            raise ValueError("Operator note cannot exceed 500 characters")
        return cleaned

    def to_state_summary(self) -> str:
        """Serialize scenario facts into a clear, concise text state for Strands Decider."""
        note_text = f" | Notes: {self.operator_note}" if self.operator_note else ""
        return (
            f"Scenario: {self.label} (ID: {self.scenario_id})\n"
            f"Facts: Density={self.density_level.value}, "
            f"FlowTrend={self.flow_trend.value}, "
            f"ExitStatus={self.exit_status.value}, "
            f"IncidentSignal={self.incident_signal.value}{note_text}"
        )


class DecisionResult(BaseModel):
    """Structured decision output from Strands Decider with confidence and threshold gate."""

    status: DecisionStatus = Field(..., description="Status of the decision processing")
    decision: Optional[str] = Field(default=None, description="Actual decision label (NORMAL, WARNING, CRITICAL) or None")
    confidence: Optional[float] = Field(default=None, description="Model-calibrated confidence score (0.0 to 1.0)")
    threshold: float = Field(default=0.70, description="Configured minimum confidence threshold for automated action")
    elapsed_ms: Optional[float] = Field(default=None, description="Decider API roundtrip latency in ms")
    source: str = Field(default="strands-decider-2B", description="Origin of decision (decider or fallback)")
    error_summary: Optional[str] = Field(default=None, description="Non-secret error description if unavailable or error")
    raw_probabilities: Optional[dict[str, float]] = Field(default=None, description="All class probabilities if available")


class TraceEvent(BaseModel):
    """Detailed audit trace event capturing a distinct stage in the decision lifecycle."""

    timestamp: str = Field(..., description="ISO 8601 or formatted timestamp")
    stage: str = Field(..., description="Pipeline stage name")
    message: str = Field(..., description="Short explanation of step")
    details: Optional[dict[str, Any]] = Field(default=None, description="Metadata associated with stage")


class BedrockResponseSchema(BaseModel):
    """Target structured schema for Amazon Bedrock agent generation."""

    summary: str = Field(..., description="Fact-grounded rationale for the decision")
    recommended_steps: List[str] = Field(default_factory=list, description="Actionable checklist for the human operator")
    human_review_required: bool = Field(default=False, description="Whether human review is indicated")
    limitations: str = Field(
        default="Based on simulated inputs; not a certified safety assessment.",
        description="Disclaimer on prototype boundaries"
    )


class AnalysisResult(BaseModel):
    """Complete end-to-end outcome combining scenario, Decider output, Bedrock generation, and audit trace."""

    scenario: CrowdScenario
    decision_result: DecisionResult
    explanation: Optional[str] = None
    recommended_steps: List[str] = Field(default_factory=list)
    human_review_required: bool = False
    bedrock_elapsed_ms: Optional[float] = None
    total_elapsed_ms: Optional[float] = None
    trace: List[TraceEvent] = Field(default_factory=list)
