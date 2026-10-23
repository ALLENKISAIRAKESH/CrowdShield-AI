"""CrowdShield AI: Decision-First Crowd Safety Agent — Streamlit Dashboard."""

from __future__ import annotations

import datetime
import json
import streamlit as st

from src.crowdshield.config import settings
from src.crowdshield.orchestrator import CrowdShieldOrchestrator
from src.crowdshield.scenarios import (
    PRESET_SCENARIOS,
    get_preset_scenario,
    list_preset_options,
)
from src.crowdshield.schemas import (
    CrowdScenario,
    DecisionStatus,
    DensityLevel,
    ExitStatus,
    FlowTrend,
    IncidentSignal,
)
from src.crowdshield.ui_components import (
    apply_custom_styles,
    render_decision_badge,
    render_footer_disclaimer,
    render_header,
    render_trace_timeline,
)

st.set_page_config(
    page_title="CrowdShield AI — Decision-First Crowd Safety Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_styles()

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = []

if "latest_result" not in st.session_state:
    st.session_state.latest_result = None

# Initialize orchestrator
orchestrator = CrowdShieldOrchestrator()

# Check connectivity
try:
    decider_health = orchestrator.decider_client.decider.check_health()
    decider_conn = "Online (Local/Host)"
except Exception:
    decider_conn = "Offline (Fallback Enabled)"

bedrock_conn = "Connected (AWS Bedrock)"

# Top banner
render_header(decider_status=decider_conn, bedrock_status=bedrock_conn)
st.write("")

# Sidebar: Scenario Selection & Controls
with st.sidebar:
    st.markdown("### ⚙️ Scenario Control")
    preset_choices = list_preset_options()
    preset_labels = [p["label"] for p in preset_choices]
    selected_label = st.selectbox("Load Scenario Preset:", preset_labels)

    selected_key = next(p["key"] for p in preset_choices if p["label"] == selected_label)
    preset_data = get_preset_scenario(selected_key)

    st.markdown("---")
    st.markdown("#### Scenario Parameters")
    with st.form("scenario_form"):
        title_input = st.text_input("Scenario Title", value=preset_data.label)
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            density = st.selectbox(
                "Crowd Density",
                options=[d.value for d in DensityLevel],
                index=[d.value for d in DensityLevel].index(preset_data.density_level.value),
            )
            flow = st.selectbox(
                "Flow Trend",
                options=[f.value for f in FlowTrend],
                index=[f.value for f in FlowTrend].index(preset_data.flow_trend.value),
            )
        with col_f2:
            exit_stat = st.selectbox(
                "Exit Route Status",
                options=[e.value for e in ExitStatus],
                index=[e.value for e in ExitStatus].index(preset_data.exit_status.value),
            )
            incident = st.selectbox(
                "Incident Signal",
                options=[i.value for i in IncidentSignal],
                index=[i.value for i in IncidentSignal].index(preset_data.incident_signal.value),
            )

        notes = st.text_area("Operator Observations / Field Notes", value=preset_data.operator_note, height=70)
        
        st.markdown("---")
        st.markdown("#### Gate Configuration")
        threshold_val = st.slider(
            "Confidence Review Threshold",
            min_value=0.50,
            max_value=0.95,
            value=settings.confidence_threshold,
            step=0.05,
            help="Decisions below this threshold are routed to human review.",
        )

        submit_btn = st.form_submit_button("🚨 Analyze Scenario", use_container_width=True)

    if st.button("🔄 Reset / Clear History", use_container_width=True):
        st.session_state.history = []
        st.session_state.latest_result = None
        st.rerun()

# Execution on submit
if submit_btn:
    try:
        scenario = CrowdScenario(
            scenario_id=f"custom_{datetime.datetime.utcnow().strftime('%H%M%S')}",
            label=title_input,
            density_level=DensityLevel(density),
            flow_trend=FlowTrend(flow),
            exit_status=ExitStatus(exit_stat),
            incident_signal=IncidentSignal(incident),
            operator_note=notes,
            simulated=True,
        )

        with st.spinner("Step 1: Running Strands Decider 2B policy classification..."):
            result = orchestrator.analyze(
                scenario=scenario,
                confidence_threshold=threshold_val,
            )

        st.session_state.latest_result = result
        st.session_state.history.insert(0, {
            "timestamp": datetime.datetime.utcnow().strftime("%H:%M:%S"),
            "scenario": result.scenario.label,
            "decision": result.decision_result.decision or "N/A",
            "confidence": f"{result.decision_result.confidence:.1%}" if result.decision_result.confidence else "N/A",
            "status": result.decision_result.status.value,
            "latency": f"{result.total_elapsed_ms} ms",
        })
    except Exception as exc:
        st.error(f"Validation or Pipeline Error: {exc}")

# Display results
res = st.session_state.latest_result
if res:
    st.markdown("### 📊 Operational Assessment")
    
    col_res1, col_res2 = st.columns([1, 1])

    with col_res1:
        st.markdown("<div class='decision-card'>", unsafe_allow_html=True)
        st.markdown("#### 1️⃣ Strands Decider 2B Classification")
        st.caption("Typed, calibrated policy classification evaluated before generative reasoning.")
        
        render_decision_badge(res.decision_result)
        
        st.write("")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(
                "Model Confidence",
                f"{res.decision_result.confidence:.1%}" if res.decision_result.confidence else "N/A",
            )
        with c2:
            st.metric("Review Threshold", f"{res.decision_result.threshold:.1%}")
        with c3:
            st.metric(
                "Decider Latency",
                f"{res.decision_result.elapsed_ms} ms" if res.decision_result.elapsed_ms else "N/A",
            )

        if res.decision_result.error_summary:
            st.warning(f"⚠️ **Notice:** {res.decision_result.error_summary}")

        if res.decision_result.raw_probabilities:
            st.markdown("**Probability Distribution:**")
            probs = res.decision_result.raw_probabilities
            st.bar_chart(probs)

        st.markdown("</div>", unsafe_allow_html=True)

    with col_res2:
        st.markdown("<div class='decision-card'>", unsafe_allow_html=True)
        st.markdown("#### 2️⃣ Amazon Bedrock Action Plan")
        st.caption("Synthesized explanation and operator checklist grounded in structured facts.")

        st.markdown(f"**Explanation:**\n{res.explanation}")
        
        st.markdown("**Recommended Operator Checklist:**")
        for i, step in enumerate(res.recommended_steps, 1):
            st.markdown(f"**{i}.** {step}")

        st.write("")
        if res.human_review_required:
            st.error("🚩 **Action Flag:** Mandatory Human Operator Review Required")
        else:
            st.success("✅ **Action Flag:** Automated Policy Clearance — Routine Stewarding")

        c4, c5 = st.columns(2)
        with c4:
            st.metric("Bedrock Latency", f"{res.bedrock_elapsed_ms} ms" if res.bedrock_elapsed_ms else "N/A")
        with c5:
            st.metric("Total End-to-End Latency", f"{res.total_elapsed_ms} ms")

        st.markdown("</div>", unsafe_allow_html=True)

    # Audit Trace
    with st.expander("🔎 View Chronological Audit Decision Trace", expanded=False):
        render_trace_timeline(res.trace)

    # Export Report Button
    st.download_button(
        label="📥 Export Analysis Report (JSON)",
        data=json.dumps(res.model_dump(), indent=2),
        file_name=f"crowdshield_report_{res.scenario.scenario_id}.json",
        mime="application/json",
    )

else:
    st.info("👈 Select a scenario preset or enter custom scenario facts in the sidebar and press **Analyze Scenario** to start.")

# Session history table
if st.session_state.history:
    st.write("")
    st.markdown("### 📋 Current Session History")
    st.dataframe(st.session_state.history, use_container_width=True)

# Footer
render_footer_disclaimer()
