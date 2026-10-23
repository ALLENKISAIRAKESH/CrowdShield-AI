"""Unit tests for Decider question formatting and response parsing."""

from decision_patterns.crowd_policy.question_definition import (
    POLICY_CRITERIA,
    POLICY_QUESTION_NAME,
    get_crowd_policy_question,
)


def test_question_schema_structure():
    """Verify official Strands Decider choice question dictionary format."""
    q = get_crowd_policy_question()
    assert q["type"] == "choice"
    assert "instructions" in q
    assert "criteria" in q
    assert set(q["criteria"].keys()) == {"NORMAL", "WARNING", "CRITICAL"}


def test_question_criteria_explanations():
    """Verify each choice category has substantive distinguishing criteria."""
    for category in ["NORMAL", "WARNING", "CRITICAL"]:
        desc = POLICY_CRITERIA[category]
        assert len(desc) > 20
        assert isinstance(desc, str)
