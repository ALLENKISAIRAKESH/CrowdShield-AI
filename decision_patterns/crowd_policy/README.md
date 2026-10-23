# Reusable Decision Pattern: Crowd Policy Classification (`#policy`)

This package provides a standalone, production-grade reusable decision pattern for classifying operational crowd safety situations using **Strands Decider 2B** before passing context downstream to an agent.

## Pattern Metadata
- **Pattern Name**: Policy classification
- **Tag**: `#policy` & `#strands-decider-2b`
- **Model Target**: `StrandsAgents/strands-decider-2B-qwen3.5-v1-2610`
- **Wire Protocol**: Strands Decider `POST /v1/systemone`
- **Output**: Typed choice (`NORMAL`, `WARNING`, `CRITICAL`), model confidence score, roundtrip latency, and confidence threshold gate.

---

## Why Use a Decision Model Here?
A general LLM can write creative prose, but when an operations dashboard needs an immediate, deterministic, typed category with calibrated confidence, a decision model is:
1. **Faster**: Sub-200ms evaluation on GPU/CPU vs multi-second LLM streaming.
2. **Deterministic & Constrained**: Only returns valid pre-configured categories (`NORMAL`, `WARNING`, `CRITICAL`).
3. **Calibrated**: Directly exposes calibrated confidence scores without prompt negotiation.

---

## Question Definition & Rubric

```json
{
  "type": "choice",
  "instructions": "Choose the most appropriate response category for the reported crowd safety situation.",
  "criteria": {
    "NORMAL": "Routine crowd flow, low or manageable density, all egress routes clear, and no distress or incident reported.",
    "WARNING": "High crowd density, congestion forming, deteriorating flow rate, or potential bottleneck/hazard requiring heightened vigilance.",
    "CRITICAL": "Extreme crowd density/crush risk, blocked evacuation exits, confirmed operator distress signal, or immediate danger requiring urgent intervention."
  }
}
```

---

## Wire Protocol & Gating Workflow

```
[Simulated Scenario Facts]
          │
          ▼
 [Strands Decider 2B]  ──> HTTP POST /v1/systemone
          │
          ▼
   { choice, confidence, latency_ms }
          │
          ├─────────────────────────────────────────┐
          │                                         │
 [confidence >= threshold]                [confidence < threshold OR error]
          │                                         │
          ▼                                         ▼
   Status: SUCCESS                        Status: LOW_CONFIDENCE / UNAVAILABLE
   Actionable Decision                     Escalate to Human Operator Review
```

---

## Quickstart

```python
from decision_patterns.crowd_policy.decision import CrowdPolicyDecider

decider = CrowdPolicyDecider(url="http://127.0.0.1:8099", default_threshold=0.70)

state = "Density=high, Flow=deteriorating, Exit=partially_obstructed"
result = decider.evaluate(state)

if result["status"] == "success":
    print("Decision:", result["decision"], "Confidence:", result["confidence"])
else:
    print("Review Required:", result["error_summary"])
```

---

## Running the Standalone Tests
```powershell
py -3.11 -m pytest tests/test_confidence_policy.py tests/test_decider_response.py
```
