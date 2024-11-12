#!/usr/bin/env python3
"""ML Train Model."""

import argparse
import itertools
import logging
import re
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

import pandas as pd

# this is required for HalvingGridSearchCV to work
from sklearn.experimental import enable_halving_search_cv  # noqa: F401
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import HalvingGridSearchCV, train_test_split
from sklearn.pipeline import Pipeline

from italiclas import ml
from italiclas.config import cfg
from italiclas.logger import logger
from italiclas.utils import core, misc, stopwatch


# ======================================================================
@stopwatch.clockit_log(logger, logging.INFO)
def train(  # noqa: PLR0913
    data_filepath: Path = cfg.data_dir / cfg.clean_filename,
    model_filepath: Path = cfg.pipeline_dir / cfg.ml_pipeline_filename,
    *,
    test_size: float = 0.35,
    random_seed: int = 42,
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
        data_filepath: The clean data filepath.
            Defaults to cfg.data_dir/cfg.clean_filename.
        model_filepath: The ML model pipeline filepath.
            Defaults to None.
        test_size: The fractional size of the test set.
            Defaults to 0.35.
        random_seed: The random state seed.
            Defaults to 42.
        scorers: The scorers to use for ML model evaluation.
            Defaults to
            (accuracy_score, precision_score, recall_score, f1_score).
        force: Force new computation.
            Defaults to False.

    Returns:
        The trained pipeline.

    Examples:
        >>> train()  # doctest: +SKIP
        Pipeline(steps=[('vect', CountVectorizer(strip_accents='unicode')),\
('clf', MultinomialNB())])

    """
    if force or not model_filepath.is_file():
        logger.info("[ML] Load training data from '%s'", data_filepath)
        df = pd.read_csv(data_filepath)  # noqa: PD901
        features = df["text"]
        target = df["is_italian"]
        # : Perform training on train/test split
        features_train, features_test, target_train, target_test = (
            train_test_split(
                features,
                target,
                test_size=test_size,
                random_state=random_seed,
            )
        )
        pipeline = ml.model.base_pipeline()
        logger.info(
            "[ML] New ML model pipeline `%s`",
            core.no_blanks(str(pipeline)),
        )
        logger.info("[ML] Train ML model pipeline on train split")
        pipeline.fit(features_train, target_train)
        logger.info("[ML] Test ML model pipeline on test split")
        target_pred = pipeline.predict(features_test)
        for scorer in scorers:
            result = scorer(target_test, target_pred)
            logger.info(
                "[ML] %s = %s",
                core.labelify(core.namify(scorer.__name__)),
                core.number2str(result),
            )
        # : Hyper-parameters optimization
        param_grid = {
            "vect__strip_accents": ["ascii", "unicode", None],
            "vect__ngram_range": [
                (a, b)
                for a, b in itertools.combinations(range(1, 6), 2)
                if a <= b
            ],
            "vect__analyzer": ["word", "char", "char_wb"],
            "clf__alpha": [0.1, 0.5, 1.0],
            "clf__fit_prior": [True, False],
        }
        logger.info("[ML] Hyperparameters optimization on: %s")
        grid_search = HalvingGridSearchCV(
            pipeline,
            param_grid=param_grid,
            verbose=getattr(logging, cfg.log_level),
        )
        grid_search.fit(features, target)
        logger.info("[ML] Optimal score: %s", grid_search.best_score_)
        logger.info("[ML] Optimal parameters: %s", grid_search.best_params_)
        pipeline = grid_search.best_estimator_
        # : Final re-training with optimized parameters
        logger.info("[ML] Re-train ML model pipeline on full dataset")
        pipeline.fit(features, target)
        logger.info("[ML] Save ML model pipeline to '%s'", model_filepath)
        core.save_obj(pipeline, model_filepath)
    else:
        logger.info("[ML] Load ML model pipeline from '%s'", model_filepath)
        pipeline = core.load_obj(model_filepath)
    if pipeline:
        logger.info("[ML] ML model pipeline ready for prediction")
    return pipeline


# ======================================================================
def more_args(arg_parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Handle more command-line application arguments."""

    def _str2func(name: str) -> Callable | None:  # ensure valid function name
        if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name):
            func = eval(name)  # noqa: S307
            if callable(func):
                return func
        return None

    arg_parser.add_argument(
        "-i",
        "--data_filepath",
        metavar="FILE",
        type=str,
        help="input clean data file path [%(default)s]",
        default=cfg.data_dir / cfg.clean_filename,
    )
    arg_parser.add_argument(
        "-o",
        "--model_filepath",
        metavar="FILE",
        type=str,
        help="output ML model pipeline file path [%(default)s]",
        default=cfg.pipeline_dir / cfg.ml_pipeline_filename,
    )
    arg_parser.add_argument(
        "-e",
        "--test_size",
        metavar="FLOAT",
        type=float,
        help="fractional size of the test dateset [%(default)s]",
        default=0.35,
    )
    arg_parser.add_argument(
        "-r",
        "--random_seed",
        metavar="FLOAT",
        type=int,
        help="fractional size of the test dateset [%(default)s]",
        default=42,
    )
    arg_parser.add_argument(
        "-s",
        "--scorers",
        metavar="SCORER",
        nargs="+",
        type=_str2func,
        help="scorers for ML model evaluation [%(default)s]",
        default=[accuracy_score, precision_score, recall_score, f1_score],
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
    train(**kws)


# ======================================================================
if __name__ == "__main__":
    main()
