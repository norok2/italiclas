#!/usr/bin/env python3
"""ML Train Model."""

import argparse
import logging
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from italiclas.config import cfg
from italiclas.logger import logger
from italiclas.ml.pipeline import get_pipeline
from italiclas.utils import core, misc, stopwatch


# ======================================================================
@stopwatch.clockit_log(logger, logging.INFO)
def train(  # noqa: PLR0913
    data_filepath: Path = cfg.data_dir / cfg.clean_filename,
    pipeline_filepath: Path = cfg.pipeline_dir / cfg.pipeline_filename,
    *,
    test_size: float = 0.3,
    random_state: int = 42,
    scorers: Sequence[Callable[[Any, Any], float]] = (
        accuracy_score,
        precision_score,
        recall_score,
        f1_score,
    ),
    force: bool = False,
) -> Pipeline:
    """Perform ML training.

    Args:
        data_filepath: _description_.
            Defaults to cfg.data_dir/cfg.clean_filename.
        pipeline_filepath: _description_.
            Defaults to None.
        test_size: _description_.
            Defaults to 0.3.
        random_state: _description_.
            Defaults to 42.
        scorers: _description_.
            Defaults to
            (accuracy_score, precision_score, recall_score, f1_score).
        force: Force new computation.
            Defaults to False.

    Returns:
        _description_

    """
    logger.info("[ML] Load training data from '%s'", data_filepath)
    df = pd.read_csv(data_filepath)  # noqa: PD901
    features = df["text"]
    target = df["is_italian"]
    features_train, features_test, target_train, target_test = (
        train_test_split(
            features,
            target,
            test_size=test_size,
            random_state=random_state,
        )
    )
    if force or not pipeline_filepath.is_file():
        pipeline = get_pipeline()
        logger.info("[ML] Train model pipeline '%s'", pipeline)
        pipeline.fit(features_train, target_train)
        logger.info("[ML] Save model pipeline to '%s'", pipeline_filepath)
        core.save_obj(pipeline, pipeline_filepath)
    else:
        logger.info("[ML] Load model pipeline from '%s'", pipeline_filepath)
        pipeline = core.load_obj(pipeline_filepath)

    target_pred = pipeline.predict(features_test)
    for scorer in scorers:
        result = scorer(target_test, target_pred)
        logger.info(
            "[ML] %s = %s",
            core.labelify(core.namify(scorer.__name__)),
            core.number2str(result),
        )


# ======================================================================
def more_args(arg_parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Handle more command-line application arguments."""
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
    train(**kws)


# ======================================================================
if __name__ == "__main__":
    main()
