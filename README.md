# Operations Monitoring System

This is a FastAPI-based backend for an Operations Monitoring System. It provides a robust API for user management, role-based access control, dynamic form creation, and data entry operations.

## Features

- User authentication and authorization
- Role-based access control
- Dynamic form creation and management
- Data entry with approval workflow
- RESTful API endpoints for CRUD operations

## Technologies Used

- FastAPI
- SQLAlchemy
- Pydantic
- Docker
- PostgreSQL

## Getting Started

### Prerequisites

- Docker and Docker Compose
- Git

### Installation and Setup

1. Clone the repository:
   ```
   git clone https://github.com/arpitptl/operations-monitoring-system.git
   cd operations-monitoring-system
   ```

2. Build and start the Docker containers:
   ```
   docker-compose build
   docker-compose up -d
   ```

3. The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access the interactive API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Main Endpoints

- `/api/users`: User management
- `/api/roles`: Role management
- `/api/forms`: Dynamic form management
- `/api/data`: Data entry operations

## Authentication

The API uses JWT for authentication. To obtain a token:

1. Send a POST request to `/api/token` with email and password.
2. Use the returned token in the Authorization header for subsequent requests:
   ```
   Authorization: Bearer <your_token_here>
   ```

## Development

To run the project in development mode:

1. Create a virtual environment and activate it
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `uvicorn src.main:app --reload`


## Postman Collection

You can find the Postman collection for this project [here](./Operations-monitoring-system.postman_collection.json).
