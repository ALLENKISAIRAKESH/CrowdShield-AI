"""Reusable Decision Pattern: Crowd Policy Classification (#policy).

Defines the exact typed question and criteria schema for Strands Decider 2B.
"""

from __future__ import annotations

from typing import Any, Dict

POLICY_QUESTION_NAME = "crowd_policy_classification"

# Official Strands Decider choice question schema with explicit criteria for each category
POLICY_CRITERIA: Dict[str, str] = {
    "NORMAL": (
        "Routine crowd flow, low or manageable density, all egress routes clear, "
        "and no distress or incident reported."
    ),
    "WARNING": (
        "High crowd density, congestion forming, deteriorating flow rate, "
        "or potential bottleneck/hazard requiring heightened vigilance."
    ),
    "CRITICAL": (
        "Extreme crowd density/crush risk, blocked evacuation exits, confirmed "
        "operator distress signal, or immediate danger requiring urgent intervention."
    ),
}

POLICY_INSTRUCTIONS = (
    "Choose the most appropriate response category for the reported crowd safety situation."
)


def get_crowd_policy_question() -> Dict[str, Any]:
    """Build the official Strands Decider choice question payload.

    Returns a dict adhering to the official Strands Decider wire protocol:
    {
        "type": "choice",
        "instructions": "...",
        "criteria": { "NORMAL": "...", "WARNING": "...", "CRITICAL": "..." }
    }
    """
    return {
        "type": "choice",
        "instructions": POLICY_INSTRUCTIONS,
        "criteria": dict(POLICY_CRITERIA),
    }
