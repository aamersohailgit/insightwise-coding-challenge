# Scalable and Testable Items API

This project implements a scalable and testable REST API for managing Items, built with FastAPI, MongoEngine, and an event-driven architecture using pyee. The application follows comprehensive logging practices and has an extensive test suite with 82% code coverage.

## Architecture

The application follows a clean, layered architecture designed for scalability and reusability:

[**Architecture Diagram**](images/architecture_diagram.png)

[**Architecture Diagram with Retry Mechanism**](images/SequenceDiagram.drawio.png)

## Features

- **FastAPI Framework**: High-performance, easy-to-use framework with automatic OpenAPI documentation
- **MongoEngine ODM**: Object-Document Mapper for MongoDB with MongoMock for testing
- **Event-Driven Design**: Pub/sub system using pyee for asynchronous operations
- **Clean Architecture**: Separation of concerns with clear layer boundaries
- **Comprehensive Testing**: 82% code coverage with pytest
- **External API Integration**: Geolocation data from zippopotam.us
- **Structured Logging**: JSON-formatted logs with request tracing and performance metrics
- **Error Handling**: Consistent error responses with detailed error information
- **Retry Mechanism**: Resilient external API calls with exponential backoff

## Setup and Installation

### Prerequisites

- Python 3.12.6
- MongoDB (or use the included MongoMock for development)
- Docker and Docker Compose (optional, for containerized setup)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/aamersohailgit/insightwise-coding-challenge.git
   cd insightwise-coding-challenge
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:

   **With Docker:**
   ```bash
   docker-compose up --build
   ```

   **Without Docker:**
   ```bash
   uvicorn app.main:app --reload
   ```

5. Access the API documentation:
   ```
   http://localhost:8000/docs
   ```

### Environment Variables

The application can be configured using the following environment variables:

- `MONGODB_URL`: MongoDB connection URL (default: mongodb://localhost:27017/)
- `MONGODB_DB`: MongoDB database name (default: items_db)
- `USE_MOCK_DB`: Use in-memory database for testing/development (default: true)
- `LOG_LEVEL`: Logging level (default: INFO)
- `AUTH_TOKEN`: Authentication token for API access (default: test-token)

## Testing

The project has a comprehensive test suite with 82% code coverage. Tests are organized by application component:

- API tests
- Model tests
- Repository tests
- Service tests
- Worker tests
- Database tests

### Running Tests

Run all tests:
```bash
pytest
```

Run tests with coverage report:
```bash
pytest --cov=app --cov-report=term
```

Generate HTML coverage report:
```bash
pytest --cov=app --cov-report=html
```

## API Endpoints

The API provides the following endpoints:

- `GET /health`: Health check endpoint
- `GET /items`: Retrieve all items
- `POST /items`: Create a new item
- `GET /items/{item_id}`: Retrieve an item by ID
- `PATCH /items/{item_id}`: Update an item
- `DELETE /items/{item_id}`: Delete an item

For detailed API documentation, visit the Swagger UI at `http://localhost:8000/docs`.

## Design Decisions and Thought Process

### Layered Architecture

I implemented a clear separation of concerns with distinct layers:
- **API Layer**: FastAPI routes, request/response handling, authentication
- **Service Layer**: Business logic, validation, external API integration
- **Repository Layer**: Data access abstraction, MongoDB operations
- **Data Layer**: Database models and connections

This structure promotes:
- **Reusability**: Components can be reused across different parts of the application
- **Testability**: Each layer can be tested in isolation
- **Maintainability**: Changes in one layer don't affect others

### Structured Logging

The logging system was designed with observability in mind:
- **JSON-formatted logs**: Easy to parse and analyze
- **Request ID tracking**: Trace requests across components
- **Performance metrics**: Timing for operations
- **Log levels**: Different levels for different environments
- **Request/Response logging**: Comprehensive API monitoring

### Error Handling

A centralized error handling approach ensures consistent responses:
- **API error handlers**: Convert exceptions to appropriate HTTP responses
- **Validation errors**: Detailed feedback on invalid data
- **Retry mechanism**: Resilient external service calls

### Testing Strategy

The testing approach focuses on comprehensive coverage:
- **Unit tests**: Test isolated components
- **Integration tests**: Test component interactions
- **API tests**: Test endpoints with expected responses
- **Mock external services**: Test without dependencies
- **Error scenario testing**: Verify proper error handling

## Reusability and Extensibility

### Reusable Components

The application is built with reusability in mind:
- **Repository pattern**: Abstracts database operations
- **Service layer**: Encapsulates business logic
- **Utility functions**: Common operations like case conversion
- **Middleware**: Reusable request processing components
- **Event system**: Decoupled communication between components

### Extensibility

The architecture makes it easy to extend the application:
- **Add new endpoints**: Create new route modules
- **Add new models**: Create new schemas and repositories
- **Add new external services**: Follow the service layer pattern
- **Add new event handlers**: Subscribe to existing events
- **Add new middleware**: Plug into the request processing pipeline

### Future Improvements

Potential enhancements to further improve the application:
- **User authentication**: Add JWT-based authentication
- **Rate limiting**: Protect APIs from abuse
- **Caching layer**: Improve performance for frequent requests
- **Background tasks**: Move more operations to asynchronous processing
- **Metrics and monitoring**: Add Prometheus metrics for observability
- **Enhanced validation**: Add more sophisticated data validation rules
- **API versioning**: Support multiple API versions