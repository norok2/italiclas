#!/usr/bin/env python3
"""ML Predict with Model."""

import argparse
import logging
from pathlib import Path

from italiclas import ml
from italiclas.config import cfg
from italiclas.logger import logger
from italiclas.utils import misc, stopwatch


# ======================================================================
@stopwatch.clockit_log(logger, logging.INFO)
def predict(
    text: str,
    ml_pipeline_filepath: Path = cfg.ml_dir / cfg.ml_model_pipeline_filename,
) -> bool:
    """Perform ML training.

    Args:
        text: The input text to classify.
            Defaults to cfg.data_dir/cfg.clean_filename.
        ml_pipeline_filepath: The ML model pipeline filepath.
            Defaults to cfg.pipeline_dir/cfg.ml_pipeline_filename.

    Returns:
        The prediction outcome.
        True if the text is Italian, False otherwise.

    Examples:
        >>> predict("ciao mondo")  # doctest: +SKIP
        True
        >>> predict("hello world")  # doctest: +SKIP
        False

    """
    if ml_pipeline_filepath.is_file():
        logger.info(
            "[ML] Predict from ML model pipeline '%s'",
            ml_pipeline_filepath,
        )
    pipeline = ml.model.pre_trained_pipeline(ml_pipeline_filepath)
    result = next(iter(pipeline.predict([text])))
    logger.debug("[ML] Input: '%s' -> Prediction: %s", text, result)
    return result


# ======================================================================
def more_args(arg_parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Handle more command-line application arguments."""
    arg_parser.add_argument(
        "text",
        metavar="TEXT",
        type=str,
        help="text to classify",
    )
    arg_parser.add_argument(
        "-i",
        "--ml_pipeline_filepath",
        metavar="FILE",
        type=str,
        help="input ML model pipeline filepath [%(default)s]",
        default=cfg.ml_dir / cfg.ml_model_pipeline_filename,
    )
    return arg_parser


# ======================================================================
@stopwatch.clockit_log(logger, logging.DEBUG)
def main() -> None:
    """Execute main script."""
    # : init args and add common parameters
    arg_parser = misc.common_args(
        description=__doc__,
        arguments=["help", "version", "verbose", "quiet", "log"],
    )
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
    print(predict(**kws))  # noqa: T201


# ======================================================================
if __name__ == "__main__":
    main()
