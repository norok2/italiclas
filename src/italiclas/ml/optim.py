#!/usr/bin/env python3
"""ML Train Model."""

import argparse
import itertools
import logging
from pathlib import Path

# this is required for HalvingGridSearchCV to work
from sklearn.experimental import enable_halving_search_cv  # noqa: F401
from sklearn.model_selection import HalvingGridSearchCV
from sklearn.pipeline import Pipeline

from italiclas.config import cfg
from italiclas.logger import logger
from italiclas.ml import model
from italiclas.utils import core, misc, stopwatch


# ======================================================================
@stopwatch.clockit_log(logger, logging.INFO)
def hyperparams(
    data_filepath: Path = cfg.data_dir / cfg.clean_filename,
    params_filepath: Path = cfg.ml_dir / cfg.optim_params_filename,
    *,
    scoring: model.ScoringType | None = "f1",
    cross_validation: int = 5,
    force: bool = False,
) -> Pipeline:
    """Perform ML parameters optimization.

    Args:
        data_filepath: The clean data filepath.
            Defaults to cfg.data_dir/cfg.clean_filename.
        params_filepath: The ML model parameters filepath.
            Defaults to cfg.data_dir/cfg.ml_params_filename.
        scoring: The scoring metrics used for optimization.
            Defaults to "f1".
        cross_validation: The number of cross validation splits.
            Defaults to 5.
        force: Force new computation.
            Defaults to False.

    Returns:
        The trained pipeline.

    Examples:
        >>> hyperparams()  # doctest: +SKIP

    """
    if force or not params_filepath.is_file():
        # : Get training data
        data = model.training_data(data_filepath)
        features = data.features
        target = data.target
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
        logger.info("[ML] Param grid: %s", param_grid)
        pipeline = model.base_pipeline()
        grid_search = HalvingGridSearchCV(
            pipeline,
            param_grid=dict(param_grid),
            scoring=scoring,
            cv=cross_validation,
            verbose=getattr(logging, cfg.log_level),
        )
        grid_search.fit(features, target)
        best_score = grid_search.best_score_
        logger.info("[ML] Optimal score (%s): %s", scoring, best_score)
        params = grid_search.best_params_
        params.update({"_scoring": scoring})
        logger.info("[ML] Save parameters to: '%s'", params_filepath)
        core.save_obj(params, params_filepath)
    else:
        params = core.load_obj(params_filepath)
        logger.info("[ML] Load parameters from: '%s'", params_filepath)
    logger.info("[ML] Optimal params: %s", params)
    return params


# ======================================================================
def more_args(arg_parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Handle more command-line application arguments."""
    arg_parser.add_argument(
        "-i",
        "--data_filepath",
        metavar="FILE",
        type=str,
        help="input clean data filepath [%(default)s]",
        default=cfg.data_dir / cfg.clean_filename,
    )
    arg_parser.add_argument(
        "-o",
        "--params_filepath",
        metavar="FILE",
        type=str,
        help="output ML model parameters filepath [%(default)s]",
        default=cfg.ml_dir / cfg.optim_params_filename,
    )
    arg_parser.add_argument(
        "-s",
        "--scoring",
        type=str,
        help="Scoring metric to optimize [%(default)s]",
        default="f1",
    )
    arg_parser.add_argument(
        "-c",
        "--cross_validation",
        type=int,
        help="Cross Validation splits [%(default)s]",
        default=5,
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
    hyperparams(**kws)


# ======================================================================
if __name__ == "__main__":
    main()
