"""Unit tests for scenario validation and presets."""

import pytest
from src.crowdshield.schemas import (
    CrowdScenario,
    DensityLevel,
    ExitStatus,
    FlowTrend,
    IncidentSignal,
)
from src.crowdshield.scenarios import PRESET_SCENARIOS, get_preset_scenario


def test_preset_scenarios_count_and_validity():
    """Verify at least 3 required presets exist and have valid fields."""
    assert len(PRESET_SCENARIOS) >= 3
    assert "routine_movement" in PRESET_SCENARIOS
    assert "growing_congestion" in PRESET_SCENARIOS
    assert "blocked_exit" in PRESET_SCENARIOS

    for key, scenario in PRESET_SCENARIOS.items():
        assert scenario.scenario_id
        assert scenario.label
        assert scenario.simulated is True
        summary = scenario.to_state_summary()
        assert scenario.label in summary
        assert scenario.density_level.value in summary


def test_scenario_note_length_limit():
    """Ensure operator notes exceeding 500 characters trigger a validation error."""
    long_note = "A" * 501
    with pytest.raises(ValueError):
        CrowdScenario(
            scenario_id="invalid_test",
            label="Too Long Note",
            operator_note=long_note,
        )


def test_scenario_enum_validation():
    """Ensure invalid enum values are caught at validation time."""
    with pytest.raises(ValueError):
        CrowdScenario(
            scenario_id="invalid_enum",
            label="Bad Enum",
            density_level="super_extreme_crowd",  # type: ignore
        )
