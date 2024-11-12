"""Test Stopwatch Utils."""

import logging
import time
from datetime import timedelta
from unittest.mock import MagicMock

import pytest

from italiclas.utils.stopwatch import clockit, clockit_log, print_elapsed


# ======================================================================
class MockTimer:
    """Mock timer function."""

    def __init__(self) -> None:  # noqa: D107
        self.time = 0

    def __call__(self) -> int:  # noqa: D102
        self.time += 1
        return self.time


# ======================================================================
def test_clockit_as_decorator() -> None:
    """Tests clockit used as a decorator with print_elapsed callback."""

    @clockit(callback=print_elapsed)
    def slow_func() -> str:
        time.sleep(0.1)
        return "Done"

    result = slow_func()

    # Assertions
    assert result == "Done"


# ======================================================================
def test_clockit_with_custom_callback() -> None:
    """Tests clockit with a custom callback function."""

    def custom_callback(func, elapsed) -> None:  # noqa: ANN001
        # Mock callback to verify arguments
        assert func.__name__ == "fast_function"
        assert isinstance(elapsed, timedelta)

    @clockit(callback=custom_callback)
    def fast_function() -> str:
        return "Done"

    fast_function()


# ======================================================================
def test_clockit_with_custom_timer() -> None:
    """Tests clockit with a custom timer function."""
    mock_timer = MockTimer()

    @clockit(timer=mock_timer)
    def any_function() -> str:
        return "Done"

    any_function()
    assert mock_timer.time == 2  # noqa: PLR2004


# ======================================================================
def test_clockit_with_custom_combiner() -> None:
    """Tests clockit with a custom combiner function."""
    mock_timer = MockTimer()

    def custom_combiner(end: float, start: float) -> float:
        assert (end, start) == (2, 1)
        return 2 * (end - start)

    @clockit(timer=mock_timer, combiner=custom_combiner)
    def any_function() -> str:
        return "Done"

    any_function()


# ======================================================================
def test_clockit_as_function() -> None:
    """Tests clockit used as a function with keyword arguments."""

    def slow_func() -> str:
        time.sleep(0.1)
        return "Done"

    decorated_function = clockit(callback=print_elapsed)(slow_func)
    result = decorated_function()
    assert result == "Done"


# ======================================================================
def test_clockit_positional_argument_error() -> None:
    """Tests clockit with unsupported positional argument."""
    with pytest.raises(
        RuntimeWarning,
        match="Unsupported positional argument.",
    ):

        @clockit("invalid_argument")  # type: ignore[arg-type]
        def any_function() -> None:
            pass


# ======================================================================
@pytest.fixture
def mock_logger() -> MagicMock:
    """Fixture to create a mock logger."""
    return MagicMock()


# ======================================================================
def test_clockit_log(mock_logger) -> None:  # noqa: ANN001
    """Tests clockit_log decorator."""

    @clockit_log(logger=mock_logger)
    def slow_func() -> str:
        time.sleep(0.1)
        return "Done"

    result = slow_func()
    assert result == "Done"
    assert mock_logger.log.call_count == 1
    expected_args, expected_kwargs = mock_logger.log.call_args
    assert expected_args[0] == logging.INFO  # Default level
    assert expected_args[1] == "Func=%s(), Elapsed=%s"  # Log message
    assert expected_args[2] == "slow_func"  # Func name
    assert isinstance(expected_args[3], timedelta)  # Time elapsed


# ======================================================================
def test_clockit_log_custom_level(mock_logger) -> None:  # noqa: ANN001
    """Tests clockit_log with custom log level."""

    @clockit_log(logger=mock_logger, level=logging.DEBUG)
    def slow_func() -> str:
        time.sleep(0.1)
        return "Done"

    result = slow_func()
    assert result == "Done"
    assert mock_logger.log.call_count == 1
    expected_args, expected_kwargs = mock_logger.log.call_args
    assert expected_args[0] == logging.DEBUG  # Default level
    assert expected_args[1] == "Func=%s(), Elapsed=%s"  # Log message
    assert expected_args[2] == "slow_func"  # Func name
    assert isinstance(expected_args[3], timedelta)  # Time elapsed
