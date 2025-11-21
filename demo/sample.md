# Getting Started with API Development

Welcome to the **Ultimate API Development Guide**! This tutorial will walk you through building a modern REST API from scratch.

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Project Setup](#project-setup)
4. [Building the API](#building-the-api)
5. [Testing](#testing)
6. [Deployment](#deployment)

## Introduction

Modern web applications rely on **robust APIs** to deliver data efficiently. In this guide, we'll build a production-ready API with:

- ✅ RESTful design principles
- ✅ Authentication & authorization
- ✅ Rate limiting
- ✅ Comprehensive error handling
- ✅ API documentation
- ✅ Unit & integration tests

## Prerequisites

Before starting, ensure you have:

- Python 3.10 or higher
- Docker and Docker Compose
- PostgreSQL 14+
- Basic understanding of HTTP and REST

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head
```

## Project Setup

### Directory Structure

```
api-project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
├── tests/
├── alembic/
├── docker-compose.yml
└── requirements.txt
```

### Configuration

Create a `.env` file with your configuration:

```env
DATABASE_URL=postgresql://user:pass@localhost/dbname
SECRET_KEY=your-secret-key-here
DEBUG=False
```

## Building the API

### Creating Your First Endpoint

Here's a simple endpoint to get started:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="My API", version="1.0.0")

class Item(BaseModel):
    name: str
    description: str
    price: float

@app.get("/")
async def root():
    return {"message": "Welcome to the API"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id, "name": "Sample Item"}

@app.post("/items/")
async def create_item(item: Item):
    return {"item": item, "status": "created"}
```

### Adding Authentication

Implement JWT-based authentication:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
```

## Testing

Write comprehensive tests:

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the API"}

def test_create_item():
    response = client.post(
        "/items/",
        json={"name": "Test", "description": "Test item", "price": 9.99}
    )
    assert response.status_code == 200
```

## Deployment

### Docker Deployment

Use Docker for consistent deployments:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Running with Docker Compose

```bash
docker-compose up -d
```

## Best Practices

> **Important**: Always validate input data and sanitize user-generated content.

1. **Version your API** - Use URL versioning (`/v1/`, `/v2/`)
2. **Document everything** - Use OpenAPI/Swagger
3. **Rate limit** - Protect against abuse
4. **Monitor** - Track errors and performance
5. **Test thoroughly** - Aim for >80% coverage

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [REST API Best Practices](https://restfulapi.net/)
- [API Security Checklist](https://github.com/shieldfy/API-Security-Checklist)

---

**Happy coding!** 🚀

For questions or issues, please open an issue on [GitHub](https://github.com/example/api-project).

