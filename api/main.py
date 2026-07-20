from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from .explain import SHAPExplainer
from .model_loader import load_artifacts
from .predictor import predict
from .schemas import HealthResponse, LoanApplication, PredictionResponse

from rag.embeddings import SentenceTransformerEmbeddingService
from rag.vector_store import FAISSVectorStore
from rag.retriever import Retriever
from rag.groq_generator import GroqResponseGenerator

from dotenv import load_dotenv
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:

    artifacts = load_artifacts()

    app.state.pipeline = artifacts["pipeline"]

    app.state.explainer = SHAPExplainer(
        artifacts["pipeline"],
        artifacts["feature_names"],
        artifacts["background_data"],
    )

    embedding_service = SentenceTransformerEmbeddingService()

    vector_store = FAISSVectorStore.load(
        "models/rag_index/index.faiss"
    )

    retriever = Retriever(
        embedding_service,
        vector_store,
    )

    generator = GroqResponseGenerator()

    app.state.retriever = retriever
    app.state.generator = generator

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

        app.state.last_prediction = result

        return PredictionResponse(**result)

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {error}",
        ) from error


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


@app.post("/ask", response_model=ChatResponse)
def ask(
    request: ChatRequest,
    http_request: Request,
):

    retriever = http_request.app.state.retriever

    generator = http_request.app.state.generator

    context = retriever.retrieve(
        request.question
    )
    enhanced_question = request.question

    if hasattr(app.state, "last_prediction"):
        pred = app.state.last_prediction

        enhanced_question = f"""
    Prediction Result:
    {pred['prediction']}

    Approval Probability:
    {pred['approval_probability']:.2%}

    Top Positive Factors:
    {', '.join(x['feature'] for x in pred['top_positive'])}

    Top Negative Factors:
    {', '.join(x['feature'] for x in pred['top_negative'])}

    User Question:
    {request.question}
    """

    answer = generator.generate(
        enhanced_question,
        context,
    )
    sources = list(
        {
            item.record.metadata.get("source", "Unknown")
            for item in context
        }
    )    
    return ChatResponse(
        answer=answer,
        sources=sources,
    )