from fastapi import FastAPI, HTTPException, Request, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging

from models import Event, EventCreate, EventUpdate
from database import db_client
from config import settings
from exceptions import (
    EventNotFoundException,
    DatabaseException,
    validation_exception_handler,
    event_not_found_handler,
    database_exception_handler,
    general_exception_handler
)
from registration.routes import router as registration_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware with configurable origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
    expose_headers=["X-Total-Count"],
    max_age=3600,
)

# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(EventNotFoundException, event_not_found_handler)
app.add_exception_handler(DatabaseException, database_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include registration router
app.include_router(registration_router)


@app.get("/")
def read_root():
    return {"message": "Events API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/events", response_model=Event, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventCreate):
    """
    Create a new event
    
    - **title**: Event title (1-200 characters)
    - **description**: Event description (1-2000 characters)
    - **date**: Event date in ISO format (YYYY-MM-DDTHH:MM:SS)
    - **location**: Event location (1-500 characters)
    - **capacity**: Maximum attendees (1-100000)
    - **organizer**: Organizer name (1-200 characters)
    - **status**: Event status (draft, published, cancelled, completed)
    """
    logger.info(f"Creating new event: {event.title}")
    event_data = event.model_dump()
    created_event = db_client.create_event(event_data)
    return created_event


@app.get("/events", response_model=List[Event])
async def list_events(
    limit: Optional[int] = Query(None, ge=1, le=100, description="Maximum number of events to return"),
    status: Optional[str] = Query(None, description="Filter events by status (draft, published, active, cancelled, completed)")
):
    """
    List all events
    
    - **limit**: Optional limit on number of events returned (1-100)
    - **status**: Optional filter by event status
    """
    logger.info(f"Listing events with limit: {limit}, status: {status}")
    events = db_client.list_events(limit=limit, status_filter=status)
    return events


@app.get("/events/{event_id}", response_model=Event)
async def get_event(event_id: str):
    """
    Get a specific event by ID
    
    - **event_id**: UUID of the event
    """
    logger.info(f"Retrieving event: {event_id}")
    event = db_client.get_event(event_id)
    if not event:
        raise EventNotFoundException(event_id)
    return event


@app.put("/events/{event_id}", response_model=Event)
async def update_event(event_id: str, event_update: EventUpdate):
    """
    Update an existing event
    
    - **event_id**: UUID of the event
    - All fields are optional; only provided fields will be updated
    """
    logger.info(f"Updating event: {event_id}")
    
    # Check if event exists
    existing_event = db_client.get_event(event_id)
    if not existing_event:
        raise EventNotFoundException(event_id)
    
    update_data = event_update.model_dump(exclude_unset=True)
    if not update_data:
        logger.warning(f"No fields to update for event: {event_id}")
        return existing_event
    
    updated_event = db_client.update_event(event_id, update_data)
    return updated_event


@app.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: str):
    """
    Delete an event
    
    - **event_id**: UUID of the event
    """
    logger.info(f"Deleting event: {event_id}")
    
    # Check if event exists
    existing_event = db_client.get_event(event_id)
    if not existing_event:
        raise EventNotFoundException(event_id)
    
    db_client.delete_event(event_id)
    return None
