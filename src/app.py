"""Prescription Guard – Streamlit Web UI.

Run with:
    PYTHONPATH=. venv/bin/streamlit run src/app.py
"""

import json
import sys
import os
from pathlib import Path

# Ensure project root is on sys.path so `src.*` imports work.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd

from src.guard_logic import check_safety
from src.config import MOCK_PATIENT_PATH, PROCESSED_DATA_PATH

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Prescription Guard",
    page_icon="💊",
    layout="wide",
)

# ── Custom CSS for a polished look ────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        color: #ffffff;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3, [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }

    /* Tag / pill styling */
    .med-tag {
        display: inline-block;
        padding: 4px 12px;
        margin: 3px 4px;
        border-radius: 16px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .med-tag-blue  { background: #1e3a5f; color: #7ec8e3; border: 1px solid #7ec8e3; }
    .med-tag-red   { background: #5f1e1e; color: #e37e7e; border: 1px solid #e37e7e; }

    /* Main header */
    .main-header {
        text-align: center;
        padding: 1rem 0 0.5rem;
    }
    .main-header h1 { font-size: 2.2rem; }
    .main-header p  { color: #888; font-size: 1rem; margin-top: -0.5rem; }

    /* Alert card */
    .alert-card {
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Load data ─────────────────────────────────────────────────────────────────

@st.cache_data
def load_patient():
    with open(MOCK_PATIENT_PATH, "r") as f:
        return json.load(f)


@st.cache_data
def load_drug_names():
    df = pd.read_pickle(PROCESSED_DATA_PATH)
    drugs = sorted(set(df["Drug 1"].str.strip().tolist() + df["Drug 2"].str.strip().tolist()))
    return drugs


patient = load_patient()
drug_names = load_drug_names()

# ── Sidebar – Patient Profile ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🩺 Patient Profile")
    st.markdown(f"**Name:** {patient['name']}")
    st.markdown(f"**ID:** {patient['patient_id']}")

    st.markdown("---")
    st.markdown("### 💊 Current Medications")
    med_pills = "".join(
        f'<span class="med-tag med-tag-blue">{m}</span>' for m in patient["active_medications"]
    )
    st.markdown(med_pills, unsafe_allow_html=True)

    st.markdown("### ⚠️ Known Allergies")
    if patient["allergies"]:
        allergy_pills = "".join(
            f'<span class="med-tag med-tag-red">{a}</span>' for a in patient["allergies"]
        )
        st.markdown(allergy_pills, unsafe_allow_html=True)
    else:
        st.markdown("_None recorded_")

    st.markdown("---")
    st.caption("Prescription Guard v1.0")

# ── Main area ─────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="main-header">'
    "<h1>💊 Prescription Guard</h1>"
    "<p>Real‑time drug interaction &amp; allergy checker</p>"
    "</div>",
    unsafe_allow_html=True,
)

st.markdown("---")

# Searchable drug dropdown
selected_drug = st.selectbox(
    "🔍 Select New Prescription",
    options=["-- Select a drug --"] + drug_names,
    index=0,
    help="Start typing to search through all available drugs.",
)

if selected_drug and selected_drug != "-- Select a drug --":
    st.markdown("---")
    results = check_safety(selected_drug, patient["active_medications"], patient["allergies"])

    # Separate by severity
    has_alerts = False
    for alert in results:
        color = alert.get("color", "gray")
        severity = alert.get("severity", "unknown").upper()
        description = alert.get("description", "")
        drug = alert.get("drug", "")

        if color == "red":
            has_alerts = True
            st.error(f"🚨 **{severity}** — {drug}: {description}")
            with st.expander("📋 Management Advice"):
                st.markdown(
                    f"**Interaction between `{selected_drug}` and `{drug}`**\n\n"
                    f"{description}\n\n"
                    "⚠️ *Consider alternative therapy or consult a pharmacist before prescribing.*"
                )
        elif color == "yellow":
            has_alerts = True
            st.warning(f"⚠️ **{severity}** — {drug}: {description}")
            with st.expander("📋 Management Advice"):
                st.markdown(
                    f"**Interaction between `{selected_drug}` and `{drug}`**\n\n"
                    f"{description}\n\n"
                    "ℹ️ *Monitor the patient closely and adjust dosage if necessary.*"
                )
        elif color == "green":
            st.success(f"✅ **{severity}** — {drug}: {description}")
        else:
            # Gray / Unknown
            st.info(f"ℹ️ **{severity}** — {drug}: {description}")

    if not has_alerts:
        st.success("✅ **No significant interactions found.** Safe to prescribe.")
