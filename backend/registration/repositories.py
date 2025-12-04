"""Repository layer for data access"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr
import logging

from .database import registration_db
from .exceptions import NotFoundError, DuplicateError, RegistrationSystemError

logger = logging.getLogger(__name__)


class UserRepository:
    """Repository for user data access"""
    
    def __init__(self):
        self.table = registration_db.users_table
    
    def save(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save a user to the database"""
        try:
            timestamp = datetime.utcnow().isoformat()
            item = {
                "userId": user_data["userId"],
                "name": user_data["name"],
                "createdAt": timestamp
            }
            
            # Use condition to prevent overwriting existing user
            self.table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(userId)"
            )
            logger.info(f"Saved user: {item['userId']}")
            return item
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                raise DuplicateError(f"User with ID {user_data['userId']} already exists")
            logger.error(f"Failed to save user: {e.response['Error']['Message']}")
            raise RegistrationSystemError(f"Failed to save user: {e.response['Error']['Message']}")
    
    def find_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Find a user by ID"""
        try:
            response = self.table.get_item(Key={"userId": user_id})
            return response.get("Item")
        except ClientError as e:
            logger.error(f"Failed to find user {user_id}: {e.response['Error']['Message']}")
            raise RegistrationSystemError(f"Failed to find user: {e.response['Error']['Message']}")
    
    def exists(self, user_id: str) -> bool:
        """Check if a user exists"""
        return self.find_by_id(user_id) is not None


class EventRepository:
    """Repository for registration event data access"""
    
    def __init__(self):
        self.table = registration_db.registration_events_table
    
    def save(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save an event to the database"""
        try:
            event_id = event_data.get('eventId') or str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()
            
            item = {
                "eventId": event_id,
                "name": event_data["name"],
                "capacity": event_data["capacity"],
                "hasWaitlist": event_data.get("hasWaitlist", False),
                "createdAt": timestamp
            }
            
            self.table.put_item(Item=item)
            logger.info(f"Saved event: {item['eventId']}")
            return item
        except ClientError as e:
            logger.error(f"Failed to save event: {e.response['Error']['Message']}")
            raise RegistrationSystemError(f"Failed to save event: {e.response['Error']['Message']}")
    
    def find_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Find an event by ID"""
        try:
            response = self.table.get_item(Key={"eventId": event_id})
            return response.get("Item")
        except ClientError as e:
            logger.error(f"Failed to find event {event_id}: {e.response['Error']['Message']}")
            raise RegistrationSystemError(f"Failed to find event: {e.response['Error']['Message']}")
    
    def exists(self, event_id: str) -> bool:
        """Check if an event exists"""
        return self.find_by_id(event_id) is not None


class RegistrationRepository:
    """Repository for registration data access"""
    
    def __init__(self):
        self.table = registration_db.registrations_table
    
    def save(self, registration_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save a registration to the database"""
        try:
            registration_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()
            
            item = {
                "registrationId": registration_id,
                "userId": registration_data["userId"],
                "eventId": registration_data["eventId"],
                "status": registration_data["status"],
                "createdAt": timestamp
            }
            
            self.table.put_item(Item=item)
            logger.info(f"Saved registration: {registration_id}")
            return item
        except ClientError as e:
            logger.error(f"Failed to save registration: {e.response['Error']['Message']}")
            raise RegistrationSystemError(f"Failed to save registration: {e.response['Error']['Message']}")
    
    def delete(self, user_id: str, event_id: str) -> None:
        """Delete a registration"""
        try:
            # First find the registration
            registration = self.find_by_user_and_event(user_id, event_id)
            if not registration:
                raise NotFoundError(f"No registration found for user {user_id} and event {event_id}")
            
            self.table.delete_item(Key={"registrationId": registration["registrationId"]})
            logger.info(f"Deleted registration for user {user_id} and event {event_id}")
        except ClientError as e:
            logger.error(f"Failed to delete registration: {e.response['Error']['Message']}")
            raise RegistrationSystemError(f"Failed to delete registration: {e.response['Error']['Message']}")
    
    def find_by_user_and_event(self, user_id: str, event_id: str) -> Optional[Dict[str, Any]]:
        """Find a registration by user and event"""
        try:
            response = self.table.query(
                IndexName='UserIdIndex',
                KeyConditionExpression=Key('userId').eq(user_id),
                FilterExpression=Attr('eventId').eq(event_id)
            )
            items = response.get('Items', [])
            return items[0] if items else None
        except ClientError as e:
            logger.error(f"Failed to find registration: {e.response['Error']['Message']}")
            raise RegistrationSystemError(f"Failed to find registration: {e.response['Error']['Message']}")
    
    def find_active_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Find all active registrations for a user"""
        try:
            response = self.table.query(
                IndexName='UserIdIndex',
                KeyConditionExpression=Key('userId').eq(user_id),
                FilterExpression=Attr('status').eq('ACTIVE')
            )
            return response.get('Items', [])
        except ClientError as e:
            logger.error(f"Failed to find user registrations: {e.response['Error']['Message']}")
            raise RegistrationSystemError(f"Failed to find user registrations: {e.response['Error']['Message']}")
    
    def count_active_by_event(self, event_id: str) -> int:
        """Count active registrations for an event"""
        try:
            response = self.table.query(
                IndexName='EventIdIndex',
                KeyConditionExpression=Key('eventId').eq(event_id),
                FilterExpression=Attr('status').eq('ACTIVE'),
                Select='COUNT'
            )
            return response.get('Count', 0)
        except ClientError as e:
            logger.error(f"Failed to count registrations: {e.response['Error']['Message']}")
            raise RegistrationSystemError(f"Failed to count registrations: {e.response['Error']['Message']}")
    
    def find_by_event(self, event_id: str) -> List[Dict[str, Any]]:
        """Find all registrations for an event"""
        try:
            response = self.table.query(
                IndexName='EventIdIndex',
                KeyConditionExpression=Key('eventId').eq(event_id)
            )
            return response.get('Items', [])
        except ClientError as e:
            logger.error(f"Failed to find event registrations: {e.response['Error']['Message']}")
            raise RegistrationSystemError(f"Failed to find event registrations: {e.response['Error']['Message']}")


class WaitlistRepository:
    """Repository for waitlist data access"""
    
    def __init__(self):
        self.table = registration_db.waitlist_table
    
    def add(self, entry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add an entry to the waitlist"""
        try:
            entry_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()
            
            item = {
                "entryId": entry_id,
                "userId": entry_data["userId"],
                "eventId": entry_data["eventId"],
                "position": entry_data["position"],
                "createdAt": timestamp
            }
            
            self.table.put_item(Item=item)
            logger.info(f"Added waitlist entry: {entry_id}")
            return item
        except ClientError as e:
            logger.error(f"Failed to add waitlist entry: {e.response['Error']['Message']}")
            raise RegistrationSystemError(f"Failed to add waitlist entry: {e.response['Error']['Message']}")
    
    def remove(self, user_id: str, event_id: str) -> None:
        """Remove an entry from the waitlist"""
        try:
            # First find the entry
            entry = self.find_by_user_and_event(user_id, event_id)
            if not entry:
                raise NotFoundError(f"No waitlist entry found for user {user_id} and event {event_id}")
            
            self.table.delete_item(Key={"entryId": entry["entryId"]})
            logger.info(f"Removed waitlist entry for user {user_id} and event {event_id}")
        except ClientError as e:
            logger.error(f"Failed to remove waitlist entry: {e.response['Error']['Message']}")
            raise RegistrationSystemError(f"Failed to remove waitlist entry: {e.response['Error']['Message']}")
    
    def find_by_user_and_event(self, user_id: str, event_id: str) -> Optional[Dict[str, Any]]:
        """Find a waitlist entry by user and event"""
        try:
            response = self.table.query(
                IndexName='EventIdPositionIndex',
                KeyConditionExpression=Key('eventId').eq(event_id),
                FilterExpression=Attr('userId').eq(user_id)
            )
            items = response.get('Items', [])
            return items[0] if items else None
        except ClientError as e:
            logger.error(f"Failed to find waitlist entry: {e.response['Error']['Message']}")
            raise RegistrationSystemError(f"Failed to find waitlist entry: {e.response['Error']['Message']}")
    
    def find_first_by_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Find the first entry in the waitlist for an event"""
        try:
            response = self.table.query(
                IndexName='EventIdPositionIndex',
                KeyConditionExpression=Key('eventId').eq(event_id),
                Limit=1,
                ScanIndexForward=True  # Sort by position ascending
            )
            items = response.get('Items', [])
            return items[0] if items else None
        except ClientError as e:
            logger.error(f"Failed to find first waitlist entry: {e.response['Error']['Message']}")
            raise RegistrationSystemError(f"Failed to find first waitlist entry: {e.response['Error']['Message']}")
    
    def get_next_position(self, event_id: str) -> int:
        """Get the next position number for the waitlist"""
        try:
            response = self.table.query(
                IndexName='EventIdPositionIndex',
                KeyConditionExpression=Key('eventId').eq(event_id),
                ScanIndexForward=False,  # Sort by position descending
                Limit=1,
                ProjectionExpression='position'
            )
            items = response.get('Items', [])
            if items:
                return items[0]['position'] + 1
            return 1
        except ClientError as e:
            logger.error(f"Failed to get next position: {e.response['Error']['Message']}")
            raise RegistrationSystemError(f"Failed to get next position: {e.response['Error']['Message']}")
    
    def find_by_event(self, event_id: str) -> List[Dict[str, Any]]:
        """Find all waitlist entries for an event"""
        try:
            response = self.table.query(
                IndexName='EventIdPositionIndex',
                KeyConditionExpression=Key('eventId').eq(event_id),
                ScanIndexForward=True  # Sort by position ascending
            )
            return response.get('Items', [])
        except ClientError as e:
            logger.error(f"Failed to find waitlist entries: {e.response['Error']['Message']}")
            raise RegistrationSystemError(f"Failed to find waitlist entries: {e.response['Error']['Message']}")


# Singleton instances
user_repository = UserRepository()
event_repository = EventRepository()
registration_repository = RegistrationRepository()
waitlist_repository = WaitlistRepository()
