# CrowdShield AI: A Decision-First Agent for Simulated Crowd Safety

**Author:** CrowdShield AI Team  
**Submission Tags:** `#strands-decider-2b` `#policy`  
**License:** MIT  

---

## 1. Introduction: The Repetitive Decision Problem
In crowd management and venue operations, dispatchers and safety supervisors continuously assess operational telemetry: crowd density spikes, gate ingress/egress transit rates, and steward incident reports. When an anomaly occurs, operators must answer a fundamental policy question:

> *"Does this situation represent routine movement, an operational warning, or an immediate critical emergency?"*

Historically, developers tackling this with AI face a dilemma:
- **Traditional machine learning classifiers** require massive labeled datasets, complex feature engineering, and lack conversational flexibility.
- **Large Language Models (LLMs)** can interpret open-ended scenario facts, but they are relatively slow, expensive for high-frequency polling, and can hallucinate or change classification thresholds unpredictably across turns.

**CrowdShield AI** demonstrates a new architectural approach: **Decision-First Agents**. By placing **Strands Decider 2B**—a small, calibrated "System One" decision model—at the front of the pipeline, we get instant, typed policy classification with calibrated confidence. Only after the decision is locked in do we call an **Amazon Bedrock-powered Strands Agent** to produce natural language explanations and tailored checklists for human stewards.

---

## 2. Why Strands Decider 2B for Policy Classification (`#policy`)
Strands Decider 2B is purpose-built to choose between discrete options or rate items on a scale. 

In CrowdShield AI, we formulated the crowd policy classification as a typed choice question:
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

### Key Advantages Observed:
1. **Speed**: Decider 2B evaluates in 100–150ms, compared to 1500–3000ms for full LLM generative text generation.
2. **Calibrated Confidence**: The response includes calibrated probability distribution across options. We use this directly in our confidence gate: if confidence falls below our threshold (e.g. 70%), the system immediately routes to human review.
3. **No Prompt Drift**: The model is restricted to our exact options (`NORMAL`, `WARNING`, `CRITICAL`), preventing malformed string outputs.

---

## 3. Generative Reasoning with Amazon Bedrock & Strands Agents
Once Decider 2B returns a classified policy category and passes the confidence gate, the state and decision are passed to an Amazon Bedrock-backed Strands Agent (`anthropic.claude-3-haiku-20240307-v1:0` or compatible).

The Bedrock agent is strictly instructed:
- **Authoritative Decision**: It must treat the Decider's classification as ground truth and cannot alter it.
- **Factual Grounding**: It explains the classification solely using provided scenario facts (density, flow trend, exit status).
- **Practical Checklist**: It synthesizes a concise, 3-to-5 point operational checklist for trained human personnel.
- **Uncertainty Prominence**: If the gate detected low confidence, the agent highlights the uncertainty and mandates human inspection.

---

## 4. Reusable Decision Pattern (`#policy`)
We extracted and published the decision workflow as an independent, reusable recipe in `decision_patterns/crowd_policy/`:
- `question_definition.py`: The exact typed schema and criteria.
- `decision.py`: The HTTP client communicating with `POST /v1/systemone` and applying the threshold gate.
- `example_usage.py`: A self-contained script demonstrating invocation in under 20 lines.

Any developer building on the Strands framework can drop this folder into their project to add reliable crowd policy gating to their agents.

---

## 5. Architectural Safeguards and Limitations
CrowdShield AI is explicitly an experimental decision-support prototype. It operates entirely on synthetic data.
- **No Direct Dispatch**: The system never triggers automated sirens, locks, or emergency services.
- **No Computer Vision**: It does not process live CCTV, facial recognition, or biometric feeds.
- **Human-in-the-Loop**: The operator always retains final decision authority.

---

## 6. Conclusion
By pairing the fast, calibrated classification of Strands Decider 2B with the rich conversational synthesis of Amazon Bedrock, CrowdShield AI provides a blueprint for reliable, high-speed agentic decision support in safety-critical operations.
