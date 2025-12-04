# Design Document

**Version:** 1.0  
**Last Updated:** December 4, 2024

## Overview

The user registration system is a domain-driven application that manages users, events, and registrations with capacity constraints and waitlist functionality. The system provides a clean separation between domain logic, data persistence, and API interfaces. The core design emphasizes immutability where possible, explicit error handling, and transactional consistency for registration operations.

The system will be implemented in Python, leveraging the existing FastAPI backend infrastructure. It will use SQLite for data persistence (consistent with the existing database.py pattern) and provide RESTful API endpoints for all operations.

## Architecture

The system follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────┐
│         API Layer (FastAPI)         │
│  - Request validation               │
│  - Response formatting              │
│  - HTTP error mapping               │
└─────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│        Service Layer                │
│  - Business logic orchestration     │
│  - Transaction management           │
│  - Domain rule enforcement          │
└─────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│        Domain Layer                 │
│  - User, Event, Registration models │
│  - Domain validation                │
│  - Business rules                   │
└─────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│      Repository Layer               │
│  - Data access abstraction          │
│  - SQL query execution              │
│  - Data mapping                     │
└─────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│      Database (SQLite)              │
└─────────────────────────────────────┘
```

### Key Architectural Decisions

1. **Repository Pattern**: Abstracts data access to enable testing and potential database migration
2. **Service Layer**: Encapsulates complex business logic and coordinates multiple repository operations
3. **Domain Models**: Rich domain objects with validation and business rules
4. **Explicit Error Types**: Custom exception hierarchy for clear error handling
5. **Transactional Consistency**: Critical operations (unregister + waitlist promotion) execute atomically

## Components and Interfaces

### Domain Models

**User**
- Attributes: `user_id: str`, `name: str`
- Validation: Non-empty userId and name
- Immutable after creation

**Event**
- Attributes: `event_id: str`, `name: str`, `capacity: int`, `has_waitlist: bool`
- Validation: Capacity must be positive integer
- Immutable configuration after creation

**Registration**
- Attributes: `registration_id: str`, `user_id: str`, `event_id: str`, `status: RegistrationStatus`, `created_at: datetime`
- Status enum: `ACTIVE`, `WAITLISTED`
- Validation: Valid user and event references

**WaitlistEntry**
- Attributes: `entry_id: str`, `user_id: str`, `event_id: str`, `position: int`, `created_at: datetime`
- Position: 1-indexed, sequential ordering

### Service Layer

**UserService**
```python
class UserService:
    def create_user(user_id: str, name: str) -> User
    def get_user(user_id: str) -> Optional[User]
```

**EventService**
```python
class EventService:
    def create_event(event_id: str, name: str, capacity: int, has_waitlist: bool) -> Event
    def get_event(event_id: str) -> Optional[Event]
    def get_available_capacity(event_id: str) -> int
```

**RegistrationService**
```python
class RegistrationService:
    def register_user(user_id: str, event_id: str) -> RegistrationResult
    def unregister_user(user_id: str, event_id: str) -> None
    def get_user_registrations(user_id: str) -> List[Event]
    def is_user_registered(user_id: str, event_id: str) -> bool
    def is_user_waitlisted(user_id: str, event_id: str) -> bool
```

**RegistrationResult** (Union Type)
- `ActiveRegistration(registration: Registration)`
- `WaitlistRegistration(entry: WaitlistEntry)`
- `RegistrationDenied(reason: str)`

### Repository Layer

**UserRepository**
```python
class UserRepository:
    def save(user: User) -> None
    def find_by_id(user_id: str) -> Optional[User]
    def exists(user_id: str) -> bool
```

**EventRepository**
```python
class EventRepository:
    def save(event: Event) -> None
    def find_by_id(event_id: str) -> Optional[Event]
    def exists(event_id: str) -> bool
```

**RegistrationRepository**
```python
class RegistrationRepository:
    def save(registration: Registration) -> None
    def delete(user_id: str, event_id: str) -> None
    def find_by_user_and_event(user_id: str, event_id: str) -> Optional[Registration]
    def find_active_by_user(user_id: str) -> List[Registration]
    def count_active_by_event(event_id: str) -> int
    def find_by_event(event_id: str) -> List[Registration]
```

**WaitlistRepository**
```python
class WaitlistRepository:
    def add(entry: WaitlistEntry) -> None
    def remove(user_id: str, event_id: str) -> None
    def find_by_user_and_event(user_id: str, event_id: str) -> Optional[WaitlistEntry]
    def find_first_by_event(event_id: str) -> Optional[WaitlistEntry]
    def get_next_position(event_id: str) -> int
    def find_by_event(event_id: str) -> List[WaitlistEntry]
```

### API Endpoints

```
POST   /users                    - Create user
GET    /users/{user_id}          - Get user details

POST   /events                   - Create event
GET    /events/{event_id}        - Get event details

POST   /registrations            - Register user for event
DELETE /registrations            - Unregister user from event
GET    /users/{user_id}/events   - List user's registered events
```

## Data Models

### Database Schema

**users**
```sql
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**events**
```sql
CREATE TABLE events (
    event_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    capacity INTEGER NOT NULL CHECK(capacity > 0),
    has_waitlist BOOLEAN NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**registrations**
```sql
CREATE TABLE registrations (
    registration_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    event_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'WAITLISTED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (event_id) REFERENCES events(event_id),
    UNIQUE(user_id, event_id)
);
```

**waitlist**
```sql
CREATE TABLE waitlist (
    entry_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    event_id TEXT NOT NULL,
    position INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (event_id) REFERENCES events(event_id),
    UNIQUE(user_id, event_id),
    UNIQUE(event_id, position)
);
```

### Domain Object Mapping

Domain objects will be mapped to/from database rows using simple dataclass constructors. The repository layer handles all SQL operations and returns fully constructed domain objects.


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, several properties can be consolidated to eliminate redundancy:

- Properties 1.1 and 1.4 both test user creation and retrieval - these can be combined into a single round-trip property
- Properties 2.1, 2.2, 2.3, and 2.5 all test event creation and retrieval - these can be combined into a single round-trip property
- Properties 3.1, 3.4 test registration creation and persistence - these can be combined with the capacity tracking property 3.3
- Properties 6.3 and 6.4 both test waitlist promotion - 6.4 is implied by 6.3 and can be consolidated
- Property 7.4 is too vague and is already covered by 7.1 and 7.2

### User Management Properties

**Property 1: User creation round-trip**
*For any* valid userId and name, creating a user and then retrieving it should return a user with the same userId and name.
**Validates: Requirements 1.1, 1.4**

**Property 2: Duplicate user rejection**
*For any* userId that already exists in the system, attempting to create another user with that userId should be rejected with an error.
**Validates: Requirements 1.2**

**Property 3: Invalid user data rejection**
*For any* user creation request where userId or name is empty or contains only whitespace, the system should reject the request with a validation error.
**Validates: Requirements 1.3**

### Event Management Properties

**Property 4: Event creation round-trip**
*For any* valid event configuration (positive capacity, any waitlist setting), creating an event and then retrieving it should return an event with the same configuration.
**Validates: Requirements 2.1, 2.2, 2.3, 2.5**

### Registration Properties

**Property 5: Successful registration creates active registration and decrements capacity**
*For any* user and event with available capacity, registering the user should create an active registration and decrease the available capacity by exactly 1.
**Validates: Requirements 3.1, 3.3, 3.4**

**Property 6: Duplicate registration rejection**
*For any* user already registered for an event, attempting to register them again for the same event should be rejected with an error.
**Validates: Requirements 3.2**

**Property 7: Full event without waitlist rejects registration**
*For any* event at full capacity with no waitlist enabled, attempting to register a new user should be rejected with an error message indicating the event is full.
**Validates: Requirements 4.1, 4.2, 4.3**

### Waitlist Properties

**Property 8: Full event with waitlist adds user to waitlist**
*For any* event at full capacity with waitlist enabled, attempting to register a new user should add them to the waitlist with a position based on order of arrival.
**Validates: Requirements 5.1, 5.2, 5.3**

**Property 9: Duplicate waitlist rejection**
*For any* user already on a waitlist for an event, attempting to add them to the same waitlist again should be rejected with an error.
**Validates: Requirements 5.4**

**Property 10: Mutual exclusion of active registration and waitlist**
*For any* user and event, the user cannot simultaneously have both an active registration and a waitlist entry for the same event.
**Validates: Requirements 5.5**

### Unregistration Properties

**Property 11: Unregistration removes registration and increments capacity**
*For any* user with an active registration for an event, unregistering should remove the registration and increase the available capacity by exactly 1.
**Validates: Requirements 6.1, 6.2**

**Property 12: Unregistration with waitlist promotes first waitlisted user**
*For any* event with active registrations and a non-empty waitlist, when a user unregisters, the first user on the waitlist should be promoted to an active registration and removed from the waitlist.
**Validates: Requirements 6.3, 6.4**

**Property 13: Invalid unregistration rejection**
*For any* user not registered for an event, attempting to unregister them from that event should be rejected with an error.
**Validates: Requirements 6.5**

### Query Properties

**Property 14: User registrations query returns only active registrations**
*For any* user, querying their registered events should return exactly the set of events where they have an active registration, excluding any events where they are only on the waitlist.
**Validates: Requirements 7.1, 7.2**

## Error Handling

### Exception Hierarchy

```python
class RegistrationSystemError(Exception):
    """Base exception for all registration system errors"""
    pass

class ValidationError(RegistrationSystemError):
    """Raised when input validation fails"""
    pass

class DuplicateError(RegistrationSystemError):
    """Raised when attempting to create a duplicate resource"""
    pass

class NotFoundError(RegistrationSystemError):
    """Raised when a requested resource doesn't exist"""
    pass

class CapacityError(RegistrationSystemError):
    """Raised when event capacity constraints are violated"""
    pass

class RegistrationError(RegistrationSystemError):
    """Raised when registration operations fail"""
    pass
```

### Error Handling Strategy

1. **Input Validation**: All inputs validated at service layer before processing
2. **Domain Validation**: Domain models validate their own invariants
3. **Explicit Errors**: All error conditions mapped to specific exception types
4. **Transaction Rollback**: Database transactions rolled back on any error
5. **API Error Mapping**: Exceptions mapped to appropriate HTTP status codes
   - `ValidationError` → 400 Bad Request
   - `DuplicateError` → 409 Conflict
   - `NotFoundError` → 404 Not Found
   - `CapacityError` → 409 Conflict
   - `RegistrationError` → 400 Bad Request

### Critical Error Scenarios

1. **Concurrent Registration**: Two users registering for the last spot simultaneously
   - Solution: Database-level unique constraint + transaction isolation
2. **Waitlist Promotion Race**: Multiple unregistrations triggering simultaneous promotions
   - Solution: Atomic transaction for unregister + promote operation
3. **Capacity Underflow**: Unregistering when capacity tracking is inconsistent
   - Solution: Validate capacity state before operations, use CHECK constraints

## Testing Strategy

### Unit Testing

Unit tests will verify specific examples and integration points:

- **Model Validation**: Test domain model validation rules with specific valid/invalid inputs
- **Repository Operations**: Test CRUD operations with known data
- **Service Orchestration**: Test service methods coordinate repositories correctly
- **API Endpoints**: Test request/response handling and error mapping
- **Edge Cases**: Empty lists, boundary values, null handling

Example unit tests:
- User creation with empty name is rejected
- Event creation with capacity=0 is rejected
- Unregistering from non-existent event returns 404
- Listing events for user with no registrations returns empty list

### Property-Based Testing

Property-based tests will verify universal correctness properties across all inputs using the **Hypothesis** library for Python. Each property test will:

- Run a minimum of 100 iterations with randomly generated inputs
- Be tagged with a comment referencing the specific correctness property from this design document
- Use the format: `# Feature: user-registration, Property {number}: {property_text}`

**Test Data Generators**:
- `user_id_strategy`: Generates valid user IDs (non-empty strings)
- `name_strategy`: Generates valid names (non-empty strings)
- `event_id_strategy`: Generates valid event IDs
- `capacity_strategy`: Generates positive integers (1-1000)
- `invalid_string_strategy`: Generates empty/whitespace strings

**Property Test Coverage**:
Each of the 14 correctness properties will be implemented as a separate property-based test. The tests will use Hypothesis strategies to generate random valid inputs and verify the properties hold across all generated cases.

**Test Organization**:
- `test_user_properties.py`: Properties 1-3 (user management)
- `test_event_properties.py`: Property 4 (event management)
- `test_registration_properties.py`: Properties 5-7 (registration)
- `test_waitlist_properties.py`: Properties 8-10 (waitlist)
- `test_unregistration_properties.py`: Properties 11-13 (unregistration)
- `test_query_properties.py`: Property 14 (queries)

### Integration Testing

Integration tests will verify end-to-end workflows:
- Complete registration flow: create user → create event → register → verify
- Waitlist flow: fill event → add to waitlist → unregister → verify promotion
- Multi-user scenarios: multiple users registering for same event

### Test Database

All tests will use an in-memory SQLite database that is created fresh for each test to ensure isolation and repeatability.
