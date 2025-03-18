# InsightWise API Application

This directory contains the main application code for the InsightWise API.

## Directory Structure

- `auth/`: Authentication module (user management, tokens)
- `core/`: Core application components (logging, events)
- `db/`: Database connection and base repository
- `features/`: Feature modules organized by domain
  - `items/`: Item management feature
  - `geo/`: Geocoding feature
- `utils/`: Utility functions and helpers
- `config.py`: Application configuration
- `errors.py`: Error handling
- `middleware.py`: HTTP middleware
- `main.py`: Application entry point

## Key Components

### Features

Each feature is organized as a self-contained module with:
- `models.py`: Database models
- `schemas.py`: Request/response data schemas
- `service.py`: Business logic
- `routes.py`: API endpoints

### Middleware

The application uses middleware for:
- Case conversion (camelCase ↔ snake_case)
- Request logging
- Authentication

### Error Handling

Centralized error handling with:
- Custom exception classes
- Global exception handlers
- Consistent error responses

### Event System

The pub/sub event system in the core module enables:
- Decoupled communication between components
- Asynchronous task handling
- Background processing