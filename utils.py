import time
import logging
from functools import wraps
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from typing import Callable, Any

logger = logging.getLogger(__name__)

def retry_database_operation(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    max_delay: float = 60.0
) -> Callable:
    """
    Decorator that implements a retry mechanism with exponential backoff for database operations.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        exponential_base: Base for exponential backoff calculation
        max_delay: Maximum delay between retries in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (SQLAlchemyError, OperationalError) as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Final retry attempt failed for {func.__name__}: {str(e)}")
                        raise
                        
                    logger.warning(
                        f"Database operation failed (attempt {attempt + 1}/{max_retries})"
                        f" for {func.__name__}: {str(e)}. Retrying in {delay:.1f} seconds..."
                    )
                    
                    time.sleep(delay)
                    delay = min(delay * exponential_base, max_delay)
            
            # This line should never be reached due to the raise in the last attempt
            return None
        return wrapper
    return decorator
