#!/usr/bin/env python3
"""ML Train Model."""

import argparse
import logging
from pathlib import Path

from sklearn.pipeline import Pipeline

from italiclas.config import cfg
from italiclas.logger import logger
from italiclas.ml import model, optim
from italiclas.utils import core, misc, stopwatch


# ======================================================================
@stopwatch.clockit_log(logger, logging.INFO)
def train(  # noqa: PLR0913
    data_filepath: Path = cfg.data_dir / cfg.clean_filename,
    pipeline_filepath: Path = cfg.pipeline_dir / cfg.ml_pipeline_filename,
    params_filepath: Path = cfg.pipeline_dir / cfg.ml_params_filename,
    *,
    calc_scores: bool = False,
    optimize: bool = False,
    force: bool = False,
) -> Pipeline:
    """Perform ML training.

    Args:
        data_filepath: The clean data filepath.
            Defaults to cfg.data_dir/cfg.clean_filename.
        pipeline_filepath: The ML model pipeline filepath.
            Defaults to cfg.data_dir/cfg.ml_pipeline_filename.
        params_filepath: The ML model parameters filepath.
            Defaults to cfg.data_dir/cfg.ml_params_filename.
        calc_scores: Compute ML model scores on cross valdation data.
            Defaults to False.
        optimize: Force new optimization.
            Defaults to False.
        force: Force new computation.
            Defaults to False.

    Returns:
        The trained (and optimized) pipeline.

    Examples:
        >>> train()  # doctest: +SKIP
        Pipeline(steps=[('vect', CountVectorizer()), ('clf', MultinomialNB())])

    """
    if force or not pipeline_filepath.is_file():
        pipeline = model.base_pipeline()
        # : Get training data
        data = model.training_data(data_filepath)
        features = data.features
        target = data.target
        # : Get params
        params = optim.hyperparams(
            data_filepath,
            params_filepath,
            force=optimize,
        )
        params = {k: v for k, v in params.items() if not k.startswith("_")}
        pipeline.set_params(**params)
        # : Training on full dataset
        logger.info("[ML] Train ML model pipeline on full dataset")
        pipeline.fit(features, target)
        logger.info("[ML] Save ML model pipeline to '%s'", pipeline_filepath)
        core.save_obj(pipeline, pipeline_filepath)
    else:
        logger.info("[ML] Load ML model pipeline from '%s'", pipeline_filepath)
        pipeline = core.load_obj(pipeline_filepath)
    if calc_scores:
        model.compute_scores(pipeline, data_filepath)
    return pipeline


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
        "--pipeline_filepath",
        metavar="FILE",
        type=str,
        help="output ML model pipeline filepath [%(default)s]",
        default=cfg.pipeline_dir / cfg.ml_pipeline_filename,
    )
    arg_parser.add_argument(
        "-p",
        "--params_filepath",
        metavar="FILE",
        type=str,
        help="output ML model parameters filepath [%(default)s]",
        default=cfg.pipeline_dir / cfg.ml_params_filename,
    )
    arg_parser.add_argument(
        "-s",
        "--calc_scores",
        action="store_true",
        help="compute ML model scores on cross validation data [%(default)s]",
    )
    arg_parser.add_argument(
        "-x",
        "--optimize",
        action="store_true",
        help="force new optimization [%(default)s]",
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
