"""Test ETL Clean Data."""

from pathlib import Path

import pandas as pd
import pytest

from italiclas.etl import clean_data


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


# ======================================================================
@pytest.mark.parametrize(
    ("file_exists", "force"),
    [(True, True), (True, False), (False, True), (False, False)],
)
def test_clean_data_processor(
    force,  # noqa: ANN001
    file_exists,  # noqa: ANN001
    raw_df,  # noqa: ANN001
    clean_df,  # noqa: ANN001
    mocker,  # noqa: ANN001
) -> None:
    """Tests `clean_data.processor()` on file_exists/force combinations."""
    raw_filename = "some_raw"
    clean_filename = "some_clean"
    dirpath = Path("some_dir/")
    mocker.patch.object(Path, "is_file", return_value=file_exists)
    if force or not file_exists:
        mocker.patch("pandas.read_csv", return_value=raw_df.copy())
    else:
        mocker.patch("pandas.read_csv", return_value=clean_df.copy())
    mocker.patch.object(pd.DataFrame, "to_csv")
    result = clean_data.processor(
        raw_filename,
        clean_filename,
        dirpath,
        force=force,
    )
    assert result == dirpath / clean_filename


# ======================================================================
def test_clean_data_processor_raw_data_no_language(raw_df, mocker) -> None:  # noqa: ANN001
    """Tests `clean_data_processor()` on invalid data: no 'language' column."""
    invalid_raw_df = raw_df.copy()
    invalid_raw_df["Lang"] = invalid_raw_df["Language"]
    invalid_raw_df = invalid_raw_df.drop(["Language"], axis=1)
    mocker.patch("pandas.read_csv", return_value=invalid_raw_df.copy())
    with pytest.raises(ValueError, match="Invalid raw data input"):
        clean_data.processor(force=True)


# ======================================================================
def test_clean_data_processor_raw_data_no_text(raw_df, mocker) -> None:  # noqa: ANN001
    """Tests `clean_data_processor()` on invalid data: no 'text' column."""
    invalid_raw_df = raw_df.copy()
    invalid_raw_df["String"] = invalid_raw_df["Text"]
    invalid_raw_df = invalid_raw_df.drop(["Text"], axis=1)
    mocker.patch("pandas.read_csv", return_value=invalid_raw_df.copy())
    with pytest.raises(ValueError, match="Invalid raw data input"):
        clean_data.processor(force=True)


# ======================================================================
@pytest.mark.parametrize(
    ("data", "check_result"),
    [
        # valid
        (
            pd.DataFrame({"text": ["io", "tu"], "is_italian": [True, True]}),
            True,
        ),
        # missing column
        (pd.DataFrame({"text": ["io", "tu"]}), False),
        # wrong data type
        (pd.DataFrame({"text": ["io", "tu"], "is_italian": [1, 1]}), False),
        # empty
        (pd.DataFrame(), False),
    ],
)
def test_is_valid(data, check_result) -> None:  # noqa: ANN001
    """Test `is_valid()`."""
    assert clean_data.is_valid(data) is check_result
