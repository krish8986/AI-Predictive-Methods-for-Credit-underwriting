from pathlib import Path
from typing import Any

import joblib


MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "credit_underwriting_pipeline.pkl"
)


def load_pipeline() -> Any:
    """Load the trained preprocessing and prediction pipeline at API startup."""
    return joblib.load(MODEL_PATH)
