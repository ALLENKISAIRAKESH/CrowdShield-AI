# 🛡️ CrowdShield AI: Decision-First Crowd Safety Agent

> **Submission for the AWS Builder Center Agent Experience Hackathon**  
> **Tags:** `#strands-decider-2b` | `#policy`  
> **License:** [MIT](LICENSE)

CrowdShield AI is an experimental decision-support assistant demonstrating a **decision-first architecture** for simulated crowd safety scenarios. 

It uses **Strands Decider 2B** to perform fast, typed policy classifications (`NORMAL`, `WARNING`, `CRITICAL`) with calibrated confidence scores, and an **Amazon Bedrock-backed Strands Agent** to synthesize grounded explanations and actionable checklists for trained human operators.

---

## 🌟 Key Features
- **Typed Decision Model**: Fast, calibrated choice classification via `Strands Decider 2B` (`#strands-decider-2b`).
- **Policy Classification Pattern**: Reusable decision pattern (`#policy`) packaged in `decision_patterns/crowd_policy/`.
- **Generative Grounding**: Amazon Bedrock-powered Strands Agent generating 3–5 step operator checklists strictly grounded on scenario telemetry.
- **Safety Confidence Gating**: Automatic escalation to human review when confidence falls below the configurable threshold.
- **Operations Dashboard**: Dark navy Streamlit interface with clear status badges, audit traces, and session JSON exports.
- **Strict Separation of Concerns**: Decider makes the policy decision; Bedrock explains it and creates the checklist. Bedrock cannot alter the Decider label.

---

## 🏗️ Architecture

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
          │                                         │
          └───────────────────┬─────────────────────┘
                              │
                              ▼
            [Amazon Bedrock + Strands Agent]
          Generates explanation & checklist
                              │
                              ▼
         [Streamlit Operations Dashboard & Audit Trace]
```

---

## 🚀 Quickstart (Windows PowerShell)

### 1. Prerequisites
- Python 3.11 or 3.12
- AWS Credentials configured with Amazon Bedrock model access (e.g. `anthropic.claude-3-haiku-20240307-v1:0`)

### 2. Setup Environment
```powershell
# Clone the repository
git clone https://github.com/ALLENKISAIRAKESH/CrowdShield-AI.git
cd CrowdShield-AI

# Install dependencies
py -3.11 -m pip install -r requirements.txt

# Create local environment config
Copy-Item .env.example .env
```

### 3. (Optional) Run Strands Decider 2B Server Locally
```powershell
strands-decider serve StrandsAgents/strands-decider-2B-qwen3.5-v1-2610 --port 8099
```
*Note: If the server is offline, CrowdShield AI automatically activates its deterministic fallback mode and marks the trace accordingly without failing.*

### 4. Launch the Dashboard
```powershell
py -3.11 -m streamlit run app.py
```

### 5. Run the Test Suite
```powershell
py -3.11 -m pytest tests -v
```

---

## 📦 Reusable Decision Pattern (`#policy`)

The crowd policy classification pattern is packaged as an independent module in [`decision_patterns/crowd_policy/`](decision_patterns/crowd_policy/):
- `question_definition.py`: Exact typed question payload and criteria definitions.
- `decision.py`: Robust client handling timeouts, error recovery, and confidence threshold gates.
- `example_usage.py`: Minimal standalone usage script.

---

## 📂 Repository Structure
```
crowdshield-ai/
├── app.py                     # Streamlit Operations Dashboard
├── README.md                  # Project overview and quickstart
├── LICENSE                    # MIT Open-Source License
├── requirements.txt           # Project dependencies
├── .env.example               # Configuration template
├── .gitignore                 # Secrets and build ignore rules
├── docs/                      # Documentation and hackathon assets
│   ├── architecture.md        # Detailed system design
│   ├── demo-script.md         # 3-minute video recording script
│   ├── builder-center-article-draft.md # Builder Center publication draft
│   └── limitations.md         # Safety boundaries and non-goals
├── decision_patterns/
│   └── crowd_policy/          # Reusable decision recipe (#policy)
│       ├── README.md
│       ├── question_definition.py
│       ├── decision.py
│       └── example_usage.py
├── src/
│   └── crowdshield/           # Application implementation
│       ├── __init__.py
│       ├── config.py
│       ├── schemas.py
│       ├── scenarios.py
│       ├── orchestrator.py
│       ├── decider_client.py
│       ├── bedrock_agent.py
│       └── ui_components.py
└── tests/                     # 100% passing test suite
    ├── test_scenarios.py
    ├── test_confidence_policy.py
    ├── test_decider_response.py
    ├── test_error_handling.py
    └── test_result_schema.py
```

---

## ⚠️ Limitations & Ethics
- **Synthetic Data**: Operates on simulated scenario facts only. Does NOT connect to physical cameras, biometric systems, or CCTV.
- **No Direct Dispatch**: Does not interface with emergency 911 dispatch or automated venue door locks.
- **Human in the Loop**: Results are advisory recommendations for trained human operators.
- See [`docs/limitations.md`](docs/limitations.md) for complete boundary statements.
