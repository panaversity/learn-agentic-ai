import os
import httpx
from typing import ClassVar
from dataclasses import dataclass
from fastapi import HTTPException


# Configuration
@dataclass
class Settings:
    DAPR_GRPC_PORT: ClassVar[str] = os.getenv("DAPR_GRPC_PORT", "50001")  # Default gRPC port
    DAPR_HTTP_PORT: ClassVar[str] = os.getenv("DAPR_HTTP_PORT", "3500")
    APP_PORT: ClassVar[str] = os.getenv("APP_PORT", "8010")
    CORS_ORIGINS: ClassVar[list[str]] = ["http://localhost:3000"]
    MODEL_NAME: ClassVar[str] = "gemini-1.5-flash"
    MODEL_BASE_URL: ClassVar[str] = "https://generativelanguage.googleapis.com/v1beta/openai/"

settings = Settings()


# Fetch Gemini API key from Dapr secrets store (using HTTP API)
async def get_gemini_api_key() -> str:
    dapr_url = f"http://localhost:{settings.DAPR_HTTP_PORT}/v1.0/secrets/secretstore/gemini-api-key"
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.get(dapr_url)
            response.raise_for_status()
            secret_data = response.json()
            return secret_data["gemini-api-key"]
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve Gemini API key: {e}")
