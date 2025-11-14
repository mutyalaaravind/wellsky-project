import asyncio
from functools import wraps
from typing import Callable, TypeVar, ParamSpec
import logging

from paperglass.domain.utils.exception_utils import exceptionToMap

from paperglass.log import getLogger
LOGGER = getLogger(__name__)

P = ParamSpec("P")
T = TypeVar("T")

def retry_with_backoff(max_retries: int = 3, initial_delay: float = 1.0, retry_on_empty: bool = False):
    def decorator(func: Callable[P, T]):
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs):
            delay = initial_delay
            LOGGER.debug("Initial delay: %s", delay)
            last_exception = None
            
            result = None
            for retry in range(max_retries):
                try:
                    result = await func(*args, **kwargs)
                    if result or not retry_on_empty:  # Always return a non-empty result.  Conditionally return the empty result if retry_on_empty is False
                        return result
                    
                except Exception as e:
                    last_exception = e
                    extra = {
                        "error": exceptionToMap(e)
                    }
                    LOGGER.warning(
                        f"Exception in {func.__name__} (kwargs: {kwargs}), attempt {retry + 1}/{max_retries}: {str(e)}",
                        extra=extra
                    )

                if retry < max_retries - 1:  # Don't sleep on the last iteration                    
                    LOGGER.warning(
                        f"Empty result from {func.__name__}, attempt {retry + 1}/{max_retries}  Delaying {delay} seconds"
                    )
                    await asyncio.sleep(delay)
                    if delay == 0:
                        delay = 1
                    else:
                        delay *= 2 

            # If we get here, all retries failed
            if last_exception:
                raise last_exception
            return result  # Return empty last result if all retries returned empty results

        return wrapper
    return decorator