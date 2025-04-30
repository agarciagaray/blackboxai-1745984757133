from fastapi import FastAPI
from app.api.v1 import credit_scoring
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from app.core.security import verify_token

app = FastAPI(
    title="Credit Scoring API",
    version="1.0.0",
    description="API REST para evaluación de scoring crediticio en Colombia"
)

# CORS middleware (optional, adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api.v1 import auth

app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(credit_scoring.router, prefix="/api/v1/credit-scoring", tags=["credit-scoring"], dependencies=[Depends(verify_token)])
