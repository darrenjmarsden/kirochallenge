# Events API Documentation

This folder contains auto-generated API documentation created with [pdoc](https://pdoc.dev/).

## View Documentation

Open `index.html` in your browser to view the complete API documentation.

## Documentation Contents

- **main.html** - API endpoints and route handlers
- **models.html** - Pydantic data models and validation schemas
- **database.html** - DynamoDB client and database operations
- **config.html** - Application configuration and settings
- **exceptions.html** - Custom exception handlers

## Regenerate Documentation

To regenerate the documentation after code changes:

```bash
cd backend
python3 -m pip install pdoc
python3 -m pdoc main models database config exceptions -o docs
```

## Interactive API Documentation

For interactive API documentation with the ability to test endpoints, visit:

- **Swagger UI:** https://qngi811123.execute-api.us-west-2.amazonaws.com/prod/docs
- **ReDoc:** https://qngi811123.execute-api.us-west-2.amazonaws.com/prod/redoc
