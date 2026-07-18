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
    X, y, test_size=0.2, random_state=42
)

# Transform raw categorical inputs while leaving numeric columns unchanged.
categorical_columns = [
    "gender",
    "marital_status",
    "employee_status",
    "residence_type",
    "loan_purpose",
]
numeric_columns = [column for column in X.columns if column not in categorical_columns]

preprocessing = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_columns,
        ),
        ("numeric", "passthrough", numeric_columns),
    ],
    sparse_threshold=0,
)

# Fit preprocessing and the classifier together so inference uses identical transformations.
pipeline = Pipeline(
    steps=[
        ("preprocessing", preprocessing),
        ("classifier", GradientBoostingClassifier(random_state=42)),
    ]
)
pipeline.fit(X_train, y_train)

# Persist the complete production artifact without replacing the legacy model.
model_path = project_root / "models" / "credit_underwriting_pipeline.pkl"
model_path.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(pipeline, model_path)

# Preserve the existing evaluation metrics on the held-out test set.
y_pred = pipeline.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
classification_report_result = classification_report(y_test, y_pred)

print(f"Accuracy: {accuracy:.2f}")
print("Classification Report:")
print(classification_report_result)
