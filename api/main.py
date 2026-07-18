from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request

from .model_loader import load_pipeline
from .predictor import predict
from .schemas import HealthResponse, LoanApplication, PredictionResponse


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.pipeline = load_pipeline()
    yield


app = FastAPI(
    title="Credit Underwriting API",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    return HealthResponse(status="ok", model_loaded=hasattr(request.app.state, "pipeline"))


@app.post("/predict", response_model=PredictionResponse)
def create_prediction(
    loan_application: LoanApplication, request: Request
) -> PredictionResponse:
    try:
        prediction, approval_probability, rejection_probability = predict(
            loan_application, request.app.state.pipeline
        )
        return PredictionResponse(
            prediction=prediction,
            approval_probability=approval_probability,
            rejection_probability=rejection_probability,
        )
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {error}") from error
