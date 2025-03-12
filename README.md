# Scalable and Testable Items API

This project implements a scalable and testable REST API for managing Items, built with FastAPI, MongoEngine, and an event-driven architecture using pyee.

## Architecture

The application follows a clean, layered architecture designed for scalability and reusability:

[**Architecture Diagram**](images/architecture_diagram.png)

## Features

- **FastAPI Framework**: High-performance, easy-to-use framework with automatic OpenAPI documentation
- **MongoEngine ODM**: Object-Document Mapper for MongoDB with MongoMock for testing
- **Event-Driven Design**: Pub/sub system using pyee for asynchronous operations
- **Clean Architecture**: Separation of concerns with clear layer boundaries
- **Comprehensive Testing**: 79% code coverage with pytest
- **External API Integration**: Geolocation data from zippopotam.us

### Prerequisites

- Python 3.12.6
- Docker and Docker Compose (optional, for containerized setup)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/aamersohailgit/insightwise-coding-challenge.git
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run with Docker
   ```
   docker-compose up --build
   ```
4. Run without Docker
   ```
   uvicorn app.main:app --reload
   ```
5. Access the API Docs - [**API Docs**](images/api_docs.png)
   ```
   http://localhost:8000/docs
   ```

### API Endpoints

* Check this out - [**API Docs**](images/api_docs.png)

### Run like this
1. Set Token - [**Token**](images/set_token.png)
2. Test APIs - e.g. [**POST API**](images/post.png)
3. Same for others
4. Run test cases
   ```
   pytest
   ```
5. Run Converage - Current test coverage: 79%
   ```
   pytest --cov=app --cov-report=html
   ```

## Design Decisions
### Layered Architecture
I implemented a clear separation of concerns with distinct layers:
- API Layer: FastAPI routes, request/response handling, authentication
- Service Layer: Business logic, validation, external API integration
- Repository Layer: Data access abstraction, MongoDB operations
- Data Layer: Database models and connections

This structure promotes reusability and testability by isolating components.

### Event-Driven System
The pub/sub event system allows:
- Asynchronous processing of tasks
- Decoupling of components
- Easier extension with new event handlers
- Improved scalability by handling time-consuming operations asynchronously

### Case Conversion
A utility layer handles camelCase/snake_case conversion between API and database:

- API accepts and returns camelCase (client-friendly)
- Database stores snake_case (Python convention)
- This is handled transparently by the service layer

### Repository Pattern
The repository pattern abstracts database operations, providing:

- A clean interface to data access
- Reusable data operations
- Easier testing with mocks
- Database implementation independence