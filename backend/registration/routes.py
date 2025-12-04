"""API routes for registration system"""
from fastapi import APIRouter, HTTPException, status, Body
from typing import List
import logging

from .models import (
    UserCreate,
    User,
    RegistrationEventCreate,
    RegistrationEvent,
    RegistrationCreate,
    RegistrationResult,
    UnregistrationResult
)
from .services import user_service, event_service, registration_service
from .exceptions import (
    ValidationError,
    DuplicateError,
    NotFoundError,
    CapacityError,
    RegistrationError
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["registration"])


# Exception handler helper
def handle_exception(e: Exception):
    """Convert service exceptions to HTTP exceptions"""
    if isinstance(e, ValidationError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    elif isinstance(e, DuplicateError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    elif isinstance(e, NotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    elif isinstance(e, CapacityError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    elif isinstance(e, RegistrationError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    else:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred")


# User endpoints
@router.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """
    Create a new user
    
    - **userId**: Unique user identifier
    - **name**: User name
    """
    try:
        logger.info(f"Creating user: {user.userId}")
        created_user = user_service.create_user(user.userId, user.name)
        return created_user
    except Exception as e:
        handle_exception(e)


@router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    """
    Get a user by ID
    
    - **user_id**: User identifier
    """
    try:
        logger.info(f"Getting user: {user_id}")
        user = user_service.get_user(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        return user
    except Exception as e:
        handle_exception(e)


@router.get("/users/{user_id}/registrations", response_model=List[RegistrationEvent])
async def get_user_registrations(user_id: str):
    """
    Get all events a user is registered for (active registrations only)
    
    - **user_id**: User identifier
    """
    try:
        logger.info(f"Getting registrations for user: {user_id}")
        events = registration_service.get_user_registrations(user_id)
        return events
    except Exception as e:
        handle_exception(e)


# Event endpoints
@router.post("/events", response_model=RegistrationEvent, status_code=status.HTTP_201_CREATED)
async def create_event(event: RegistrationEventCreate):
    """
    Create a new event with registration capabilities
    
    - **eventId**: Optional custom event ID (auto-generated if not provided)
    - **name** or **title**: Event name
    - **capacity**: Maximum number of attendees
    - **hasWaitlist** or **waitlistEnabled**: Whether event has waitlist enabled
    """
    try:
        event_name = event.get_name()
        if not event_name:
            raise ValidationError("Event name or title is required")
        
        logger.info(f"Creating registration event: {event_name}")
        created_event = event_service.create_event(
            event.eventId,
            event_name,
            event.capacity,
            event.get_waitlist_enabled()
        )
        return created_event
    except Exception as e:
        handle_exception(e)


@router.get("/events/{event_id}", response_model=RegistrationEvent)
async def get_event(event_id: str):
    """
    Get an event by ID
    
    - **event_id**: Event identifier
    """
    try:
        logger.info(f"Getting event: {event_id}")
        event = event_service.get_event(event_id)
        if not event:
            raise NotFoundError(f"Event {event_id} not found")
        return event
    except Exception as e:
        handle_exception(e)


@router.get("/events/{event_id}/capacity")
async def get_event_capacity(event_id: str):
    """
    Get available capacity for an event
    
    - **event_id**: Event identifier
    """
    try:
        logger.info(f"Getting capacity for event: {event_id}")
        available = event_service.get_available_capacity(event_id)
        event = event_service.get_event(event_id)
        return {
            "eventId": event_id,
            "totalCapacity": event["capacity"],
            "availableCapacity": available
        }
    except Exception as e:
        handle_exception(e)


@router.get("/events/{event_id}/registrations")
async def get_event_registrations(event_id: str):
    """
    Get all registrations for an event
    
    - **event_id**: Event identifier
    """
    try:
        logger.info(f"Getting registrations for event: {event_id}")
        # Verify event exists
        event = event_service.get_event(event_id)
        if not event:
            raise NotFoundError(f"Event {event_id} not found")
        
        # Get all registrations for this event
        from .repositories import registration_repository, waitlist_repository
        registrations = registration_repository.find_by_event(event_id)
        waitlist = waitlist_repository.find_by_event(event_id)
        
        return {
            "eventId": event_id,
            "registrations": registrations,
            "waitlist": waitlist
        }
    except Exception as e:
        handle_exception(e)


# Registration endpoints
@router.post("/events/{event_id}/registrations", response_model=RegistrationResult, status_code=status.HTTP_201_CREATED)
async def register_user_for_event(event_id: str, body: dict = Body(...)):
    """
    Register a user for an event
    
    - **event_id**: Event identifier (in path)
    - **userId**: User identifier (in body)
    
    Returns either an active registration or a waitlist entry if the event is full
    """
    try:
        user_id = body.get("userId")
        if not user_id:
            raise ValidationError("userId is required in request body")
        
        logger.info(f"Registering user {user_id} for event {event_id}")
        result = registration_service.register_user(user_id, event_id)
        return result
    except Exception as e:
        handle_exception(e)


@router.delete("/events/{event_id}/registrations/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unregister_user_from_event(event_id: str, user_id: str):
    """
    Unregister a user from an event
    
    - **event_id**: Event identifier
    - **user_id**: User identifier
    """
    try:
        logger.info(f"Unregistering user {user_id} from event {event_id}")
        result = registration_service.unregister_user(user_id, event_id)
        return None  # 204 No Content
    except Exception as e:
        handle_exception(e)
