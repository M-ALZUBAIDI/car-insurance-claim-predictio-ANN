"""
Standalone inference pipeline for the Car Insurance Claim Risk model.

Loads the trained model (Model 5 — class-weighted ANN) plus its preprocessing
artifacts, and exposes predict_claim_risk() for scoring new applicants.

Run directly for a quick example:
    python src/inference.py
"""

import os
import joblib
import pandas as pd
from tensorflow.keras.models import load_model

MODELS_DIR = os.path.join(os.path.dirname(__file__), "..", "models")

ORDINAL_COLS = ["AGE", "DRIVING_EXPERIENCE", "EDUCATION", "INCOME", "VEHICLE_YEAR"]
ONEHOT_COLS = ["GENDER", "RACE", "VEHICLE_TYPE"]


def load_pipeline(models_dir: str = MODELS_DIR):
    """Load the trained model and preprocessing artifacts."""
    model = load_model(os.path.join(models_dir, "insurance_risk_model.h5"))
    scaler = joblib.load(os.path.join(models_dir, "scaler.pkl"))
    ordinal_encoder = joblib.load(os.path.join(models_dir, "ordinal_encoder.pkl"))
    feature_columns = joblib.load(os.path.join(models_dir, "feature_columns.pkl"))
    return model, scaler, ordinal_encoder, feature_columns


def predict_claim_risk(raw_input: dict, threshold: float = 0.5, models_dir: str = MODELS_DIR) -> dict:
    """
    Score a single applicant.

    Parameters
    ----------
    raw_input : dict
        Raw applicant fields, matching the original CSV columns
        (excluding ID, POSTAL_CODE, OUTCOME).
    threshold : float
        Decision cutoff. Default 0.5 is the threshold used in the shipped
        model (maximizes recall on the claim class, per the project's
        business priority). Use 0.595 for the F1-optimal alternative.

    Returns
    -------
    dict with claim_probability, prediction (0/1), and a human-readable label.
    """
    model, scaler, ordinal_encoder, feature_columns = load_pipeline(models_dir)

    df_input = pd.DataFrame([raw_input])
    df_input[ORDINAL_COLS] = ordinal_encoder.transform(df_input[ORDINAL_COLS])
    df_input = pd.get_dummies(df_input, columns=ONEHOT_COLS, drop_first=True, dtype=int)

    # Align columns with training data (adds any missing dummy columns as 0)
    df_input = df_input.reindex(columns=feature_columns, fill_value=0)

    X_scaled = scaler.transform(df_input)
    prob = float(model.predict(X_scaled, verbose=0)[0][0])
    prediction = int(prob > threshold)

    return {
        "claim_probability": prob,
        "prediction": prediction,
        "label": "Likely to claim" if prediction == 1 else "Unlikely to claim",
    }


if __name__ == "__main__":
    sample_applicant = {
        "AGE": "26-39",
        "GENDER": "male",
        "RACE": "majority",
        "DRIVING_EXPERIENCE": "10-19y",
        "EDUCATION": "high school",
        "INCOME": "working class",
        "CREDIT_SCORE": 0.5,
        "VEHICLE_OWNERSHIP": 1.0,
        "VEHICLE_YEAR": "before 2015",
        "MARRIED": 0.0,
        "CHILDREN": 1.0,
        "ANNUAL_MILEAGE": 12000.0,
        "VEHICLE_TYPE": "sedan",
        "SPEEDING_VIOLATIONS": 1,
        "DUIS": 0,
        "PAST_ACCIDENTS": 0,
    }

    result = predict_claim_risk(sample_applicant)
    print(result)
