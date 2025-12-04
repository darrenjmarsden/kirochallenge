"""API routes for registration system"""
from fastapi import APIRouter, HTTPException, status
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

router = APIRouter(prefix="/registration", tags=["registration"])


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


# Event endpoints
@router.post("/events", response_model=RegistrationEvent, status_code=status.HTTP_201_CREATED)
async def create_event(event: RegistrationEventCreate):
    """
    Create a new event with registration capabilities
    
    - **eventId**: Optional custom event ID (auto-generated if not provided)
    - **name**: Event name
    - **capacity**: Maximum number of attendees
    - **hasWaitlist**: Whether event has waitlist enabled
    """
    try:
        logger.info(f"Creating registration event: {event.name}")
        created_event = event_service.create_event(
            event.eventId,
            event.name,
            event.capacity,
            event.hasWaitlist
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


# Registration endpoints
@router.post("/registrations", response_model=RegistrationResult, status_code=status.HTTP_201_CREATED)
async def register_user(registration: RegistrationCreate):
    """
    Register a user for an event
    
    - **userId**: User identifier
    - **eventId**: Event identifier
    
    Returns either an active registration or a waitlist entry if the event is full
    """
    try:
        logger.info(f"Registering user {registration.userId} for event {registration.eventId}")
        result = registration_service.register_user(registration.userId, registration.eventId)
        return result
    except Exception as e:
        handle_exception(e)


@router.delete("/registrations", response_model=UnregistrationResult)
async def unregister_user(userId: str, eventId: str):
    """
    Unregister a user from an event
    
    - **userId**: User identifier
    - **eventId**: Event identifier
    """
    try:
        logger.info(f"Unregistering user {userId} from event {eventId}")
        result = registration_service.unregister_user(userId, eventId)
        return result
    except Exception as e:
        handle_exception(e)


@router.get("/users/{user_id}/events", response_model=List[RegistrationEvent])
async def get_user_events(user_id: str):
    """
    Get all events a user is registered for (active registrations only)
    
    - **user_id**: User identifier
    """
    try:
        logger.info(f"Getting events for user: {user_id}")
        events = registration_service.get_user_registrations(user_id)
        return events
    except Exception as e:
        handle_exception(e)
