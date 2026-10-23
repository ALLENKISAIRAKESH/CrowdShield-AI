# CrowdShield AI: System Architecture

## Overview
CrowdShield AI demonstrates a **decision-first agentic architecture** for operational decision support in simulated crowd-safety environments.

Rather than delegating high-stakes policy classification to unstructured text prompts in a large language model, the system introduces a specialized decision model—**Strands Decider 2B**—as an authoritative System One classification engine. An **Amazon Bedrock-backed Strands Agent** then acts as a System Two component, grounding its explanation and action plan strictly upon the structured decision outcome.

```
┌─────────────────────────────────────────────────────────────┐
│                      Operator Input                         │
│  (Scenario Presets or Custom Crowd Density / Egress Inputs) │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Domain Normalization                      │
│             CrowdScenario (Pydantic Schema)                 │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Stage 1: Strands Decider 2B                     │
│       Typed Policy Classification (POST /v1/systemone)      │
│   Options: NORMAL | WARNING | CRITICAL + Confidence Score   │
└──────────────────────────────┬──────────────────────────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
    [Confidence >= Threshold]       [Confidence < Threshold / Error]
      Status: SUCCESS                 Status: LOW_CONFIDENCE / UNAVAILABLE
               │                               │
               └───────────────┬───────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Stage 2: Amazon Bedrock Agent                   │
│           (Strands Agent SDK + Bedrock Runtime)             │
│   Produces fact-grounded explanation + operator checklist   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             Presentation & Audit Logging                    │
│    Streamlit Operations Dashboard + Chronological Trace     │
└─────────────────────────────────────────────────────────────┘
```

## Architectural Layers
1. **Presentation Layer (`app.py`, `src/crowdshield/ui_components.py`)**:
   - Streamlit dashboard styled after modern operations command consoles.
   - Distinct badges separating Decider output from Bedrock generated text.
   - Interactive threshold control and JSON report exporter.

2. **Orchestration Layer (`src/crowdshield/orchestrator.py`)**:
   - Manages state serialization, execution order, confidence gates, and timing measurements.

3. **Decision Layer (`decision_patterns/crowd_policy/`, `src/crowdshield/decider_client.py`)**:
   - Reusable `#policy` pattern implementation.
   - Dispatches structured choice questions via HTTP to Strands Decider 2B.
   - Evaluates calibrated confidence scores against a user-configured threshold.

4. **Generative Layer (`src/crowdshield/bedrock_agent.py`)**:
   - Driven by Strands Agents SDK and Amazon Bedrock (`anthropic.claude-3-haiku-20240307-v1:0` or compatible).
   - Constrained by system prompts to prevent modifying or hallucinating decisions.

5. **Domain Layer (`src/crowdshield/schemas.py`)**:
   - Pydantic models for strict data contracts, validation, and JSON serialization.
