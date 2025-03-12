import logging
from functools import wraps
import httpx
import json
import traceback

from app.core.events import event_emitter
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class ApiError(Exception):
    """Custom exception for API-related errors."""

    def __init__(self, message, status_code=None, details=None, original_exception=None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        self.original_exception = original_exception
        super().__init__(message)

async def log_request_response(request, response=None, error=None):
    """Log API request and response details."""
    context = {
        "request": {
            "method": request.method,
            "url": str(request.url),
            "headers": {k: v for k, v in request.headers.items() if k.lower() not in ['authorization']},
        }
    }

    if response:
        try:
            response_body = response.text
            if len(response_body) > 1000:  # Truncate large responses
                response_body = response_body[:1000] + "... [truncated]"

            context["response"] = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response_body
            }
        except Exception as e:
            context["response"] = {
                "status_code": response.status_code if response else None,
                "error_parsing_body": str(e)
            }

    if error:
        context["error"] = {
            "type": type(error).__name__,
            "message": str(error),
            "traceback": traceback.format_exc()
        }

    log_method = logger.error if error or (response and response.status_code >= 400) else logger.debug

    log_method(
        f"External API {'error' if error else 'call'}: {request.method} {request.url}",
        extra={"context": context}
    )

def handle_api_errors(operation_name):
    """
    Decorator to handle API errors consistently.

    Args:
        operation_name: Name of the operation being performed (for logging)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except httpx.HTTPStatusError as e:
                await log_request_response(e.request, e.response, e)

                # Extract relevant information
                status_code = e.response.status_code
                response_body = None
                try:
                    response_body = e.response.json()
                except:
                    response_body = e.response.text

                # Emit event
                event_name = f"api.{operation_name}.error"
                event_emitter.emit(event_name, status_code=status_code, error=str(e))

                # Raise custom exception
                raise ApiError(
                    message=f"External API error: {e.response.status_code}",
                    status_code=status_code,
                    details={"body": response_body},
                    original_exception=e
                )

            except httpx.RequestError as e:
                await log_request_response(e.request, error=e)

                # Emit event for connection errors
                event_name = f"api.{operation_name}.connection_error"
                event_emitter.emit(event_name, error=str(e))

                # Raise custom exception
                raise ApiError(
                    message=f"API request failed: {str(e)}",
                    details={"error_type": "connection_error"},
                    original_exception=e
                )

            except Exception as e:
                logger.exception(f"Unexpected error during {operation_name}")

                # Emit event for unexpected errors
                event_name = f"api.{operation_name}.unexpected_error"
                event_emitter.emit(event_name, error=str(e))

                # Re-raise as custom exception
                raise ApiError(
                    message=f"Unexpected error during {operation_name}: {str(e)}",
                    details={"error_type": "unexpected"},
                    original_exception=e
                )

        return wrapper
    return decorator