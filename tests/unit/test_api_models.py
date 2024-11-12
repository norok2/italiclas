"""Test API Models."""

import pytest
from pydantic import ValidationError

from italiclas.api.models.payloads import PredictPayload
from italiclas.api.models.responses import PingResponse, PredictResponse


# ======================================================================
@pytest.mark.parametrize(
    ("text", "expectation"),
    [
        ("ciao mondo", True),
        ("hello world", True),
        (123, ValidationError),
        (None, ValidationError),
    ],
)
def test_predictpayload(text, expectation) -> None:  # noqa: ANN001
    """Test for PredictPayload model."""
    if isinstance(expectation, type) and issubclass(expectation, Exception):
        with pytest.raises(expectation):
            PredictPayload(text=text)
    else:
        result = PredictPayload(text=text)
        assert (result.text == text) is expectation


# ======================================================================
@pytest.mark.parametrize(
    ("message", "expectation"),
    [
        ("0.0.0", True),
        ("hello world", True),
        (123, ValidationError),
        (None, ValidationError),
    ],
)
def test_pingresponse(message, expectation) -> None:  # noqa: ANN001
    """Test for PingResponse model."""
    if isinstance(expectation, type) and issubclass(expectation, Exception):
        with pytest.raises(expectation):
            PingResponse(message=message)
    else:
        result = PingResponse(message=message)
        assert (result.message == message) is expectation


# ======================================================================
@pytest.mark.parametrize(
    ("is_italian", "expectation"),
    [
        (True, True),
        (False, True),
        (123, ValidationError),
        (None, ValidationError),
    ],
)
def test_predictresponse(is_italian, expectation) -> None:  # noqa: ANN001
    """Test for PredictResponse model."""
    if isinstance(expectation, type) and issubclass(expectation, Exception):
        with pytest.raises(expectation):
            PredictResponse(is_italian=is_italian)
    else:
        result = PredictResponse(is_italian=is_italian)
        assert (result.is_italian == is_italian) is expectation
