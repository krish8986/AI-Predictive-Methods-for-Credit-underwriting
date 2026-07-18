from typing import Any

import pandas as pd

from .schemas import LoanApplication


def build_input_data(loan_application: LoanApplication) -> pd.DataFrame:
    """Create the one-row raw feature DataFrame expected by the pipeline."""
    return pd.DataFrame([loan_application.model_dump()])


def predict(
    loan_application: LoanApplication,
    pipeline: Any,
    explainer: Any,
):
    """
    Generate prediction along with SHAP explainability.
    """

    input_data = build_input_data(loan_application)

    # Prediction
    prediction = str(pipeline.predict(input_data)[0])

    probabilities = pipeline.predict_proba(input_data)[0]

    probabilities_by_class = dict(zip(pipeline.classes_, probabilities))

    # SHAP Explanation
    explanation = explainer.explain(input_data)

    top_positive = [
        {
            "feature": item["feature"],
            "impact": abs(item["impact"]),
            "direction": "positive",
        }
        for item in explanation["top_positive"]
    ]

    top_negative = [
        {
            "feature": item["feature"],
            "impact": abs(item["impact"]),
            "direction": "negative",
        }
        for item in explanation["top_negative"]
    ]

    return {
        "prediction": prediction,
        "approval_probability": float(
            probabilities_by_class["Approved"]
        ),
        "rejection_probability": float(
            probabilities_by_class["Rejected"]
        ),
        "top_positive": top_positive,
        "top_negative": top_negative,
    }