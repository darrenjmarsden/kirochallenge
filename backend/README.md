# FastAPI Events Backend

REST API for managing events with DynamoDB storage, designed for serverless deployment on AWS Lambda.

## 🚀 Features

- **CRUD Operations** - Create, Read, Update, Delete events
- **Status Filtering** - Filter events by status (draft, published, active, cancelled, completed)
- **DynamoDB Integration** - Serverless NoSQL database
- **Input Validation** - Pydantic models with comprehensive validation
- **Error Handling** - Custom exceptions with detailed error messages
- **CORS Support** - Configurable cross-origin resource sharing
- **Logging** - Structured logging for debugging and monitoring
- **Lambda Ready** - Mangum adapter for AWS Lambda deployment

## 📁 Project Structure

```
backend/
├── main.py              # FastAPI app and route handlers
├── models.py            # Pydantic data models
├── database.py          # DynamoDB client
├── config.py            # Configuration management
├── exceptions.py        # Custom exception handlers
├── lambda_handler.py    # Lambda entry point
├── requirements.txt     # Python dependencies
└── docs/               # Auto-generated API documentation
```

## 🔧 Local Development Setup

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```bash
DYNAMODB_TABLE_NAME=events-table
AWS_REGION=us-west-2
# For local development with DynamoDB Local:
# AWS_ENDPOINT_URL=http://localhost:8000
```

### 4. Run Development Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## 📖 API Documentation

### Interactive Documentation

Once running locally, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Generated Documentation

View the auto-generated code documentation in the `docs/` folder:
```bash
open docs/index.html
```

To regenerate documentation:
```bash
pip install pdoc
python -m pdoc main models database config exceptions -o docs
```

## 🔌 API Endpoints

### Events Management

| Method | Endpoint | Description | Query Params |
|--------|----------|-------------|--------------|
| POST | `/events` | Create a new event | - |
| GET | `/events` | List all events | `limit`, `status` |
| GET | `/events/{id}` | Get specific event | - |
| PUT | `/events/{id}` | Update an event | - |
| DELETE | `/events/{id}` | Delete an event | - |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |

## 📝 Event Schema

### Create Event (POST /events)

```json
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

### Event Response

```json
{
  "eventId": "uuid-string",
  "title": "Tech Conference 2025",
  "description": "Annual technology conference",
  "date": "2025-06-15T09:00:00Z",
  "location": "San Francisco, CA",
  "capacity": 500,
  "organizer": "Tech Corp",
  "status": "published",
  "createdAt": "2025-12-04T00:44:05.599047",
  "updatedAt": "2025-12-04T00:44:05.599047"
}
```

### Update Event (PUT /events/{id})

All fields are optional:
```json
{
  "capacity": 600,
  "status": "active"
}
```

## 🎯 Event Status Values

- `draft` - Event is being planned
- `published` - Event is announced but not yet active
- `active` - Event is currently happening
- `cancelled` - Event has been cancelled
- `completed` - Event has finished

## 🧪 Testing with curl

**Create an event:**
```bash
curl -X POST http://localhost:8000/events \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Event",
    "description": "A test event",
    "date": "2025-12-31T18:00:00Z",
    "location": "Test Location",
    "capacity": 100,
    "organizer": "Test Org",
    "status": "draft"
  }'
```

**List events:**
```bash
curl http://localhost:8000/events
```

**Filter by status:**
```bash
curl "http://localhost:8000/events?status=active&limit=10"
```

**Update an event:**
```bash
curl -X PUT http://localhost:8000/events/{event-id} \
  -H "Content-Type: application/json" \
  -d '{"status": "published"}'
```

**Delete an event:**
```bash
curl -X DELETE http://localhost:8000/events/{event-id}
```

## 🗄️ Local Development with DynamoDB Local

To test locally without AWS:

1. **Install DynamoDB Local:**
   ```bash
   docker run -p 8000:8000 amazon/dynamodb-local
   ```

2. **Configure environment:**
   ```bash
   export AWS_ENDPOINT_URL=http://localhost:8000
   export DYNAMODB_TABLE_NAME=events-local
   ```

3. **Create the table:**
   ```bash
   aws dynamodb create-table \
     --table-name events-local \
     --attribute-definitions AttributeName=eventId,AttributeType=S \
     --key-schema AttributeName=eventId,KeyType=HASH \
     --billing-mode PAY_PER_REQUEST \
     --endpoint-url http://localhost:8000
   ```

## 🚀 Deployment

This backend is designed to run on AWS Lambda. See the main [README.md](../README.md) and [DEPLOYMENT.md](../DEPLOYMENT.md) for deployment instructions.

## 🛠️ Technologies

- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation using Python type annotations
- **Boto3** - AWS SDK for Python
- **Mangum** - AWS Lambda adapter for ASGI applications
- **Python 3.11** - Runtime environment
