#!/usr/bin/env python3
"""ETL Clean Data."""

import argparse
import logging
from pathlib import Path

import pandas as pd

from italiclas.config import cfg
from italiclas.etl import raw_data
from italiclas.logger import logger
from italiclas.utils import misc, stopwatch


# ======================================================================
def is_valid(df: pd.DataFrame) -> bool:
    """Check if data frame is valid clean data.

    Args:
        df: The input data frame.

    Returns:
        True if the data frame is valid, False otherwise.

    """
    columns = (
        ("text", pd.api.types.is_string_dtype),
        ("is_italian", pd.api.types.is_bool_dtype),
    )
    return all(
        col in df.columns and type_checker(df[col])
        for col, type_checker in columns
    )


# ======================================================================
@stopwatch.clockit_log(logger, logging.INFO)
def processor(
    raw_filename: str = cfg.raw_filename,
    clean_filename: str = cfg.clean_filename,
    dirpath: Path = cfg.data_dir,
    *,
    force: bool = False,
) -> Path | None:
    """Clean data by preprocessing the raw data.

    The input raw data is a CSV file with columns: 'Text' and 'Language'.

     - 'Text' contain free-form non-cleaned text.
     - 'Language' contain the main language in English

    Args:
        raw_filename: The input raw data filename.
            It must exists in 'dirpath'.
        clean_filename: The output clean data filename.
            It will be created in 'dirpath'.
        dirpath: The directory where to store the data.
        force: Force new computation.
            Defaults to False.

    Returns:
        The path to the clean data file.

    Raises:
        ValueError: if the content of the raw data cannot be processed
    Examples:
        >>> data_cleaner()  # doctest: +SKIP
        PosixPath('artifacts/data/clean_data.csv')

    """
    raw_filepath = dirpath / raw_filename
    clean_filepath = dirpath / clean_filename
    if force or not clean_filepath.is_file():
        logger.info("[ETL] Cleaning data '%s'", raw_filepath)
        data = pd.read_csv(raw_filepath).rename(columns=str.lower)
        if raw_data.is_valid(data):
            data["is_italian"] = data["language"] == "Italian"
            data = data[["text", "is_italian"]]
            logger.info(data.columns)
            data.to_csv(clean_filepath, index=False)
            logger.info("[ETL] Clean data stored to '%s'", clean_filepath)
        else:
            msg = (
                "Invalid raw data input: expecting columns "
                "['text', 'language'] (case ignored) of string data type."
            )
            raise ValueError(msg)
    else:
        logger.info("[ETL] Load clean data from '%s'", clean_filepath)
        data = pd.read_csv(clean_filepath)
    # : inspect clean dataset
    num_total = data["is_italian"].count()
    num_italian = data["is_italian"].sum()
    logger.info(
        "Total: %d; Italian: %d (%.2f%%)",
        num_total,
        num_italian,
        100 * num_italian / num_total,
    )
    return clean_filepath


# ======================================================================
def more_args(arg_parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Handle more command-line application arguments."""
    arg_parser.add_argument(
        "-i",
        "--raw_filename",
        metavar="IN_FILE",
        type=str,
        help="input file name [%(default)s]",
        default=cfg.raw_filename,
    )
    arg_parser.add_argument(
        "-o",
        "--clean_filename",
        metavar="OUT_FILE",
        type=str,
        help="output file name [%(default)s]",
        default=cfg.clean_filename,
    )
    arg_parser.add_argument(
        "-d",
        "--dirpath",
        metavar="PATH",
        type=str,
        help="data path [%(default)s]",
        default=cfg.data_dir,
    )
    return arg_parser


# ======================================================================
@stopwatch.clockit_log(logger, logging.DEBUG)
def main() -> None:
    """Execute main script."""
    # : init args and add common parameters
    arg_parser = misc.common_args(description=__doc__)
    # : add script parameters
    arg_parser = more_args(arg_parser)
    args = arg_parser.parse_args()

    misc.cli_logging(args, __doc__.strip())

    to_skip = {"log", "verbose", "quiet"}
    kws = {
        k: v
        for k, v in vars(args).items()
        if k not in to_skip and v is not None
    }
    processor(**kws)


# ======================================================================
if __name__ == "__main__":
    main()
