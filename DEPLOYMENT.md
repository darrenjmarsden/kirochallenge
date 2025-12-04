# Deployment Guide

## Prerequisites

1. **AWS Credentials** - You'll need AWS access keys with permissions to create:
   - Lambda functions
   - API Gateway
   - DynamoDB tables
   - IAM roles

2. **Python 3.11+** - Required for CDK and Lambda runtime

3. **Node.js & AWS CDK CLI**:
   ```bash
   npm install -g aws-cdk
   ```

## Setup AWS Credentials

1. Copy the example environment file:
   ```bash
   cp .env.deploy.example .env.deploy
   ```

2. Edit `.env.deploy` with your AWS credentials:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key_here
   export AWS_SECRET_ACCESS_KEY=your_secret_key_here
   export AWS_REGION=us-east-1
   ```

3. Load the credentials:
   ```bash
   source .env.deploy
   ```

## Quick Deploy

Run the deployment script:

```bash
./deploy.sh
```

This will:
- Install CDK dependencies
- Bootstrap CDK in your AWS account (if needed)
- Deploy the API Gateway, Lambda function, and DynamoDB table
- Output your public API endpoint URL

## Manual Deployment

If you prefer to deploy manually:

```bash
cd infrastructure
pip install -r requirements.txt
cdk bootstrap  # Only needed once per account/region
cdk deploy
```

## Testing Your API

Once deployed, you'll receive an API Gateway URL like:
```
https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/
```

### Test Endpoints

```bash
# Health check
curl https://your-api-url/health

# Create an event
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

# List all events
curl https://your-api-url/events

# Get specific event
curl https://your-api-url/events/{eventId}

# Update event
curl -X PUT https://your-api-url/events/{eventId} \
  -H "Content-Type: application/json" \
  -d '{"capacity": 600}'

# Delete event
curl -X DELETE https://your-api-url/events/{eventId}
```

## Architecture

- **API Gateway**: Provides the public HTTPS endpoint
- **Lambda Function**: Runs the FastAPI application (serverless)
- **DynamoDB**: NoSQL database for event storage (pay-per-request)
- **Lambda Layer**: Contains Python dependencies (FastAPI, boto3, etc.)

## Cost Optimization

This serverless architecture is cost-effective:
- Lambda: Pay only for execution time (free tier: 1M requests/month)
- API Gateway: Pay per request (free tier: 1M requests/month)
- DynamoDB: Pay per request (free tier: 25GB storage, 25 read/write units)

## Cleanup

To remove all resources and avoid charges:

```bash
cd infrastructure
cdk destroy
```
