from pathlib import Path
from typing import Any

import joblib

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

PIPELINE_PATH = MODELS_DIR / "credit_underwriting_pipeline.pkl"
FEATURE_NAMES_PATH = MODELS_DIR / "feature_names.pkl"
BACKGROUND_DATA_PATH = MODELS_DIR / "background_data.pkl"


def load_artifacts() -> dict[str, Any]:
    pipeline = joblib.load(PIPELINE_PATH)
    feature_names = joblib.load(FEATURE_NAMES_PATH)
    background_data = joblib.load(BACKGROUND_DATA_PATH)

    return {
        "pipeline": pipeline,
        "feature_names": feature_names,
        "background_data": background_data,
    }