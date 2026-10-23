"""Predefined scenario presets for CrowdShield AI demonstrations."""

from __future__ import annotations

from typing import Dict, List
from .schemas import (
    CrowdScenario,
    DensityLevel,
    ExitStatus,
    FlowTrend,
    IncidentSignal,
)

PRESET_SCENARIOS: Dict[str, CrowdScenario] = {
    "routine_movement": CrowdScenario(
        scenario_id="preset_01_routine",
        label="Routine Movement",
        density_level=DensityLevel.MODERATE,
        flow_trend=FlowTrend.STABLE,
        exit_status=ExitStatus.CLEAR,
        incident_signal=IncidentSignal.NONE_REPORTED,
        operator_note="Main concourse during standard transition. Normal ingress and egress rates observed.",
        simulated=True,
    ),
    "growing_congestion": CrowdScenario(
        scenario_id="preset_02_congestion",
        label="Growing Congestion",
        density_level=DensityLevel.HIGH,
        flow_trend=FlowTrend.INCREASING,
        exit_status=ExitStatus.CLEAR,
        incident_signal=IncidentSignal.POSSIBLE,
        operator_note="Density surging near north exit gates prior to headliner finale. Bottleneck developing.",
        simulated=True,
    ),
    "blocked_exit": CrowdScenario(
        scenario_id="preset_03_blocked",
        label="Blocked Exit Emergency",
        density_level=DensityLevel.VERY_HIGH,
        flow_trend=FlowTrend.DETERIORATING,
        exit_status=ExitStatus.BLOCKED,
        incident_signal=IncidentSignal.CONFIRMED_BY_OPERATOR,
        operator_note="Service cart obstructing Gate B exit; crowd pressure building, reverse surge reported.",
        simulated=True,
    ),
    "ambiguous_report": CrowdScenario(
        scenario_id="preset_04_ambiguous",
        label="Ambiguous Conflicting Report",
        density_level=DensityLevel.MODERATE,
        flow_trend=FlowTrend.UNKNOWN,
        exit_status=ExitStatus.PARTIALLY_OBSTRUCTED,
        incident_signal=IncidentSignal.UNKNOWN,
        operator_note="Conflicting radio reports regarding corridor C. Visual verification pending.",
        simulated=True,
    ),
}


def get_preset_scenario(preset_key: str) -> CrowdScenario:
    """Retrieve a preset scenario by key, defaulting to routine_movement."""
    return PRESET_SCENARIOS.get(preset_key, PRESET_SCENARIOS["routine_movement"])


def list_preset_options() -> List[Dict[str, str]]:
    """Return options for UI dropdown."""
    return [
        {"key": k, "label": v.label, "id": v.scenario_id}
        for k, v in PRESET_SCENARIOS.items()
    ]
