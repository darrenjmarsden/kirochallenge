# Implementation Plan

- [ ] 1. Set up project structure and database schema
  - Create directory structure for domain models, repositories, services, and API routes
  - Implement database schema with tables for users, events, registrations, and waitlist
  - Set up database initialization and migration utilities
  - Configure test database setup for in-memory SQLite
  - _Requirements: 1.4, 2.5, 3.4, 5.3_

- [ ] 2. Implement domain models and validation
  - Create User model with userId and name attributes
  - Create Event model with eventId, name, capacity, and hasWaitlist attributes
  - Create Registration model with status enum (ACTIVE, WAITLISTED)
  - Create WaitlistEntry model with position tracking
  - Implement validation logic for all models (non-empty strings, positive capacity)
  - _Requirements: 1.1, 1.3, 2.1, 2.4_

- [ ]* 2.1 Write property test for user creation round-trip
  - **Property 1: User creation round-trip**
  - **Validates: Requirements 1.1, 1.4**

- [ ]* 2.2 Write property test for invalid user data rejection
  - **Property 3: Invalid user data rejection**
  - **Validates: Requirements 1.3**

- [ ]* 2.3 Write property test for event creation round-trip
  - **Property 4: Event creation round-trip**
  - **Validates: Requirements 2.1, 2.2, 2.3, 2.5**

- [ ] 3. Implement exception hierarchy
  - Create base RegistrationSystemError exception
  - Create ValidationError, DuplicateError, NotFoundError, CapacityError, RegistrationError exceptions
  - _Requirements: 1.2, 1.3, 2.4, 3.2, 4.1, 4.2, 5.4, 6.5_

- [ ] 4. Implement repository layer
  - Create UserRepository with save, find_by_id, and exists methods
  - Create EventRepository with save, find_by_id, and exists methods
  - Create RegistrationRepository with save, delete, find operations, and count_active_by_event
  - Create WaitlistRepository with add, remove, find operations, and get_next_position
  - Implement database connection management and transaction support
  - _Requirements: 1.4, 2.5, 3.4, 5.3, 6.1_

- [ ]* 4.1 Write unit tests for repository CRUD operations
  - Test user repository save and retrieval
  - Test event repository save and retrieval
  - Test registration repository operations
  - Test waitlist repository operations
  - _Requirements: 1.4, 2.5, 3.4, 5.3_

- [ ] 5. Implement UserService
  - Implement create_user method with validation and duplicate checking
  - Implement get_user method for retrieval
  - Handle ValidationError for empty fields and DuplicateError for existing userIds
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ]* 5.1 Write property test for duplicate user rejection
  - **Property 2: Duplicate user rejection**
  - **Validates: Requirements 1.2**

- [ ] 6. Implement EventService
  - Implement create_event method with capacity validation and waitlist configuration
  - Implement get_event method for retrieval
  - Implement get_available_capacity method to calculate remaining spots
  - Handle ValidationError for invalid capacity values
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 7. Implement RegistrationService core registration logic
  - Implement register_user method that checks capacity and creates active registrations
  - Implement logic to decrement available capacity on successful registration
  - Implement duplicate registration detection
  - Return RegistrationResult union type (ActiveRegistration, WaitlistRegistration, or RegistrationDenied)
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ]* 7.1 Write property test for successful registration
  - **Property 5: Successful registration creates active registration and decrements capacity**
  - **Validates: Requirements 3.1, 3.3, 3.4**

- [ ]* 7.2 Write property test for duplicate registration rejection
  - **Property 6: Duplicate registration rejection**
  - **Validates: Requirements 3.2**

- [ ] 8. Implement full event handling without waitlist
  - Add capacity checking logic to register_user method
  - Implement rejection logic when event is full and has no waitlist
  - Return clear error message indicating event is full
  - _Requirements: 4.1, 4.2, 4.3_

- [ ]* 8.1 Write property test for full event rejection
  - **Property 7: Full event without waitlist rejects registration**
  - **Validates: Requirements 4.1, 4.2, 4.3**

- [ ] 9. Implement waitlist functionality
  - Add waitlist logic to register_user method for full events with waitlist enabled
  - Implement position assignment based on order of arrival
  - Implement duplicate waitlist detection
  - Ensure mutual exclusion between active registration and waitlist
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ]* 9.1 Write property test for waitlist addition
  - **Property 8: Full event with waitlist adds user to waitlist**
  - **Validates: Requirements 5.1, 5.2, 5.3**

- [ ]* 9.2 Write property test for duplicate waitlist rejection
  - **Property 9: Duplicate waitlist rejection**
  - **Validates: Requirements 5.4**

- [ ]* 9.3 Write property test for mutual exclusion
  - **Property 10: Mutual exclusion of active registration and waitlist**
  - **Validates: Requirements 5.5**

- [ ] 10. Implement unregistration logic
  - Implement unregister_user method to remove active registrations
  - Implement capacity increment on unregistration
  - Handle error case for unregistering non-existent registrations
  - _Requirements: 6.1, 6.2, 6.5_

- [ ]* 10.1 Write property test for unregistration
  - **Property 11: Unregistration removes registration and increments capacity**
  - **Validates: Requirements 6.1, 6.2**

- [ ]* 10.2 Write property test for invalid unregistration rejection
  - **Property 13: Invalid unregistration rejection**
  - **Validates: Requirements 6.5**

- [ ] 11. Implement waitlist promotion logic
  - Add atomic transaction for unregister + promote operation
  - Implement logic to find first waitlisted user and promote to active registration
  - Remove promoted user from waitlist
  - Ensure promotion happens automatically on unregistration when waitlist exists
  - _Requirements: 6.3, 6.4_

- [ ]* 11.1 Write property test for waitlist promotion
  - **Property 12: Unregistration with waitlist promotes first waitlisted user**
  - **Validates: Requirements 6.3, 6.4**

- [ ] 12. Implement query operations
  - Implement get_user_registrations method to return list of events with active registrations
  - Implement is_user_registered helper method
  - Implement is_user_waitlisted helper method
  - Ensure waitlisted events are excluded from registered events list
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ]* 12.1 Write property test for user registrations query
  - **Property 14: User registrations query returns only active registrations**
  - **Validates: Requirements 7.1, 7.2**

- [ ] 13. Implement API layer with FastAPI
  - Create POST /users endpoint for user creation
  - Create GET /users/{user_id} endpoint for user retrieval
  - Create POST /events endpoint for event creation
  - Create GET /events/{event_id} endpoint for event retrieval
  - Create POST /registrations endpoint for registration
  - Create DELETE /registrations endpoint for unregistration
  - Create GET /users/{user_id}/events endpoint for listing user's events
  - Implement request validation using Pydantic models
  - Map exceptions to appropriate HTTP status codes
  - _Requirements: All requirements_

- [ ]* 13.1 Write unit tests for API endpoints
  - Test request validation and error responses
  - Test successful operations return correct status codes
  - Test error mapping (400, 404, 409)
  - _Requirements: All requirements_

- [ ] 14. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ]* 15. Write integration tests for end-to-end workflows
  - Test complete registration flow: create user → create event → register → verify
  - Test waitlist flow: fill event → add to waitlist → unregister → verify promotion
  - Test multi-user concurrent registration scenarios
  - Test edge cases: empty lists, boundary values
  - _Requirements: All requirements_
