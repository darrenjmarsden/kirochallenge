from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


class EventNotFoundException(Exception):
    """Raised when an event is not found"""
    def __init__(self, event_id: str):
        self.event_id = event_id
        super().__init__(f"Event with ID {event_id} not found")


class DatabaseException(Exception):
    """Raised when a database operation fails"""
    def __init__(self, operation: str, detail: str):
        self.operation = operation
        self.detail = detail
        super().__init__(f"Database {operation} failed: {detail}")


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages"""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(f"Validation error on {request.url.path}: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors
        }
    )


async def event_not_found_handler(request: Request, exc: EventNotFoundException):
    """Handle event not found errors"""
    logger.info(f"Event not found: {exc.event_id}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "detail": str(exc),
            "event_id": exc.event_id
        }
    )


async def database_exception_handler(request: Request, exc: DatabaseException):
    """Handle database errors"""
    logger.error(f"Database error during {exc.operation}: {exc.detail}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Database operation failed",
            "operation": exc.operation
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors"""
    logger.error(f"Unexpected error on {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred",
            "path": str(request.url.path)
        }
    )
