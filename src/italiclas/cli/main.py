#!/usr/bin/env python3
"""CLI Main Application."""

import argparse
import logging

from italiclas import etl, ml
from italiclas.logger import logger
from italiclas.utils import misc, stopwatch


# ======================================================================
def more_args(arg_parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Handle more command-line application arguments."""
    arg_parser.add_argument(
        "text",
        metavar="TEXT",
        type=str,
        help="text to classify",
    )
    return arg_parser


# ======================================================================
@stopwatch.clockit_log(logger, logging.INFO)
def main() -> None:
    """Execute main script."""
    # : init args and add common parameters
    arg_parser = misc.common_args(description=__doc__)
    # : add script parameters
    arg_parser = more_args(arg_parser)
    args = arg_parser.parse_args()

    misc.cli_logging(args, __doc__.strip())

    etl.fetch_raw_data()
    etl.preprocess_raw_data()
    ml.train()
    result = ml.predict(args.text)
    logger.info("'%s' -> is_italian=%s", args.text, result)
    print(result)  # noqa: T201


# ======================================================================
if __name__ == "__main__":
    main()
