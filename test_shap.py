import joblib
import pandas as pd

from api.explain import SHAPExplainer

pipeline = joblib.load("models/credit_underwriting_pipeline.pkl")
feature_names = joblib.load("models/feature_names.pkl")
background = joblib.load("models/background_data.pkl")

explainer = SHAPExplainer(
    pipeline,
    feature_names,
    background,
)

sample = pd.read_csv("credit_underwriting1.csv").drop(
    columns=["loan_id", "loan_status"]
).head(1)

result = explainer.explain(sample)

print(type(result))
print(result)