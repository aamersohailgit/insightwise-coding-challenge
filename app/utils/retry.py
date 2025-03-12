import asyncio
import random
from functools import wraps
from typing import Callable, List, Type, Optional, Any

from app.core.logging_config import get_logger

logger = get_logger(__name__)

def async_retry(
    retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    exceptions: Optional[List[Type[Exception]]] = None
):
    """
    Retry decorator for async functions that may experience transient failures.

    Args:
        retries: Number of times to retry the function
        delay: Initial delay between retries (in seconds)
        backoff_factor: Factor to increase delay with each retry
        jitter: Whether to add randomness to the delay time
        exceptions: List of exceptions that should trigger a retry
                   (defaults to general exceptions)
    """
    if exceptions is None:
        exceptions = [Exception]

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None
            current_delay = delay

            for attempt in range(retries + 1):
                try:
                    if attempt > 0:
                        logger.info(
                            f"Retry attempt {attempt}/{retries} for {func.__name__}",
                            extra={"attempt": attempt, "max_retries": retries}
                        )

                    return await func(*args, **kwargs)

                except tuple(exceptions) as e:
                    last_exception = e

                    if attempt == retries:
                        logger.warning(
                            f"All {retries} retries failed for {func.__name__}",
                            extra={"error": str(e), "function": func.__name__}
                        )
                        raise

                    # Calculate wait time with optional jitter
                    wait_time = current_delay
                    if jitter:
                        wait_time = current_delay * (0.5 + random.random())

                    logger.warning(
                        f"Operation {func.__name__} failed, retrying in {wait_time:.2f}s",
                        extra={
                            "error": str(e),
                            "attempt": attempt,
                            "wait_time": wait_time,
                            "function": func.__name__
                        }
                    )

                    # Wait before retrying
                    await asyncio.sleep(wait_time)

                    # Increase delay for next attempt
                    current_delay *= backoff_factor

        return wrapper

    return decorator