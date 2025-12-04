import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # API Configuration
    API_TITLE: str = "Events API"
    API_DESCRIPTION: str = "REST API for managing events with DynamoDB"
    API_VERSION: str = "1.0.0"
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000"
    ).split(",")
    CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # DynamoDB Configuration
    DYNAMODB_TABLE_NAME: str = os.getenv("DYNAMODB_TABLE_NAME", "events-table")
    # AWS_REGION is automatically set by Lambda runtime, fallback to AWS_DEFAULT_REGION for local dev
    AWS_REGION: str = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    AWS_ENDPOINT_URL: str = os.getenv("AWS_ENDPOINT_URL", "")
    
    # Validation limits
    MAX_EVENTS_PER_REQUEST: int = 100


settings = Settings()
