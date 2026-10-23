# CrowdShield AI: Operational Limitations and Prototype Boundaries

CrowdShield AI is developed as an experimental technology demonstration for the **AWS Builder Center Agent Experience Hackathon**.

### Explicit Boundaries
1. **Simulated Data Only**: The system processes operator-entered facts or predefined scenario presets. It does NOT consume live video streams, CCTV cameras, or computer vision sensors.
2. **No Automated Dispatch or Actuation**: The system does NOT send automated dispatch orders to 911/emergency responders, nor does it control physical turnstiles, fire doors, or venue alarms.
3. **No Biometric or Personal Data**: CrowdShield AI does not collect, analyze, or store personally identifiable information (PII), facial embeddings, or demographic data.
4. **Not Safety Certified**: CrowdShield AI has not been evaluated or certified under ISO, NFPA, or municipal life-safety standards. It must never be used as a standalone or primary safety monitoring system in real venues.
5. **Confidence Interpretation**: Model confidence scores reflect internal model calibration on test distributions; they do not represent actuarial or physical crowd crush probabilities.
