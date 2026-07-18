from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# Load the same source dataset regardless of the shell working directory.
project_root = Path(__file__).resolve().parent
data_path = project_root / "credit_underwriting1.csv"
data = pd.read_csv(data_path)

# Separate the target and exclude the identifier from model features.
X = data.drop(columns=["loan_id", "loan_status"])
y = data["loan_status"]

# Preserve the existing train/test split configuration.
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
)

# Transform raw categorical inputs while leaving numeric columns unchanged.
categorical_columns = [
    "gender",
    "marital_status",
    "employee_status",
    "residence_type",
    "loan_purpose",
]

numeric_columns = [
    column for column in X.columns
    if column not in categorical_columns
]

preprocessing = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_columns,
        ),
        (
            "numeric",
            "passthrough",
            numeric_columns,
        ),
    ],
    sparse_threshold=0,
)

# Build the production ML pipeline.
pipeline = Pipeline(
    steps=[
        (
            "preprocessing",
            preprocessing,
        ),
        (
            "classifier",
            GradientBoostingClassifier(random_state=42),
        ),
    ]
)

# Train the complete pipeline.
pipeline.fit(X_train, y_train)

# --------------------------------------------------------
# SHAP SUPPORT ARTIFACTS
# --------------------------------------------------------

preprocessor = pipeline.named_steps["preprocessing"]

# Feature names after OneHotEncoder expansion.
feature_names = preprocessor.get_feature_names_out().tolist()

# Representative background dataset for SHAP.
background_data = preprocessor.transform(
    X_train.sample(
        n=min(100, len(X_train)),
        random_state=42,
    )
)

# --------------------------------------------------------
# SAVE ARTIFACTS
# --------------------------------------------------------

models_dir = project_root / "models"
models_dir.mkdir(parents=True, exist_ok=True)

pipeline_path = models_dir / "credit_underwriting_pipeline.pkl"
feature_names_path = models_dir / "feature_names.pkl"
background_data_path = models_dir / "background_data.pkl"

joblib.dump(pipeline, pipeline_path)
joblib.dump(feature_names, feature_names_path)
joblib.dump(background_data, background_data_path)

# --------------------------------------------------------
# MODEL EVALUATION
# --------------------------------------------------------

y_pred = pipeline.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

classification_report_result = classification_report(
    y_test,
    y_pred,
)

print(f"Accuracy: {accuracy:.2f}")

print("\nClassification Report:\n")

print(classification_report_result)

print("\nSaved Artifacts:")

print(f"✔ Pipeline        : {pipeline_path}")

print(f"✔ Feature Names   : {feature_names_path}")

print(f"✔ Background Data : {background_data_path}")