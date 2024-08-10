import asyncio
import functools
import logging
import os
from datetime import datetime
from contextlib import redirect_stdout
import io

log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)

current_date = datetime.now().strftime('%Y-%m-%d')
log_filename = os.path.join(log_dir, f'{current_date}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def log_function(func):
    """
    Decorator that logs the call and return value of the decorated function.
    Also logs any exceptions raised by the function and captures print statements.

    Args:
        func (Callable): The function to be decorated.

    Returns:
        Callable: The wrapped function with logging.
    """

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        stream = io.StringIO()
        try:
            logger.info(f"Function '{func.__name__}' called with args: {args} and kwargs: {kwargs}")
            with redirect_stdout(stream):
                result = await func(*args, **kwargs)

            output = stream.getvalue()
            if output:
                logger.info(f"Print output from '{func.__name__}':\n{output}")
            if result is None:
                logger.info(f"Function '{func.__name__}' completed without returning a value")
            else:
                logger.info(f"Function '{func.__name__}' returned {result}")
            return result
        except Exception as e:
            output = stream.getvalue()
            if output:
                logger.info(f"Print output from '{func.__name__}':\n{output}")
            logger.exception(f"Function '{func.__name__}' raised an exception: {e}")
            raise

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        stream = io.StringIO()
        try:
            logger.info(f"Function '{func.__name__}' called with args: {args} and kwargs: {kwargs}")
            with redirect_stdout(stream):
                result = func(*args, **kwargs)

            output = stream.getvalue()
            if output:
                logger.info(f"Print output from '{func.__name__}':\n{output}")
            if result is None:
                logger.info(f"Function '{func.__name__}' completed without returning a value")
            else:
                logger.info(f"Function '{func.__name__}' returned {result}")
            return result
        except Exception as e:
            output = stream.getvalue()
            if output:
                logger.info(f"Print output from '{func.__name__}':\n{output}")
            logger.exception(f"Function '{func.__name__}' raised an exception: {e}")
            raise

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
