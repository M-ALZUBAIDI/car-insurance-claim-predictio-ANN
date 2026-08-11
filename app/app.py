"""
Streamlit demo for the Car Insurance Claim Risk model.

Run from the repo root:
    streamlit run app/app.py

Requires the trained model artifacts in ../models/:
    insurance_risk_model.h5, scaler.pkl, ordinal_encoder.pkl, feature_columns.pkl
"""

import os
import sys

import streamlit as st

# Make src/ importable when running `streamlit run app/app.py` from the repo root
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))
from inference import load_pipeline, predict_claim_risk, MODELS_DIR  # noqa: E402

st.set_page_config(
    page_title="Claim Risk Assessment",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# DESIGN SYSTEM — underwriter's desk / case-file aesthetic
# ============================================================
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,500;8..60,600;8..60,700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600;700&display=swap');

:root {
    --paper: #EEF1E7;
    --paper-raised: #F7F9F1;
    --ink: #14201C;
    --ink-soft: #3E4A42;
    --ink-faint: #8A9186;
    --rule: #C9D0BE;
    --brass: #B8863B;
    --brass-deep: #96692A;
    --risk-low: #2F6B4F;
    --risk-med: #B8863B;
    --risk-high: #A23B2E;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--paper) !important;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }
#MainMenu, footer { visibility: hidden; }

.block-container { padding-top: 2.2rem !important; max-width: 1180px; }

* { font-family: 'Inter', sans-serif; }

/* ---------- masthead ---------- */
.eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    letter-spacing: 0.18em;
    color: var(--brass-deep);
    font-weight: 600;
    margin-bottom: 6px;
}
.headline {
    font-family: 'Source Serif 4', serif;
    font-size: 42px;
    font-weight: 700;
    color: var(--ink);
    line-height: 1.1;
    margin-bottom: 8px;
}
.subcaption {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12.5px;
    color: var(--ink-soft);
    letter-spacing: 0.02em;
}
.masthead-rule {
    border: none;
    border-top: 2px solid var(--ink);
    margin: 18px 0 26px 0;
}

/* ---------- section labels ---------- */
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11.5px;
    letter-spacing: 0.14em;
    color: var(--brass-deep);
    font-weight: 700;
    border-bottom: 1px solid var(--rule);
    padding-bottom: 6px;
    margin: 22px 0 14px 0;
}
.section-label:first-of-type { margin-top: 4px; }

/* ---------- panel card ---------- */
.panel {
    background: var(--paper-raised);
    border: 1px solid var(--rule);
    border-radius: 4px;
    padding: 26px 28px 22px 28px;
}
.panel-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    letter-spacing: 0.16em;
    color: var(--ink-faint);
    font-weight: 700;
    margin-bottom: 4px;
}

/* ---------- form field labels ---------- */
[data-testid="stWidgetLabel"] p {
    font-family: 'Inter', sans-serif !important;
    font-size: 12.5px !important;
    font-weight: 600 !important;
    color: var(--ink-soft) !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.stSelectbox div[data-baseweb="select"] > div,
.stNumberInput input {
    background: #FFFFFF !important;
    border: 1px solid var(--rule) !important;
    border-radius: 3px !important;
    color: var(--ink) !important;
    font-family: 'IBM Plex Mono', monospace !important;
}
.stSlider [data-baseweb="slider"] { padding-top: 6px; }

/* ---------- radio as segmented control ---------- */
div[role="radiogroup"] { gap: 6px; }
div[role="radiogroup"] label {
    background: #FFFFFF;
    border: 1px solid var(--rule);
    border-radius: 3px;
    padding: 8px 12px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 12px !important;
}

/* ---------- submit button ---------- */
.stButton > button {
    background: var(--ink) !important;
    color: var(--paper) !important;
    border: none !important;
    border-radius: 3px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase;
    font-size: 12.5px !important;
    padding: 12px !important;
}
.stButton > button:hover { background: var(--brass-deep) !important; color: #FFFFFF !important; }

/* ---------- empty state ---------- */
.pending-box {
    border: 1.5px dashed var(--rule);
    border-radius: 4px;
    padding: 60px 20px;
    text-align: center;
    color: var(--ink-faint);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12.5px;
    letter-spacing: 0.04em;
}

/* ---------- stamp ---------- */
.stamp-wrap { display: flex; justify-content: center; margin: 8px 0 22px 0; }
.stamp {
    width: 168px; height: 168px;
    border-radius: 50%;
    border: 3.5px solid var(--stamp-color);
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    transform: rotate(-7deg);
    color: var(--stamp-color);
    font-family: 'IBM Plex Mono', monospace;
    box-shadow: inset 0 0 0 3px var(--paper-raised), inset 0 0 0 4px var(--stamp-color);
}
@media (prefers-reduced-motion: no-preference) {
    .stamp { animation: stampIn 0.35s ease-out; }
}
@keyframes stampIn {
    from { transform: rotate(-7deg) scale(1.6); opacity: 0; }
    to { transform: rotate(-7deg) scale(1); opacity: 1; }
}
.stamp-verdict { font-size: 15px; font-weight: 700; letter-spacing: 0.06em; text-align: center; line-height: 1.25; }
.stamp-pct { font-size: 26px; font-weight: 700; margin-top: 4px; }

/* ---------- ledger meter ---------- */
.meter-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px; letter-spacing: 0.1em; color: var(--ink-faint);
    display: flex; justify-content: space-between; margin-bottom: 5px;
}
.meter-track {
    width: 100%; height: 10px; background: #E2E6D9;
    border: 1px solid var(--rule); border-radius: 2px; position: relative; overflow: hidden;
}
.meter-fill { height: 100%; border-radius: 1px; }
.meter-ticks { position: relative; height: 14px; }
.meter-tick {
    position: absolute; top: 0; font-family: 'IBM Plex Mono', monospace;
    font-size: 9.5px; color: var(--ink-faint); transform: translateX(-50%);
}

/* ---------- ledger rows ---------- */
.ledger-row {
    display: flex; justify-content: space-between; align-items: baseline;
    padding: 9px 0; border-bottom: 1px solid var(--rule);
    font-family: 'IBM Plex Mono', monospace; font-size: 12.5px;
}
.ledger-row:last-child { border-bottom: none; }
.ledger-key { color: var(--ink-soft); }
.ledger-val { color: var(--ink); font-weight: 600; }

/* ---------- footer ---------- */
.footer-mono {
    margin-top: 40px; padding-top: 16px; border-top: 1px solid var(--rule);
    font-family: 'IBM Plex Mono', monospace; font-size: 11px;
    letter-spacing: 0.06em; color: var(--ink-faint); text-align: center;
}

/* alerts restyle */
.stAlert { border-radius: 3px !important; font-family: 'Inter', sans-serif !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ============================================================
# MASTHEAD
# ============================================================
st.markdown('<div class="eyebrow">UNDERWRITING DESK · CASE ASSESSMENT</div>', unsafe_allow_html=True)
st.markdown('<div class="headline">Claim Risk Assessment</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subcaption">MODEL 5 · CLASS-WEIGHTED ANN · TUNED FOR CLAIM RECALL</div>',
    unsafe_allow_html=True,
)
st.markdown('<hr class="masthead-rule">', unsafe_allow_html=True)

# ============================================================
# check model artifacts exist
# ============================================================
required_files = ["insurance_risk_model.h5", "scaler.pkl", "ordinal_encoder.pkl", "feature_columns.pkl"]
missing = [f for f in required_files if not os.path.exists(os.path.join(MODELS_DIR, f))]

if missing:
    st.error(
        "Model artifacts not found in `models/`: "
        + ", ".join(missing)
        + ".\n\nRun the notebook end-to-end first, then copy the generated files into `models/`."
    )
    st.stop()


@st.cache_resource
def get_pipeline():
    return load_pipeline()


with st.spinner("Opening the case file..."):
    get_pipeline()

# ============================================================
# LAYOUT — application (left) / assessment (right)
# ============================================================
col_form, col_result = st.columns([6, 5], gap="large")

with col_form:
    st.markdown('<div class="panel-title">APPLICATION</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-label">APPLICANT</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        age = st.selectbox("Age group", ["16-25", "26-39", "40-64", "65+"], index=1)
        race = st.selectbox("Race", ["majority", "minority"])
        education = st.selectbox("Education", ["none", "high school", "university"], index=1)
        married = st.selectbox("Married?", ["No", "Yes"]) == "Yes"
    with c2:
        gender = st.selectbox("Gender", ["male", "female"])
        income = st.selectbox(
            "Income bracket", ["poverty", "working class", "middle class", "upper class"], index=1
        )
        children = st.selectbox("Has children?", ["No", "Yes"]) == "Yes"
        credit_score = st.slider("Credit score (normalized)", 0.0, 1.0, 0.5, 0.01)

    st.markdown('<div class="section-label">VEHICLE</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        vehicle_year = st.selectbox("Vehicle year", ["before 2015", "after 2015"])
        vehicle_type = st.selectbox("Vehicle type", ["sedan", "sports car"])
    with c4:
        vehicle_ownership = st.selectbox("Owns vehicle outright?", ["Yes", "No"]) == "Yes"
        annual_mileage = st.number_input("Annual mileage", min_value=0, max_value=50000, value=12000, step=500)

    st.markdown('<div class="section-label">DRIVING RECORD</div>', unsafe_allow_html=True)
    c5, c6, c7 = st.columns(3)
    with c5:
        driving_experience = st.selectbox(
            "Experience", ["0-9y", "10-19y", "20-29y", "30y+"], index=1
        )
    with c6:
        speeding_violations = st.number_input("Speeding violations", min_value=0, max_value=20, value=0, step=1)
    with c7:
        duis = st.number_input("DUIs", min_value=0, max_value=10, value=0, step=1)
    past_accidents = st.number_input("Past accidents", min_value=0, max_value=15, value=0, step=1)

    st.markdown('<div class="section-label">DECISION THRESHOLD</div>', unsafe_allow_html=True)
    threshold_choice = st.radio(
        "Decision threshold",
        ["0.50 — maximize claim recall", "0.595 — F1-optimal balance"],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
    )
    threshold = 0.5 if threshold_choice.startswith("0.50") else 0.595

    st.write("")
    submitted = st.button("Submit application", use_container_width=True)

with col_result:
    st.markdown('<div class="panel-title">ASSESSMENT</div>', unsafe_allow_html=True)

    if not submitted:
        st.markdown(
            '<div class="pending-box">CASE PENDING<br><br>'
            'Complete the application and submit<br>to generate a risk assessment.</div>',
            unsafe_allow_html=True,
        )
    else:
        raw_input = {
            "AGE": age,
            "GENDER": gender,
            "RACE": race,
            "DRIVING_EXPERIENCE": driving_experience,
            "EDUCATION": education,
            "INCOME": income,
            "CREDIT_SCORE": credit_score,
            "VEHICLE_OWNERSHIP": 1.0 if vehicle_ownership else 0.0,
            "VEHICLE_YEAR": vehicle_year,
            "MARRIED": 1.0 if married else 0.0,
            "CHILDREN": 1.0 if children else 0.0,
            "ANNUAL_MILEAGE": float(annual_mileage),
            "VEHICLE_TYPE": vehicle_type,
            "SPEEDING_VIOLATIONS": speeding_violations,
            "DUIS": duis,
            "PAST_ACCIDENTS": past_accidents,
        }

        with st.spinner("Reviewing the file..."):
            result = predict_claim_risk(raw_input, threshold=threshold)

        prob = result["claim_probability"]
        prob_pct = prob * 100
        is_risky = result["prediction"] == 1

        # descriptive risk band (independent of the decision threshold)
        if prob < 0.35:
            band, band_color = "LOW", "var(--risk-low)"
        elif prob < 0.6:
            band, band_color = "MEDIUM", "var(--risk-med)"
        else:
            band, band_color = "HIGH", "var(--risk-high)"

        verdict = "LIKELY TO CLAIM" if is_risky else "UNLIKELY TO CLAIM"
        stamp_color = "var(--risk-high)" if is_risky else "var(--risk-low)"

        st.markdown(
            f'<div class="stamp-wrap"><div class="stamp" style="--stamp-color:{stamp_color}">'
            f'<div class="stamp-verdict">{verdict}</div>'
            f'<div class="stamp-pct">{prob_pct:.1f}%</div>'
            f"</div></div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="meter-label"><span>0%</span><span>RISK BAND: {band}</span><span>100%</span></div>'
            f'<div class="meter-track"><div class="meter-fill" '
            f'style="width:{prob_pct:.1f}%; background:{band_color};"></div></div>',
            unsafe_allow_html=True,
        )
        st.write("")

        st.markdown(
            f"""
            <div class="ledger-row"><span class="ledger-key">Claim probability</span><span class="ledger-val">{prob_pct:.1f}%</span></div>
            <div class="ledger-row"><span class="ledger-key">Decision threshold</span><span class="ledger-val">{threshold:.3f}</span></div>
            <div class="ledger-row"><span class="ledger-key">Risk band</span><span class="ledger-val">{band}</span></div>
            <div class="ledger-row"><span class="ledger-key">Model</span><span class="ledger-val">Model 5</span></div>
            """,
            unsafe_allow_html=True,
        )

        with st.expander("Why this model behaves this way"):
            st.write(
                "This model is trained with class weights favoring the minority claim class, "
                "trading some overall accuracy for a higher recall on real claims — missing a "
                "claim is treated as costlier than a false alarm. See the project README for the "
                "full model comparison and rationale."
            )

st.markdown(
    '<div class="footer-mono">DEEP LEARNING UNIT · FINAL PROJECT &nbsp;·&nbsp; '
    "TURKI · MOHAMMED · ABDULAZIZ · NAWAF · SALEH</div>",
    unsafe_allow_html=True,
)
