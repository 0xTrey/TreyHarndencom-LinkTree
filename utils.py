import time
import random
import logging
from functools import wraps
from typing import Callable, Any, Type, Union, Tuple
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError, TimeoutError

logger = logging.getLogger(__name__)

def retry_database_operation(
    max_retries: int = 5,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    max_delay: float = 30.0,
    jitter: float = 0.1,
    exceptions: Tuple[Type[Exception], ...] = (
        SQLAlchemyError,
        OperationalError,
        IntegrityError,
        TimeoutError,
        Exception  # Catch all database-related exceptions
    )
) -> Callable:
    """
    Decorator that implements a retry mechanism with exponential backoff and jitter for database operations.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        exponential_base: Base for exponential backoff calculation
        max_delay: Maximum delay between retries in seconds
        jitter: Random jitter factor (0-1) to add to delay
        exceptions: Tuple of exception types to catch and retry
    
    Returns:
        Callable: Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries - 1:
                        logger.error(
                            f"Final retry attempt ({max_retries}/{max_retries}) failed "
                            f"for {func.__name__}: {str(e)}"
                        )
                        raise last_exception
                    
                    # Calculate delay with jitter
                    jitter_amount = random.uniform(-jitter * delay, jitter * delay)
                    actual_delay = min(delay + jitter_amount, max_delay)
                    
                    logger.warning(
                        f"Database operation failed (attempt {attempt + 1}/{max_retries}) "
                        f"for {func.__name__}: {str(e)}. "
                        f"Retrying in {actual_delay:.2f} seconds..."
                    )
                    
                    time.sleep(actual_delay)
                    delay = min(delay * exponential_base, max_delay)
            
            # This should never be reached due to the raise in the final attempt
            return None
        return wrapper
    return decorator

def is_retriable_error(exception: Exception) -> bool:
    """
    Determine if an exception should trigger a retry attempt.
    
    Args:
        exception: The exception to check
        
    Returns:
        bool: True if the error should trigger a retry, False otherwise
    """
    # Common retriable error messages
    retriable_messages = [
        "connection timed out",
        "deadlock detected",
        "connection reset",
        "connection refused",
        "operational error",
        "lost connection",
        "too many connections"
    ]
    
    error_message = str(exception).lower()
    return any(msg in error_message for msg in retriable_messages)
