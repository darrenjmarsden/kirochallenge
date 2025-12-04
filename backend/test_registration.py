"""Simple test script for registration system"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from registration.services import user_service, event_service, registration_service
from registration.exceptions import (
    ValidationError,
    DuplicateError,
    NotFoundError,
    CapacityError
)


def test_user_creation():
    """Test user creation"""
    print("\n=== Testing User Creation ===")
    try:
        user = user_service.create_user("user1", "John Doe")
        print(f"✓ Created user: {user}")
        
        # Test duplicate
        try:
            user_service.create_user("user1", "Jane Doe")
            print("✗ Should have raised DuplicateError")
        except DuplicateError as e:
            print(f"✓ Duplicate user rejected: {e}")
        
        # Test empty name
        try:
            user_service.create_user("user2", "")
            print("✗ Should have raised ValidationError")
        except ValidationError as e:
            print(f"✓ Empty name rejected: {e}")
            
    except Exception as e:
        print(f"✗ Error: {e}")


def test_event_creation():
    """Test event creation"""
    print("\n=== Testing Event Creation ===")
    try:
        event = event_service.create_event(None, "Tech Conference", 2, True)
        print(f"✓ Created event: {event}")
        
        # Test invalid capacity
        try:
            event_service.create_event(None, "Bad Event", 0, False)
            print("✗ Should have raised ValidationError")
        except ValidationError as e:
            print(f"✓ Invalid capacity rejected: {e}")
            
    except Exception as e:
        print(f"✗ Error: {e}")


def test_registration_flow():
    """Test registration flow"""
    print("\n=== Testing Registration Flow ===")
    try:
        # Create users
        user1 = user_service.create_user("reg_user1", "Alice")
        user2 = user_service.create_user("reg_user2", "Bob")
        user3 = user_service.create_user("reg_user3", "Charlie")
        print(f"✓ Created 3 users")
        
        # Create event with capacity 2 and waitlist
        event = event_service.create_event("event1", "Workshop", 2, True)
        print(f"✓ Created event with capacity 2 and waitlist")
        
        # Register first user
        result1 = registration_service.register_user("reg_user1", "event1")
        print(f"✓ User 1 registered: {result1['message']}")
        
        # Register second user
        result2 = registration_service.register_user("reg_user2", "event1")
        print(f"✓ User 2 registered: {result2['message']}")
        
        # Register third user (should go to waitlist)
        result3 = registration_service.register_user("reg_user3", "event1")
        print(f"✓ User 3 registered: {result3['message']}")
        
        # Check capacity
        available = event_service.get_available_capacity("event1")
        print(f"✓ Available capacity: {available}")
        
        # Get user 1's events
        events = registration_service.get_user_registrations("reg_user1")
        print(f"✓ User 1 is registered for {len(events)} event(s)")
        
        # Unregister user 1 (should promote user 3)
        unregister_result = registration_service.unregister_user("reg_user1", "event1")
        print(f"✓ User 1 unregistered: {unregister_result['message']}")
        if unregister_result['promoted']:
            print(f"✓ User 3 promoted from waitlist")
        
        # Check capacity again
        available = event_service.get_available_capacity("event1")
        print(f"✓ Available capacity after unregister: {available}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


def test_full_event_without_waitlist():
    """Test full event without waitlist"""
    print("\n=== Testing Full Event Without Waitlist ===")
    try:
        # Create users
        user1 = user_service.create_user("nowait_user1", "Dave")
        user2 = user_service.create_user("nowait_user2", "Eve")
        user3 = user_service.create_user("nowait_user3", "Frank")
        
        # Create event with capacity 2 and NO waitlist
        event = event_service.create_event("event2", "Limited Workshop", 2, False)
        print(f"✓ Created event with capacity 2 and NO waitlist")
        
        # Register first two users
        registration_service.register_user("nowait_user1", "event2")
        registration_service.register_user("nowait_user2", "event2")
        print(f"✓ Registered 2 users (event full)")
        
        # Try to register third user (should fail)
        try:
            registration_service.register_user("nowait_user3", "event2")
            print("✗ Should have raised CapacityError")
        except CapacityError as e:
            print(f"✓ Registration rejected: {e}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Starting Registration System Tests")
    print("=" * 50)
    
    # Note: These tests require DynamoDB tables to be set up
    # For local testing, you need DynamoDB Local running
    
    test_user_creation()
    test_event_creation()
    test_registration_flow()
    test_full_event_without_waitlist()
    
    print("\n" + "=" * 50)
    print("Tests completed!")
