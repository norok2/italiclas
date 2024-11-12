"""Test ETL Raw Data."""

from http import HTTPStatus
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest

from italiclas.etl import raw_data


# ======================================================================
@pytest.mark.parametrize(
    ("file_exists", "force"),
    [(True, True), (True, False), (False, True), (False, False)],
)
def test_raw_data_fetcher(force, file_exists, mocker) -> None:  # noqa: ANN001
    """Tests `raw_data.fetcher()` on file_exists/force combinations."""
    raw_filename = "some_filename"
    dirpath = Path("some_dir/")
    mock_zip = MagicMock()
    mock_response = MagicMock()
    mock_response.status_code = HTTPStatus.OK
    mocker.patch.object(Path, "is_file", return_value=file_exists)
    mock_zipfile = mocker.patch("zipfile.ZipFile", return_value=mock_zip)
    mock_move = mocker.patch("shutil.move")
    mock_get = mocker.patch("requests.get", return_value=mock_response)
    result = raw_data.fetcher(raw_filename, dirpath, force=force)
    assert mock_get.called is (force or not file_exists)
    if mock_get.called:
        assert mock_zipfile.called is True
        assert mock_move.called is True
    assert result == dirpath / raw_filename


# ======================================================================
@pytest.mark.parametrize(
    "status_code",
    [HTTPStatus.NOT_FOUND, HTTPStatus.INTERNAL_SERVER_ERROR],
)
def test_raw_data_fetcher_error(status_code, mocker) -> None:  # noqa: ANN001
    """Tests `raw_data.fetcher()` with error scenarios."""
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mocker.patch("requests.get", return_value=mock_response)
    mocker.patch.object(Path, "is_file", return_value=False)
    result = raw_data.fetcher()
    assert result is None


# ======================================================================
@pytest.mark.parametrize(
    ("data", "check_result"),
    [
        # valid
        (
            pd.DataFrame(
                {
                    "text": ["hello", "world"],
                    "language": ["English", "English"],
                },
            ),
            True,
        ),
        # missing column
        (pd.DataFrame({"text": ["hello", "world"]}), False),
        # wrong data type
        (
            pd.DataFrame({"text": ["hello", "world"], "language": [1, 1]}),
            False,
        ),
        # empty
        (pd.DataFrame(), False),
    ],
)
def test_is_valid(data, check_result) -> None:  # noqa: ANN001
    """Test `clean_data.is_valid()`."""
    assert raw_data.is_valid(data) is check_result
