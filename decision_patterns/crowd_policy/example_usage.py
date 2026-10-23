"""Minimal example showing how to invoke the Crowd Policy Decision pattern (#policy)."""

import json
from decision_patterns.crowd_policy.decision import CrowdPolicyDecider

def main():
    # 1. Instantiate the Decider client with default or custom endpoint
    decider = CrowdPolicyDecider(url="http://127.0.0.1:8099", default_threshold=0.75)

    # 2. Prepare the crowd situation state
    simulated_state = (
        "Scenario: North Exit Bottleneck\n"
        "Facts: Density=very_high, FlowTrend=deteriorating, "
        "ExitStatus=blocked, IncidentSignal=confirmed_by_operator | Notes: Gate B blocked"
    )

    print("Evaluating crowd situation state with Strands Decider 2B...")
    # 3. Call the typed policy classification
    result = decider.evaluate(simulated_state)

    print("\nDecision Result:")
    print(json.dumps(result, indent=2))

    # 4. Inspect status and confidence gate
    if result["status"] == "success":
        print(f"\n[ACTIONABLE] Policy Decision: {result['decision']} (Confidence: {result['confidence']:.2%})")
    elif result["status"] == "low_confidence":
        print(f"\n[NEEDS HUMAN REVIEW] Confidence ({result['confidence']:.2%}) below threshold ({result['threshold']:.2%})")
    else:
        print(f"\n[FALLBACK / REVIEW REQUIRED] Status: {result['status']} - {result['error_summary']}")

if __name__ == "__main__":
    main()
