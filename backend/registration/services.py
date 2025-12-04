"""Service layer for business logic"""
from typing import Optional, List, Dict, Any, Union
import logging

from .repositories import (
    user_repository,
    event_repository,
    registration_repository,
    waitlist_repository
)
from .exceptions import (
    ValidationError,
    DuplicateError,
    NotFoundError,
    CapacityError,
    RegistrationError
)
from .models import RegistrationStatus

logger = logging.getLogger(__name__)


class UserService:
    """Service for user operations"""
    
    def __init__(self):
        self.repository = user_repository
    
    def create_user(self, user_id: str, name: str) -> Dict[str, Any]:
        """Create a new user"""
        # Validate inputs
        if not user_id or not user_id.strip():
            raise ValidationError("UserId cannot be empty")
        if not name or not name.strip():
            raise ValidationError("Name cannot be empty")
        
        # Check for duplicate
        if self.repository.exists(user_id):
            raise DuplicateError(f"User with ID {user_id} already exists")
        
        # Create user
        user_data = {
            "userId": user_id.strip(),
            "name": name.strip()
        }
        return self.repository.save(user_data)
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by ID"""
        return self.repository.find_by_id(user_id)


class EventService:
    """Service for event operations"""
    
    def __init__(self):
        self.repository = event_repository
        self.registration_repository = registration_repository
    
    def create_event(self, event_id: Optional[str], name: str, capacity: int, has_waitlist: bool) -> Dict[str, Any]:
        """Create a new event"""
        # Validate inputs
        if not name or not name.strip():
            raise ValidationError("Event name cannot be empty")
        if capacity <= 0:
            raise ValidationError("Capacity must be a positive integer")
        
        # Create event
        event_data = {
            "eventId": event_id,
            "name": name.strip(),
            "capacity": capacity,
            "hasWaitlist": has_waitlist
        }
        return self.repository.save(event_data)
    
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get an event by ID"""
        return self.repository.find_by_id(event_id)
    
    def get_available_capacity(self, event_id: str) -> int:
        """Get the available capacity for an event"""
        event = self.repository.find_by_id(event_id)
        if not event:
            raise NotFoundError(f"Event {event_id} not found")
        
        active_count = self.registration_repository.count_active_by_event(event_id)
        return event["capacity"] - active_count


class RegistrationService:
    """Service for registration operations"""
    
    def __init__(self):
        self.user_repository = user_repository
        self.event_repository = event_repository
        self.registration_repository = registration_repository
        self.waitlist_repository = waitlist_repository
    
    def register_user(self, user_id: str, event_id: str) -> Dict[str, Any]:
        """Register a user for an event"""
        # Validate user exists
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        
        # Validate event exists
        event = self.event_repository.find_by_id(event_id)
        if not event:
            raise NotFoundError(f"Event {event_id} not found")
        
        # Check if already registered
        existing_registration = self.registration_repository.find_by_user_and_event(user_id, event_id)
        if existing_registration:
            raise DuplicateError(f"User {user_id} is already registered for event {event_id}")
        
        # Check if already on waitlist
        existing_waitlist = self.waitlist_repository.find_by_user_and_event(user_id, event_id)
        if existing_waitlist:
            raise DuplicateError(f"User {user_id} is already on the waitlist for event {event_id}")
        
        # Check capacity
        active_count = self.registration_repository.count_active_by_event(event_id)
        available = event["capacity"] - active_count
        
        if available > 0:
            # Create active registration
            registration_data = {
                "userId": user_id,
                "eventId": event_id,
                "status": RegistrationStatus.ACTIVE.value
            }
            registration = self.registration_repository.save(registration_data)
            logger.info(f"User {user_id} registered for event {event_id}")
            return {
                "success": True,
                "message": "Successfully registered for event",
                "registration": registration,
                "waitlistEntry": None
            }
        else:
            # Event is full
            if not event.get("hasWaitlist", False):
                raise CapacityError(f"Event {event_id} is full and has no waitlist")
            
            # Add to waitlist
            position = self.waitlist_repository.get_next_position(event_id)
            entry_data = {
                "userId": user_id,
                "eventId": event_id,
                "position": position
            }
            waitlist_entry = self.waitlist_repository.add(entry_data)
            logger.info(f"User {user_id} added to waitlist for event {event_id} at position {position}")
            return {
                "success": True,
                "message": f"Event is full. Added to waitlist at position {position}",
                "registration": None,
                "waitlistEntry": waitlist_entry
            }
    
    def unregister_user(self, user_id: str, event_id: str) -> Dict[str, Any]:
        """Unregister a user from an event"""
        # Check if user is registered
        registration = self.registration_repository.find_by_user_and_event(user_id, event_id)
        if not registration:
            raise NotFoundError(f"User {user_id} is not registered for event {event_id}")
        
        # Remove registration
        self.registration_repository.delete(user_id, event_id)
        logger.info(f"User {user_id} unregistered from event {event_id}")
        
        # Check if there's a waitlist to promote from
        event = self.event_repository.find_by_id(event_id)
        promoted = None
        
        if event and event.get("hasWaitlist", False):
            first_waitlist = self.waitlist_repository.find_first_by_event(event_id)
            if first_waitlist:
                # Promote first waitlisted user
                promoted_user_id = first_waitlist["userId"]
                
                # Remove from waitlist
                self.waitlist_repository.remove(promoted_user_id, event_id)
                
                # Create active registration
                registration_data = {
                    "userId": promoted_user_id,
                    "eventId": event_id,
                    "status": RegistrationStatus.ACTIVE.value
                }
                promoted = self.registration_repository.save(registration_data)
                logger.info(f"Promoted user {promoted_user_id} from waitlist to active registration for event {event_id}")
        
        return {
            "success": True,
            "message": "Successfully unregistered from event",
            "promoted": promoted
        }
    
    def get_user_registrations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all events a user is registered for (active registrations only)"""
        # Validate user exists
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        
        # Get active registrations
        registrations = self.registration_repository.find_active_by_user(user_id)
        
        # Get event details for each registration
        events = []
        for reg in registrations:
            event = self.event_repository.find_by_id(reg["eventId"])
            if event:
                events.append(event)
        
        return events
    
    def is_user_registered(self, user_id: str, event_id: str) -> bool:
        """Check if a user is registered for an event"""
        registration = self.registration_repository.find_by_user_and_event(user_id, event_id)
        return registration is not None and registration.get("status") == RegistrationStatus.ACTIVE.value
    
    def is_user_waitlisted(self, user_id: str, event_id: str) -> bool:
        """Check if a user is on the waitlist for an event"""
        entry = self.waitlist_repository.find_by_user_and_event(user_id, event_id)
        return entry is not None


# Singleton instances
user_service = UserService()
event_service = EventService()
registration_service = RegistrationService()
