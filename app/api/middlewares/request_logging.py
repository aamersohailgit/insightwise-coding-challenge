import time
from typing import Callable
import uuid

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logging_config import get_logger, set_request_id, get_request_id

logger = get_logger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log incoming requests and outgoing responses with timing information."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable):
        # Generate request ID if not present
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        set_request_id(request_id)

        # Start timer
        start_time = time.time()

        # Log the request
        path = request.url.path
        query_params = dict(request.query_params)
        client_host = request.client.host if request.client else None
        client_port = request.client.port if request.client else None

        logger.info(
            f"Request started: {request.method} {path}",
            extra={
                'method': request.method,
                'path': path,
                'query_params': query_params,
                'client_host': client_host,
                'client_port': client_port,
                'headers': dict(request.headers),
            }
        )

        try:
            # Process the request and get the response
            response = await call_next(request)

            # Calculate request processing time
            process_time = time.time() - start_time
            process_time_ms = round(process_time * 1000, 2)

            # Log the response
            logger.info(
                f"Request completed: {request.method} {path}",
                extra={
                    'method': request.method,
                    'path': path,
                    'status_code': response.status_code,
                    'duration_ms': process_time_ms,
                }
            )

            # Add the request ID to the response headers
            response.headers['X-Request-ID'] = get_request_id()
            # Add timing information to headers
            response.headers['X-Process-Time'] = str(process_time_ms)

            return response

        except Exception as e:
            # Calculate request processing time
            process_time = time.time() - start_time
            process_time_ms = round(process_time * 1000, 2)

            # Log the error
            logger.error(
                f"Request failed: {request.method} {path}",
                exc_info=e,
                extra={
                    'method': request.method,
                    'path': path,
                    'error': str(e),
                    'duration_ms': process_time_ms,
                }
            )

            # Re-raise the exception
            raise

def add_middleware(app: FastAPI):
    """Add the request logging middleware to the FastAPI app."""
    app.add_middleware(RequestLoggingMiddleware)