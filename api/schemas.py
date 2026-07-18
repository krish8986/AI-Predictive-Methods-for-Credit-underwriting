from pydantic import BaseModel, ConfigDict


class LoanApplication(BaseModel):
    model_config = ConfigDict(extra="forbid")

    applicant_age: int
    gender: str
    marital_status: str
    employee_status: str
    residence_type: str
    loan_purpose: str
    income_annum: int
    loan_amount: int
    loan_term: int
    cibil_score: int
    residential_assets_value: int
    commercial_assets_value: int
    luxury_assets_value: int
    bank_asset_value: int
    loan_interest: float
    loan_percent_income: int
    active_loans: int


class FeatureImpact(BaseModel):
    feature: str
    impact: float
    direction: str


class PredictionResponse(BaseModel):
    prediction: str
    approval_probability: float
    rejection_probability: float

    top_positive: list[FeatureImpact]
    top_negative: list[FeatureImpact]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool