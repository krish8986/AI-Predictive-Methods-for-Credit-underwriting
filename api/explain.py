from typing import Any

import pandas as pd
import shap


class SHAPExplainer:
    def __init__(
        self,
        pipeline: Any,
        feature_names: list[str],
        background_data,
    ):
        self.pipeline = pipeline
        self.preprocessor = pipeline.named_steps["preprocessing"]
        self.classifier = pipeline.named_steps["classifier"]
        self.feature_names = feature_names

        self.explainer = shap.TreeExplainer(
            self.classifier,
            background_data,
        )

    def explain(self, input_df: pd.DataFrame) -> dict:

        transformed = self.preprocessor.transform(input_df)

        explanation = self.explainer(transformed)

        values = explanation.values[0]

        feature_importance = []

        for feature, value in zip(self.feature_names, values):

            readable_feature = (
              feature.replace("numeric__", "")
                     .replace("categorical__", "")
                     .replace("_", " ")
                     .title()
            )
            feature_importance.append(
                {
                     "feature": readable_feature,
                     "impact": float(value),
                }
            )
        feature_importance.sort(
            key=lambda x: abs(x["impact"]),
            reverse=True,
        )

        top_positive = []

        top_negative = []

        for item in feature_importance:

            if item["impact"] > 0:

                top_positive.append(
                    {
                        "feature": item["feature"],
                        "impact": item["impact"],
                    }
                )

            elif item["impact"] < 0:

                top_negative.append(
                    {
                        "feature": item["feature"],
                        "impact": item["impact"],
                    }
                )

        return {

            "top_positive": top_positive[:5],

            "top_negative": top_negative[:5],

            "all_features": feature_importance,

            "shap_values": explanation.values,

            "base_value": float(explanation.base_values[0]),
        }