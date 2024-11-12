"""PyTest ConfTest file."""

import pandas as pd
import pytest


# ======================================================================
@pytest.fixture
def raw_df() -> pd.DataFrame:
    """Fixture to create a sample DataFrame."""
    data = {
        "Text": ["Hello World", "Ciao Mondo!", "Hallo Welt"],
        "Language": ["English", "Italian", "German"],
    }
    return pd.DataFrame(data)


# ======================================================================
@pytest.fixture
def clean_df() -> pd.DataFrame:
    """Fixture to create a sample DataFrame."""
    data = {
        "text": ["Hello World", "Ciao Mondo!", "Hallo Welt"],
        "is_italian": [False, True, False],
    }
    return pd.DataFrame(data)
