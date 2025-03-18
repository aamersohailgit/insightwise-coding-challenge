import json
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.case_converter import camel_to_snake_dict, snake_to_camel_dict
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)

class CaseConverterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Convert request body from camelCase to snake_case
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                request_body = await request.json()
                # Store the original request body
                setattr(request, "body_json", request_body)
                # Convert to snake_case
                snake_case_body = camel_to_snake_dict(request_body)
                # Override the request's body method to return snake_case
                async def get_json():
                    return snake_case_body
                setattr(request, "json", get_json)
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Not JSON or empty body, skip conversion
                pass

        # Process the request and get the response
        response = await call_next(request)

        # For non-streaming responses with JSON content
        if (response.headers.get("content-type") == "application/json" and
            hasattr(response, "body")):
            try:
                # Get the response body
                response_body = json.loads(response.body.decode("utf-8"))
                # Convert from snake_case to camelCase
                camel_case_body = snake_to_camel_dict(response_body)
                # Replace the response body
                response.body = json.dumps(camel_case_body).encode("utf-8")
                # Update content length
                response.headers["content-length"] = str(len(response.body))
            except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
                # Not JSON or invalid, skip conversion
                pass

        return response

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Log the request
        logger.info(f"Request: {request.method} {request.url.path}")

        # Process the request
        response = await call_next(request)

        # Log the response
        logger.info(f"Response: {request.method} {request.url.path} - Status: {response.status_code}")

        return response

def setup_middlewares(app):
    app.add_middleware(CaseConverterMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
