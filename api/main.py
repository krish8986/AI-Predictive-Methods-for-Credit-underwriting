from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request

from .explain import SHAPExplainer
from .model_loader import load_artifacts
from .predictor import predict
from .schemas import HealthResponse, LoanApplication, PredictionResponse


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:

    artifacts = load_artifacts()

    app.state.pipeline = artifacts["pipeline"]

    app.state.explainer = SHAPExplainer(
        artifacts["pipeline"],
        artifacts["feature_names"],
        artifacts["background_data"],
    )

    yield


app = FastAPI(
    title="Credit Underwriting API",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
def health(request: Request):

    return HealthResponse(
        status="ok",
        model_loaded=hasattr(request.app.state, "pipeline"),
    )


@app.post("/predict", response_model=PredictionResponse)
def create_prediction(
    loan_application: LoanApplication,
    request: Request,
):

    try:

        result = predict(
            loan_application,
            request.app.state.pipeline,
            request.app.state.explainer,
        )

        return PredictionResponse(**result)

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {error}",
        ) from error