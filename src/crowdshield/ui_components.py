"""Custom styling and presentation components for Streamlit operations dashboard."""

from __future__ import annotations

import json
from typing import Any, Dict, List
import streamlit as st

from .schemas import AnalysisResult, DecisionResult, DecisionStatus, TraceEvent

CUSTOM_CSS = """
<style>
/* Operations Dashboard Theme: Dark Navy with Teal/Cyan Accents */
.stApp {
    background-color: #0c121e;
    color: #e2e8f0;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
}

/* Header badge styling */
.sim-pill {
    background: rgba(245, 158, 11, 0.15);
    border: 1px solid #f59e0b;
    color: #fcd34d;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    display: inline-block;
    margin-left: 10px;
}

.model-badge {
    background: rgba(14, 165, 233, 0.15);
    border: 1px solid #0284c7;
    color: #38bdf8;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
}

/* Decision outcome cards */
.decision-card {
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 20px;
    background: #131d31;
    border: 1px solid #1e293b;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
}

.badge-normal {
    background: rgba(16, 185, 129, 0.2);
    border: 1px solid #10b981;
    color: #34d399;
    padding: 6px 14px;
    border-radius: 6px;
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    display: inline-block;
}

.badge-warning {
    background: rgba(245, 158, 11, 0.2);
    border: 1px solid #f59e0b;
    color: #fbbf24;
    padding: 6px 14px;
    border-radius: 6px;
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    display: inline-block;
}

.badge-critical {
    background: rgba(239, 68, 68, 0.2);
    border: 1px solid #ef4444;
    color: #f87171;
    padding: 6px 14px;
    border-radius: 6px;
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    display: inline-block;
}

.badge-review {
    background: rgba(249, 115, 22, 0.2);
    border: 1px solid #f97316;
    color: #fb923c;
    padding: 6px 14px;
    border-radius: 6px;
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    display: inline-block;
}

.trace-item {
    padding: 8px 12px;
    border-left: 3px solid #0284c7;
    background: #0f172a;
    margin-bottom: 8px;
    border-radius: 0 6px 6px 0;
    font-size: 0.85rem;
}

.disclaimer-banner {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid #334155;
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 0.8rem;
    color: #94a3b8;
    margin-top: 30px;
}
</style>
"""


def apply_custom_styles() -> None:
    """Inject custom styles into the Streamlit app."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_header(decider_status: str, bedrock_status: str) -> None:
    """Render top operational banner."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(
            "## 🛡️ CrowdShield AI <span class='sim-pill'>⚠️ SIMULATED DATA</span>",
            unsafe_allow_html=True,
        )
        st.caption("Decision-First Crowd Safety Agent — Powered by Strands Decider 2B & Amazon Bedrock")
    with col2:
        st.markdown(
            f"<div style='text-align: right;'>"
            f"<span class='model-badge'>Decider: {decider_status}</span><br>"
            f"<span class='model-badge' style='margin-top:4px; display:inline-block;'>Bedrock: {bedrock_status}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )


def render_decision_badge(decision_result: DecisionResult) -> None:
    """Render the primary typed decision badge from Decider."""
    status = decision_result.status
    decision = decision_result.decision

    if status == DecisionStatus.SUCCESS:
        if decision == "NORMAL":
            st.markdown("<span class='badge-normal'>🟢 NORMAL</span>", unsafe_allow_html=True)
        elif decision == "WARNING":
            st.markdown("<span class='badge-warning'>🟡 WARNING</span>", unsafe_allow_html=True)
        elif decision == "CRITICAL":
            st.markdown("<span class='badge-critical'>🔴 CRITICAL</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span class='badge-review'>⚪ {decision}</span>", unsafe_allow_html=True)
    elif status == DecisionStatus.LOW_CONFIDENCE:
        st.markdown("<span class='badge-review'>⚠️ NEEDS HUMAN REVIEW (LOW CONFIDENCE)</span>", unsafe_allow_html=True)
    elif status == DecisionStatus.UNAVAILABLE:
        st.markdown("<span class='badge-critical'>🔌 DECIDER SERVICE UNAVAILABLE</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='badge-critical'>❌ DECISION ERROR</span>", unsafe_allow_html=True)


def render_trace_timeline(trace_events: List[TraceEvent]) -> None:
    """Render chronological decision trace."""
    st.markdown("#### 🔍 Audit Decision Trace")
    for event in trace_events:
        st.markdown(
            f"<div class='trace-item'>"
            f"<b>[{event.stage.upper()}]</b> &nbsp;<span style='color:#64748b; font-size:0.75rem;'>{event.timestamp}</span><br>"
            f"{event.message}"
            f"</div>",
            unsafe_allow_html=True,
        )


def render_footer_disclaimer() -> None:
    """Render mandatory hackathon prototype disclaimer."""
    st.markdown(
        """
        <div class='disclaimer-banner'>
        <b>Mandatory Safety & Prototype Disclaimer:</b> CrowdShield AI is an experimental decision-support 
        demonstration built for the AWS Builder Center Agent Experience Hackathon. It operates exclusively on 
        synthetic/simulated scenarios. It does NOT connect to real CCTV cameras, biometric systems, 
        or emergency dispatch infrastructure, and is NOT a certified life-safety assessment tool.
        </div>
        """,
        unsafe_allow_html=True,
    )
