---
inclusion: fileMatch
fileMatchPattern: '(main\.py|.*api.*|.*route.*|.*endpoint.*|.*handler.*)'
---

# API Standards and Conventions

This document defines the REST API standards and conventions for this project. These guidelines ensure consistency, predictability, and best practices across all API endpoints.

## HTTP Methods

Use HTTP methods according to their semantic meaning:

### GET
- **Purpose:** Retrieve resources
- **Idempotent:** Yes
- **Safe:** Yes (no side effects)
- **Request Body:** Not allowed
- **Success Codes:** 200 (OK), 206 (Partial Content)
- **Example:** `GET /events` - List all events

### POST
- **Purpose:** Create new resources
- **Idempotent:** No
- **Safe:** No
- **Request Body:** Required
- **Success Codes:** 201 (Created), 202 (Accepted)
- **Response:** Include `Location` header with new resource URI
- **Example:** `POST /events` - Create a new event

### PUT
- **Purpose:** Update/replace entire resource
- **Idempotent:** Yes
- **Safe:** No
- **Request Body:** Required (full resource)
- **Success Codes:** 200 (OK), 204 (No Content)
- **Example:** `PUT /events/{id}` - Update an event

### PATCH
- **Purpose:** Partial update of resource
- **Idempotent:** Yes
- **Safe:** No
- **Request Body:** Required (partial resource)
- **Success Codes:** 200 (OK), 204 (No Content)
- **Example:** `PATCH /events/{id}` - Update specific fields

### DELETE
- **Purpose:** Remove resources
- **Idempotent:** Yes
- **Safe:** No
- **Request Body:** Not allowed
- **Success Codes:** 204 (No Content), 200 (OK with body)
- **Example:** `DELETE /events/{id}` - Delete an event

## HTTP Status Codes

### Success Codes (2xx)

- **200 OK** - Request succeeded, response includes body
- **201 Created** - Resource created successfully
  - Must include `Location` header
  - Should return created resource in body
- **202 Accepted** - Request accepted for async processing
- **204 No Content** - Success with no response body (DELETE, PUT)

### Client Error Codes (4xx)

- **400 Bad Request** - Invalid request syntax or validation error
- **401 Unauthorized** - Authentication required or failed
- **403 Forbidden** - Authenticated but not authorized
- **404 Not Found** - Resource does not exist
- **405 Method Not Allowed** - HTTP method not supported for endpoint
- **409 Conflict** - Request conflicts with current state
- **422 Unprocessable Entity** - Validation error (semantic)
- **429 Too Many Requests** - Rate limit exceeded

### Server Error Codes (5xx)

- **500 Internal Server Error** - Unexpected server error
- **502 Bad Gateway** - Invalid response from upstream
- **503 Service Unavailable** - Temporary unavailability
- **504 Gateway Timeout** - Upstream timeout

## JSON Response Format Standards

### Success Response Format

All successful responses should follow this structure:

```json
{
  "data": { /* resource or array of resources */ },
  "meta": { /* optional metadata */ }
}
```

**Single Resource:**
```json
{
  "eventId": "uuid",
  "title": "Event Title",
  "status": "active",
  "createdAt": "2025-12-04T00:00:00Z",
  "updatedAt": "2025-12-04T00:00:00Z"
}
```

**Collection:**
```json
[
  { "eventId": "uuid-1", "title": "Event 1" },
  { "eventId": "uuid-2", "title": "Event 2" }
]
```

**With Pagination:**
```json
{
  "data": [ /* array of resources */ ],
  "meta": {
    "total": 100,
    "page": 1,
    "pageSize": 20,
    "totalPages": 5
  }
}
```

### Error Response Format

All error responses must follow this consistent structure:

```json
{
  "detail": "Human-readable error message",
  "type": "error_type_identifier",
  "status": 400,
  "errors": [ /* optional array of specific errors */ ]
}
```

**Validation Error Example:**
```json
{
  "detail": "Validation error",
  "type": "validation_error",
  "status": 422,
  "errors": [
    {
      "field": "capacity",
      "message": "Must be greater than 0",
      "value": -5
    },
    {
      "field": "date",
      "message": "Invalid date format",
      "value": "invalid-date"
    }
  ]
}
```

**Not Found Error Example:**
```json
{
  "detail": "Event with ID abc-123 not found",
  "type": "not_found",
  "status": 404
}
```

**Database Error Example:**
```json
{
  "detail": "Database operation failed",
  "type": "database_error",
  "status": 500,
  "operation": "update"
}
```

## URL and Endpoint Conventions

### Resource Naming
- Use **plural nouns** for collections: `/events`, `/users`
- Use **lowercase** with hyphens for multi-word resources: `/event-registrations`
- Avoid verbs in URLs (use HTTP methods instead)

### URL Structure
```
/{resource}                    # Collection
/{resource}/{id}               # Single resource
/{resource}/{id}/{sub-resource} # Nested resource
```

**Examples:**
- `GET /events` - List events
- `GET /events/123` - Get event 123
- `GET /events/123/attendees` - Get attendees for event 123

### Query Parameters

Use query parameters for:
- **Filtering:** `?status=active&location=SF`
- **Sorting:** `?sort=date&order=desc`
- **Pagination:** `?page=2&limit=20`
- **Field selection:** `?fields=id,title,date`
- **Search:** `?q=conference`

**Examples:**
```
GET /events?status=active&limit=10
GET /events?sort=date&order=desc
GET /events?q=tech&location=SF
```

## Request Headers

### Required Headers
- `Content-Type: application/json` - For POST, PUT, PATCH requests
- `Accept: application/json` - For all requests

### Optional Headers
- `Authorization: Bearer {token}` - For authenticated requests
- `X-Request-ID: {uuid}` - For request tracing
- `If-Match: {etag}` - For optimistic locking

## Response Headers

### Standard Headers
- `Content-Type: application/json; charset=utf-8`
- `X-Request-ID: {uuid}` - Echo request ID for tracing
- `X-RateLimit-Limit: 1000` - Rate limit maximum
- `X-RateLimit-Remaining: 999` - Remaining requests
- `X-RateLimit-Reset: 1638360000` - Reset timestamp

### Caching Headers
- `Cache-Control: no-cache` - For dynamic content
- `Cache-Control: max-age=3600` - For cacheable content
- `ETag: "version-hash"` - For resource versioning

## Data Format Standards

### Dates and Times
- Use **ISO 8601** format: `2025-12-04T00:00:00Z`
- Always use **UTC timezone** (Z suffix)
- Field names: `createdAt`, `updatedAt`, `deletedAt`

### Identifiers
- Use **UUIDs** for resource IDs: `550e8400-e29b-41d4-a716-446655440000`
- Field name: `{resource}Id` (e.g., `eventId`, `userId`)

### Booleans
- Use `true` or `false` (lowercase)
- Avoid `1/0` or `"true"/"false"` strings

### Null Values
- Include fields with `null` value rather than omitting
- Exception: Optional fields in PATCH requests

### Numbers
- Use JSON numbers, not strings: `"capacity": 100`
- For currency, use integers (cents): `"price": 1999` (for $19.99)

### Enums
- Use lowercase strings with underscores: `"status": "in_progress"`
- Document all possible values in API docs

## Validation Rules

### Request Validation
- Validate all input before processing
- Return **422 Unprocessable Entity** for validation errors
- Include specific field-level errors in response
- Validate data types, formats, ranges, and business rules

### Field Constraints
```python
# Example validation rules
{
  "title": {
    "type": "string",
    "minLength": 1,
    "maxLength": 200,
    "required": true
  },
  "capacity": {
    "type": "integer",
    "minimum": 1,
    "maximum": 100000,
    "required": true
  },
  "status": {
    "type": "string",
    "enum": ["draft", "published", "active", "cancelled", "completed"],
    "required": true
  }
}
```

## Error Handling Best Practices

### Error Messages
- Be **specific** but don't expose sensitive information
- Use **human-readable** language
- Include **actionable** guidance when possible
- Avoid technical jargon in user-facing messages

### Logging
- Log all errors with context (request ID, user ID, timestamp)
- Include stack traces for 5xx errors
- Don't log sensitive data (passwords, tokens, PII)

### Error Recovery
- Implement retry logic for transient failures
- Use exponential backoff for rate limiting
- Provide clear guidance for client-side error handling

## CORS Configuration

### Allowed Origins
- Development: `http://localhost:*`
- Production: Specific domains only

### Allowed Methods
- `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`

### Allowed Headers
- `Content-Type`, `Authorization`, `X-Request-ID`

### Exposed Headers
- `X-Total-Count`, `X-RateLimit-*`

## Versioning Strategy

### URL Versioning (Recommended)
```
/v1/events
/v2/events
```

### Header Versioning (Alternative)
```
Accept: application/vnd.api.v1+json
```

### Version Lifecycle
- Support at least 2 versions simultaneously
- Deprecate with 6-month notice
- Document breaking changes clearly

## Security Best Practices

### Input Sanitization
- Validate and sanitize all user input
- Prevent SQL injection, XSS, and other attacks
- Use parameterized queries for database operations

### Authentication & Authorization
- Use JWT tokens or OAuth 2.0
- Implement proper token expiration
- Validate permissions for each request

### Rate Limiting
- Implement per-user and per-IP rate limits
- Return `429 Too Many Requests` when exceeded
- Include `Retry-After` header

### HTTPS Only
- Enforce HTTPS in production
- Redirect HTTP to HTTPS
- Use HSTS headers

## Performance Guidelines

### Response Times
- Target: < 200ms for simple queries
- Maximum: < 1000ms for complex operations
- Use async processing for long-running tasks

### Pagination
- Default page size: 20 items
- Maximum page size: 100 items
- Use cursor-based pagination for large datasets

### Caching
- Cache GET responses when appropriate
- Use ETags for conditional requests
- Implement cache invalidation strategy

## Documentation Requirements

### Endpoint Documentation
Each endpoint must document:
- HTTP method and URL
- Request parameters (path, query, body)
- Request/response examples
- Possible status codes
- Authentication requirements
- Rate limits

### OpenAPI/Swagger
- Maintain OpenAPI 3.0 specification
- Auto-generate from code when possible
- Keep documentation in sync with implementation

## Testing Standards

### Test Coverage
- Unit tests for business logic
- Integration tests for API endpoints
- Contract tests for external dependencies

### Test Scenarios
- Happy path (success cases)
- Error cases (validation, not found, etc.)
- Edge cases (boundary values, empty data)
- Security tests (authentication, authorization)

## Examples

### Complete Request/Response Flow

**Request:**
```http
POST /events HTTP/1.1
Host: api.example.com
Content-Type: application/json
Authorization: Bearer eyJhbGc...
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000

{
  "title": "Tech Conference 2025",
  "description": "Annual technology conference",
  "date": "2025-06-15T09:00:00Z",
  "location": "San Francisco, CA",
  "capacity": 500,
  "organizer": "Tech Corp",
  "status": "published"
}
```

**Success Response:**
```http
HTTP/1.1 201 Created
Content-Type: application/json; charset=utf-8
Location: /events/550e8400-e29b-41d4-a716-446655440000
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000

{
  "eventId": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Tech Conference 2025",
  "description": "Annual technology conference",
  "date": "2025-06-15T09:00:00Z",
  "location": "San Francisco, CA",
  "capacity": 500,
  "organizer": "Tech Corp",
  "status": "published",
  "createdAt": "2025-12-04T00:00:00Z",
  "updatedAt": "2025-12-04T00:00:00Z"
}
```

**Error Response:**
```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json; charset=utf-8
X-Request-ID: 550e8400-e29b-41d4-a716-446655440000

{
  "detail": "Validation error",
  "type": "validation_error",
  "status": 422,
  "errors": [
    {
      "field": "capacity",
      "message": "Must be greater than 0",
      "value": -5
    }
  ]
}
```

---

**Note:** These standards should be applied consistently across all API endpoints. When in doubt, prioritize clarity, consistency, and developer experience.
