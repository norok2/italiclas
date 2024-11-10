"""Stopwatch utilities for timing single runs."""

import functools
import logging
import operator
from collections.abc import Callable
from datetime import datetime
from typing import Any


# ======================================================================
def print_elapsed(
    func: Callable,
    elapsed: Any,  # noqa: ANN401
    msg: str = "Func={func_name}(), Elapsed={elapsed}",
) -> None:
    """Print clockit() elapsed time for the given function."""
    print(msg.format(func_name=func.__name__, elapsed=elapsed))  # noqa: T201


# ======================================================================
def log_elapsed(
    func: Callable,
    elapsed: Any,  # noqa: ANN401
    logger: logging.Logger,
    msg: str = "Func=%s(), Elapsed=%s",
    level: int = logging.INFO,
) -> None:
    """Log clockit() elapsed time for the given function."""
    logger.log(level, msg, func.__name__, elapsed)


# ======================================================================
def clockit(
    decorating: Callable | None = None,
    callback: Callable[[Callable, Any], None] = print_elapsed,
    timer: Callable[[], Any] = datetime.now,
    combiner: Callable[[Any, Any], Any] = operator.sub,
) -> Callable:
    """Measure the time it takes to execute the decorated callable.

    Can be used either directly (with or without parentheses)
    or with keyword arguments.

    Args:
        decorating: The callable to decorate.
        callback: The function to call to give feedback on the measured time.
            Must accept a callable as a first argument, and the result of
            `combiner()` applied to the result of two `timer()` calls.
        timer: The timestamp generation function.
        combiner: The measure generation function.
            Must accept two timestamps as per `timer()` output.

    Returns:
        The decorated callable.

    Raises:
        RuntimeWarning: When using additional positional arguments.
            The only supported positional argument is the callable to decorate.

    Examples:
        >>> @clockit(callback=print_elapsed)
        ... def fn():
        ...     return "Done"

        >>> fn()  # doctest: +ELLIPSIS
        Func=fn(), Elapsed=0:00:00.000...
        'Done'

    """

    def _decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: tuple, **kws: dict) -> Any:  # noqa: ANN401
            begin_time = timer()
            result = func(*args, **kws)
            end_time = timer()
            callback(func, combiner(end_time, begin_time))
            return result

        return wrapper

    if callable(decorating):
        return _decorator(decorating)
    if decorating is None:
        return _decorator
    err_msg = "Unsupported positional argument."
    raise RuntimeWarning(err_msg)


# ======================================================================
def clockit_log(
    logger: logging.Logger,
    level: int = logging.INFO,
) -> Callable:
    """Measure and log the time it takes to execute the decorated callable."""
    log_elapsed_by_level = functools.partial(
        log_elapsed,
        logger=logger,
        level=level,
    )
    return functools.partial(clockit, callback=log_elapsed_by_level)
