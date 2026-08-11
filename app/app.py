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
    page_title="Insurance Claim Risk Predictor",
    page_icon="🚗",
    layout="centered",
)

# ---------- header ----------
st.title("🚗 Car Insurance Claim Risk Predictor")
st.caption(
    "A class-weighted ANN estimates the probability that a policyholder will file a claim, "
    "tuned to prioritize catching real claims over minimizing false alarms."
)

# ---------- check model artifacts exist ----------
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


with st.spinner("Loading model..."):
    get_pipeline()

st.divider()

# ---------- input form ----------
st.subheader("Applicant Details")

col1, col2 = st.columns(2)

with col1:
    age = st.selectbox("Age group", ["16-25", "26-39", "40-64", "65+"], index=1)
    gender = st.selectbox("Gender", ["male", "female"])
    race = st.selectbox("Race", ["majority", "minority"])
    driving_experience = st.selectbox("Driving experience", ["0-9y", "10-19y", "20-29y", "30y+"], index=1)
    education = st.selectbox("Education", ["none", "high school", "university"], index=1)
    income = st.selectbox(
        "Income bracket", ["poverty", "working class", "middle class", "upper class"], index=1
    )
    vehicle_year = st.selectbox("Vehicle year", ["before 2015", "after 2015"])
    vehicle_type = st.selectbox("Vehicle type", ["sedan", "sports car"])

with col2:
    credit_score = st.slider("Credit score (normalized)", 0.0, 1.0, 0.5, 0.01)
    annual_mileage = st.number_input("Annual mileage", min_value=0, max_value=50000, value=12000, step=500)
    vehicle_ownership = st.selectbox("Owns vehicle outright?", ["Yes", "No"]) == "Yes"
    married = st.selectbox("Married?", ["No", "Yes"]) == "Yes"
    children = st.selectbox("Has children?", ["No", "Yes"]) == "Yes"
    speeding_violations = st.number_input("Speeding violations", min_value=0, max_value=20, value=0, step=1)
    duis = st.number_input("DUIs", min_value=0, max_value=10, value=0, step=1)
    past_accidents = st.number_input("Past accidents", min_value=0, max_value=15, value=0, step=1)

st.divider()

threshold_choice = st.radio(
    "Decision threshold",
    ["0.50 — maximize claim recall (deployed default)", "0.595 — F1-optimal balance"],
    index=0,
)
threshold = 0.5 if threshold_choice.startswith("0.50") else 0.595

# ---------- predict ----------
if st.button("Predict Claim Risk", type="primary", use_container_width=True):
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

    with st.spinner("Scoring applicant..."):
        result = predict_claim_risk(raw_input, threshold=threshold)

    st.subheader("Result")

    prob_pct = result["claim_probability"] * 100
    is_risky = result["prediction"] == 1

    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("Claim Probability", f"{prob_pct:.1f}%")
    with c2:
        if is_risky:
            st.error(f"**{result['label']}** — flagged above the {threshold:.3f} threshold")
        else:
            st.success(f"**{result['label']}** — below the {threshold:.3f} threshold")

    st.progress(min(result["claim_probability"], 1.0))

    with st.expander("Why this model behaves this way"):
        st.write(
            "This model (Model 5 in the project notebook) is trained with class weights favoring "
            "the minority claim class, trading some overall accuracy for a higher recall on real "
            "claims — missing a claim is treated as costlier than a false alarm. See the project "
            "README for the full model comparison and rationale."
        )

st.divider()
st.caption("Deep Learning Unit — Final Project · Turki · Mohammed · Abdulaziz · Nawaf · Saleh")
