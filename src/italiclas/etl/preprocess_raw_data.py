#!/usr/bin/env python3
"""ETL Preprocess Raw Data."""

import argparse
import logging
from pathlib import Path

import pandas as pd

from italiclas.config import cfg
from italiclas.logger import logger
from italiclas.utils import core, misc, stopwatch


# ======================================================================
@stopwatch.clockit_log(logger, logging.INFO)
def preprocess_raw_data(
    raw_filename: str = cfg.raw_filename,
    clean_filename: str = cfg.clean_filename,
    dirpath: Path = cfg.data_dir,
    *,
    force: bool = False,
) -> Path | None:
    """Preprocess and clean raw data.

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

    Examples:
        >>> preprocess_raw_data()  # doctest: +SKIP
        PosixPath('artifacts/data/clean_data.csv')

    """
    raw_filepath = dirpath / raw_filename
    clean_filepath = dirpath / clean_filename
    if force or not clean_filepath.is_file():
        logger.info("[ETL] Preprocessing raw data '%s'", raw_filepath)
        df = pd.read_csv(raw_filepath)  # noqa: PD901
        df = df.rename(columns=lambda x: core.namify(x.lower()))  # noqa: PD901
        df["is_italian"] = df["language"] == "Italian"
        df.drop(["language"], axis=1, inplace=True)
        logger.info(df.columns)
        df.to_csv(clean_filepath, index=False)
        logger.info("[ETL] Clean data stored to '%s'", clean_filepath)
    else:
        logger.info("[ETL] Load clean data from '%s'", clean_filepath)
        df = pd.read_csv(clean_filepath)  # noqa: PD901
    # : inspect clean dataset
    num_total = df["is_italian"].count()
    num_italian = df["is_italian"].sum()
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
    preprocess_raw_data(**kws)


# ======================================================================
if __name__ == "__main__":
    main()
