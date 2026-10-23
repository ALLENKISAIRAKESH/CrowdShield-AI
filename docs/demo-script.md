# CrowdShield AI: 3-Minute Video Demo Script

**Total Target Duration:** 2 minutes 45 seconds (Under the mandatory 3:00 hackathon limit)  
**Required Tags:** `#strands-decider-2b` and `#policy`

---

### Segment 1: Introduction & The Core Problem (0:00 – 0:25)
- **Visual:** Full view of the CrowdShield AI Dashboard in dark operations theme with the "⚠️ SIMULATED DATA" badge visible.
- **Narrator Voiceover:**
  > "Welcome to CrowdShield AI—a decision-first agent for simulated crowd safety built for the AWS Builder Center Agent Experience Hackathon. In event operations, dispatchers repeatedly make critical policy judgements. Relying solely on large language models for these decisions introduces latency, cost, and hallucination risks. CrowdShield AI uses Strands Decider 2B for fast, typed policy classification, followed by an Amazon Bedrock-backed Strands Agent to generate actionable operator checklists."

---

### Segment 2: Scenario Selection & Typed Policy Decision (0:25 – 1:00)
- **Visual:** Cursor selects "Growing Congestion" preset, points out the high crowd density and deteriorating flow indicators, then clicks **"Analyze Scenario"**.
- **Narrator Voiceover:**
  > "Here we load a simulated scenario of surging density at a concert egress gate. When we click 'Analyze Scenario', the orchestrator serializes the normalized state facts and sends them to Strands Decider 2B. Notice the result: Decider returns a typed category—WARNING—with a calibrated confidence score of 89% in under 150 milliseconds. Crucially, this classification was made by Decider 2B, not hardcoded text or LLM improvisation."

---

### Segment 3: Generative Explanation via Amazon Bedrock (1:00 – 1:35)
- **Visual:** Focus on the right-hand card: Amazon Bedrock Action Plan and recommended checklist.
- **Narrator Voiceover:**
  > "Next, our Strands Agent, powered by Amazon Bedrock, consumes the structured decision and scenario facts. It explains why the situation warrants a WARNING and produces a 3-step practical checklist for human stewards on the ground: verifying gate locks and easing bottlenecks. The Bedrock agent is strictly constrained: it cannot alter or second-guess the Decider's classification."

---

### Segment 4: Confidence Gating & Safety Fallback (1:35 – 2:10)
- **Visual:** Load "Ambiguous Conflicting Report" or raise the threshold slider to 90%. Click **"Analyze Scenario"**.
- **Narrator Voiceover:**
  > "What happens when inputs are ambiguous or model confidence is low? Let's run this conflicting report. The Decider confidence falls below our safety threshold. Instead of faking certainty, the confidence gate immediately trips into 'NEEDS HUMAN REVIEW'. The Bedrock agent prominently highlights this uncertainty, instructing operators to perform physical verification."

---

### Segment 5: Reusable Decision Pattern & Conclusion (2:10 – 2:50)
- **Visual:** Switch briefly to the `decision_patterns/crowd_policy/` directory in VS Code / IDE showing `question_definition.py` and `README.md`.
- **Narrator Voiceover:**
  > "We packaged this exact workflow as a standalone reusable decision pattern under the `#policy` tag. Any developer can copy `decision_patterns/crowd_policy` and integrate typed policy classification into their own Strands agents in under 20 lines of code. The code is open source under the MIT license on GitHub."
- **Visual:** Return to the dashboard and highlight the disclaimer footer.
- **Narrator Voiceover:**
  > "Thank you! CrowdShield AI proves how decision models and generative agents collaborate for safer, faster human-in-the-loop workflows."
