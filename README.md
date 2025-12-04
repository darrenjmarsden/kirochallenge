# Events API - Serverless FastAPI Application

A production-ready serverless REST API for managing events, built with FastAPI and deployed on AWS using Lambda, API Gateway, and DynamoDB.

## 🚀 Live API

**Public Endpoint:** https://qngi811123.execute-api.us-west-2.amazonaws.com/prod/

**API Documentation:** 
- Swagger UI: https://qngi811123.execute-api.us-west-2.amazonaws.com/prod/docs
- ReDoc: https://qngi811123.execute-api.us-west-2.amazonaws.com/prod/redoc

## 📋 Features

- **RESTful API** for event management (CRUD operations)
- **Serverless architecture** using AWS Lambda + API Gateway
- **NoSQL database** with DynamoDB (pay-per-request)
- **Status filtering** for events (draft, published, active, cancelled, completed)
- **Input validation** with Pydantic models
- **CORS enabled** for frontend integration
- **Comprehensive error handling** and logging
- **Infrastructure as Code** with AWS CDK

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│   Client    │─────▶│ API Gateway  │─────▶│   Lambda    │─────▶│  DynamoDB    │
│  (Browser)  │      │   (HTTPS)    │      │  (FastAPI)  │      │   (NoSQL)    │
└─────────────┘      └──────────────┘      └─────────────┘      └──────────────┘
```

## 📁 Project Structure

```
.
├── backend/                 # FastAPI application
│   ├── main.py             # API endpoints
│   ├── models.py           # Pydantic models
│   ├── database.py         # DynamoDB client
│   ├── config.py           # Configuration
│   ├── exceptions.py       # Custom exceptions
│   ├── lambda_handler.py   # Lambda entry point
│   └── requirements.txt    # Python dependencies
├── infrastructure/          # AWS CDK infrastructure
│   ├── app.py              # CDK app entry point
│   ├── stacks/
│   │   └── backend_stack.py # Infrastructure definition
│   └── requirements.txt    # CDK dependencies
├── deploy.sh               # Deployment script
└── DEPLOYMENT.md           # Detailed deployment guide
```

## 🔧 Setup & Deployment

### Prerequisites

- Python 3.11+
- Node.js (for AWS CDK)
- Docker (for building Lambda layers)
- AWS credentials with appropriate permissions

### Quick Deploy

1. **Set up AWS credentials:**
   ```bash
   cp .env.deploy.example .env.deploy
   # Edit .env.deploy with your AWS credentials
   source .env.deploy
   ```

2. **Deploy to AWS:**
   ```bash
   ./deploy.sh
   ```

3. **Get your API URL from the output**

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## 📖 API Usage

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/health` | Health check |
| POST | `/events` | Create a new event |
| GET | `/events` | List all events |
| GET | `/events?status=active` | Filter events by status |
| GET | `/events/{id}` | Get specific event |
| PUT | `/events/{id}` | Update an event |
| DELETE | `/events/{id}` | Delete an event |

### Example Requests

**Create an event:**
```bash
curl -X POST https://your-api-url/events \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tech Conference 2025",
    "description": "Annual technology conference",
    "date": "2025-06-15T09:00:00Z",
    "location": "San Francisco, CA",
    "capacity": 500,
    "organizer": "Tech Corp",
    "status": "published"
  }'
```

**List all events:**
```bash
curl https://your-api-url/events
```

**Filter by status:**
```bash
curl "https://your-api-url/events?status=active"
```

**Update an event:**
```bash
curl -X PUT https://your-api-url/events/{event-id} \
  -H "Content-Type: application/json" \
  -d '{"capacity": 600, "status": "active"}'
```

**Delete an event:**
```bash
curl -X DELETE https://your-api-url/events/{event-id}
```

## 🔍 Event Model

```json
{
  "eventId": "uuid",
  "title": "string (1-200 chars)",
  "description": "string (max 2000 chars)",
  "date": "ISO 8601 datetime",
  "location": "string (1-500 chars)",
  "capacity": "integer (1-100000)",
  "organizer": "string (1-200 chars)",
  "status": "draft | published | active | cancelled | completed",
  "createdAt": "ISO 8601 datetime",
  "updatedAt": "ISO 8601 datetime"
}
```

## 🧪 Local Development

### Run locally with DynamoDB Local:

```bash
cd backend
pip install -r requirements.txt

# Set up local DynamoDB
export AWS_ENDPOINT_URL=http://localhost:8000
export DYNAMODB_TABLE_NAME=events-local

# Run the API
uvicorn main:app --reload
```

Visit http://localhost:8000/docs for interactive API documentation.

## 💰 Cost Optimization

This serverless architecture is highly cost-effective:

- **Lambda:** Pay only for execution time
  - Free tier: 1M requests/month
- **API Gateway:** Pay per request
  - Free tier: 1M requests/month  
- **DynamoDB:** Pay per request
  - Free tier: 25GB storage, 25 read/write units

**Estimated cost for low traffic:** < $1/month

## 🧹 Cleanup

To remove all AWS resources:

```bash
cd infrastructure
source ../.env.deploy
npx aws-cdk destroy
```

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT.md) - Detailed deployment instructions
- [Backend API Docs](backend/docs/) - Generated API documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/) - FastAPI framework
- [AWS CDK Docs](https://docs.aws.amazon.com/cdk/) - Infrastructure as Code

## 🛠️ Technologies

- **Backend:** FastAPI, Pydantic, Boto3, Mangum
- **Infrastructure:** AWS CDK (Python)
- **AWS Services:** Lambda, API Gateway, DynamoDB
- **Runtime:** Python 3.11

## 📝 License

MIT
