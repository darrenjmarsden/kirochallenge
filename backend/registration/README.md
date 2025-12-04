# User Registration System

A comprehensive event registration system with capacity management and waitlist functionality.

## Features

- **User Management**: Create and manage users with unique identifiers
- **Event Management**: Create events with capacity constraints and optional waitlists
- **Registration**: Register users for events with automatic capacity tracking
- **Waitlist**: Automatic waitlist management when events reach capacity
- **Promotion**: Automatic promotion from waitlist when spots become available

## API Endpoints

### Users

- `POST /registration/users` - Create a new user
- `GET /registration/users/{user_id}` - Get user details

### Events

- `POST /registration/events` - Create a new event
- `GET /registration/events/{event_id}` - Get event details
- `GET /registration/events/{event_id}/capacity` - Get available capacity

### Registrations

- `POST /registration/registrations` - Register a user for an event
- `DELETE /registration/registrations?userId={user_id}&eventId={event_id}` - Unregister a user
- `GET /registration/users/{user_id}/events` - List user's registered events

## Architecture

The system follows a layered architecture:

```
API Layer (routes.py)
    ↓
Service Layer (services.py)
    ↓
Repository Layer (repositories.py)
    ↓
Database Layer (database.py)
```

### Components

- **Models** (`models.py`): Pydantic models for request/response validation
- **Exceptions** (`exceptions.py`): Custom exception hierarchy
- **Database** (`database.py`): DynamoDB connection and table management
- **Repositories** (`repositories.py`): Data access layer
- **Services** (`services.py`): Business logic layer
- **Routes** (`routes.py`): FastAPI endpoints

## Database Schema

### Tables

1. **users-table**
   - Primary Key: `userId` (String)
   - Attributes: `name`, `createdAt`

2. **registration-events-table**
   - Primary Key: `eventId` (String)
   - Attributes: `name`, `capacity`, `hasWaitlist`, `createdAt`

3. **registrations-table**
   - Primary Key: `registrationId` (String)
   - GSI: `UserIdIndex` (userId)
   - GSI: `EventIdIndex` (eventId)
   - Attributes: `userId`, `eventId`, `status`, `createdAt`

4. **waitlist-table**
   - Primary Key: `entryId` (String)
   - GSI: `EventIdPositionIndex` (eventId, position)
   - Attributes: `userId`, `eventId`, `position`, `createdAt`

## Business Rules

1. **User Creation**
   - UserId must be unique
   - Name cannot be empty

2. **Event Creation**
   - Capacity must be positive
   - Waitlist is optional

3. **Registration**
   - User must exist
   - Event must exist
   - User cannot register twice for same event
   - If event is full and has no waitlist, registration is denied
   - If event is full and has waitlist, user is added to waitlist

4. **Unregistration**
   - User must be registered
   - When user unregisters, first waitlisted user is automatically promoted

5. **Waitlist**
   - Users are added in order (FIFO)
   - User cannot be on waitlist and have active registration simultaneously

## Error Handling

The system uses a custom exception hierarchy:

- `ValidationError` (400) - Invalid input data
- `DuplicateError` (409) - Resource already exists
- `NotFoundError` (404) - Resource not found
- `CapacityError` (409) - Event capacity exceeded
- `RegistrationError` (400) - Registration operation failed

## Testing

Run the test script:

```bash
cd backend
python test_registration.py
```

Note: Requires DynamoDB tables to be set up (either AWS or DynamoDB Local).

## Deployment

The registration system is integrated into the main backend infrastructure. Deploy using:

```bash
cd infrastructure
cdk deploy
```

This will create all necessary DynamoDB tables and configure the Lambda function with appropriate permissions.
