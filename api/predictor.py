from typing import Any, Tuple

import pandas as pd

from .schemas import LoanApplication


def build_input_data(loan_application: LoanApplication) -> pd.DataFrame:
    """Create the one-row raw feature DataFrame expected by the pipeline."""
    return pd.DataFrame([loan_application.model_dump()])


def predict(
    loan_application: LoanApplication, pipeline: Any
) -> Tuple[str, float, float]:
    input_data = build_input_data(loan_application)
    prediction = str(pipeline.predict(input_data)[0])
    probabilities = pipeline.predict_proba(input_data)[0]
    probabilities_by_class = dict(zip(pipeline.classes_, probabilities))

    return (
        prediction,
        float(probabilities_by_class["Approved"]),
        float(probabilities_by_class["Rejected"]),
    )
