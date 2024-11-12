#!/usr/bin/env python3
"""ETL Fetch Raw Data."""

import argparse
import logging
import shutil
import tempfile
import zipfile
from http import HTTPStatus
from pathlib import Path

import pandas as pd
import requests

from italiclas.config import cfg
from italiclas.logger import logger
from italiclas.utils import misc, stopwatch


# ======================================================================
def is_valid(df: pd.DataFrame) -> bool:
    """Check if data frame is valid raw data.

    Args:
        df: The input data frame.

    Returns:
        True if the data frame is valid, False otherwise.

    """
    columns = ("text", "language")
    return all(col in df.columns for col in columns) and all(
        pd.api.types.is_string_dtype(df[col]) for col in columns
    )


# ======================================================================
@stopwatch.clockit_log(logger, logging.INFO)
def fetcher(  # noqa: PLR0913
    raw_filename: str = cfg.raw_filename,
    dirpath: Path = cfg.data_dir,
    *,
    source: str = cfg.raw_data_source,
    source_filename: str = cfg.raw_data_source_filename,
    timeout: int = 180,
    chunk_size: int = 4096,
    force: bool = False,
) -> Path | None:
    """Fetch raw data.

    Expects the source to point to a ZIP file containing the name specified
    in the source filename.

    Args:
        raw_filename: The output raw data filename.
        dirpath: The directory where to store the data.
        source: The raw data source URL.
        source_filename: The raw data source filename inside the ZIP file.
            Defaults to cfg.raw_data_source_filename.
        timeout: The request timeout.
            Defaults to 180.
        chunk_size: The chunk size for fetching data from the request.
            Defaults to 4096.
        force: Force new computation.
            Defaults to False.

    Returns:
        The path to the raw data file.

    Examples:
        >>> fetch_raw_data()  # doctest: +SKIP
        PosixPath('artifacts/data/raw_data.csv')

    """
    raw_filepath = dirpath / raw_filename
    if force or not raw_filepath.is_file():
        response = requests.get(source, stream=True, timeout=timeout)
        if response.status_code == HTTPStatus.OK:  # 200
            logger.info("[ETL] Fetching raw data")
            with tempfile.NamedTemporaryFile() as temp_file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:  # filter out keep-alive new chunks
                        temp_file.write(chunk)
                temp_file.flush()
                temp_file.seek(0)

                with zipfile.ZipFile(temp_file, "r") as zip_ref:
                    zip_ref.extract(source_filename, dirpath)
            logger.info("[ETL] Save raw data to '%s'", raw_filepath)
            shutil.move(dirpath / source_filename, raw_filepath)
        else:
            logger.error("[ETL] Could not get raw data")
            raw_filepath = None
    else:
        logger.info("[ETL] Raw data already present in '%s'", raw_filepath)
    return raw_filepath


# ======================================================================
def _more_args(arg_parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Handle more command-line application arguments."""
    arg_parser.add_argument(
        "-o",
        "--raw_filename",
        metavar="OUT_FILE",
        type=str,
        help="output filename [%(default)s]",
        default=cfg.raw_filename,
    )
    arg_parser.add_argument(
        "-d",
        "--dirpath",
        metavar="PATH",
        type=str,
        help="output data path [%(default)s]",
        default=cfg.data_dir,
    )
    arg_parser.add_argument(
        "-s",
        "--source",
        metavar="URL",
        type=str,
        help="data source path [%(default)s]",
        default=cfg.raw_data_source,
    )
    arg_parser.add_argument(
        "-n",
        "--source_filename",
        metavar="URL",
        type=str,
        help="data source filename [%(default)s]",
        default=cfg.raw_data_source_filename,
    )
    arg_parser.add_argument(
        "-t",
        "--timeout",
        metavar="SEC",
        type=str,
        help="fetch connection timeout in seconds [%(default)s]",
        default=180,
    )
    arg_parser.add_argument(
        "-b",
        "--chunk_size",
        metavar="BYTES",
        type=str,
        help="fetch chunk size in bytes [%(default)s]",
        default=4096,
    )
    return arg_parser


# ======================================================================
@stopwatch.clockit_log(logger, logging.DEBUG)
def main() -> None:
    """Execute main script."""
    # : init args and add common parameters
    arg_parser = misc.common_args(description=__doc__)
    # : add script parameters
    arg_parser = _more_args(arg_parser)
    args = arg_parser.parse_args()

    misc.cli_logging(args, __doc__.strip())

    to_skip = {"log", "verbose", "quiet"}
    kws = {
        k: v
        for k, v in vars(args).items()
        if k not in to_skip and v is not None
    }
    fetcher(**kws)


# ======================================================================
if __name__ == "__main__":
    main()
