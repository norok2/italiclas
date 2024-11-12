"""ML Model."""

import functools
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, get_args

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import GridSearchCV
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from italiclas.logger import logger
from italiclas.utils import core


# ======================================================================
def base_pipeline() -> Pipeline:
    """Get the ML model pipeline."""
    # TODO @norok2: # noqa: FIX002, TD003
    #   - read optimized parameters from configuration
    return Pipeline([("vect", CountVectorizer()), ("clf", MultinomialNB())])


# ======================================================================
@functools.lru_cache(None)
def pre_trained_pipeline(filepath: Path) -> Pipeline:
    """Load pre-trained ML model pipeline.

    Args:
        filepath: The ML model pipeline filepath.

    Returns:
        The pre-trained ML model pipeline.

    """
    logger.info("[ML] Load ML model pipeline '%s'", filepath)
    return core.load_obj(filepath)


# ======================================================================
@dataclass
class TrainingData:
    """Traing data result."""

    features: pd.DataFrame
    target: pd.Series


# ======================================================================
@functools.lru_cache(None)
def training_data(filepath: Path) -> Pipeline:
    """Load training data.

    Args:
        filepath: The input filepath.

    Returns:
        The training data.

    """
    logger.info("[ML] Load clean data from '%s'", filepath)
    df = pd.read_csv(filepath)  # noqa: PD901
    features = df["text"]
    target = df["is_italian"]
    return TrainingData(features=features, target=target)


# ======================================================================
ScoringType = Literal[
    "accuracy",
    "balanced_accuracy",
    "average_precision",
    "neg_brier_score",
    "f1",
    "neg_log_loss",
    "precision",
    "recall",
    "jaccard",
    "roc_auc",
]
SCORINGS = get_args(ScoringType)


# ======================================================================
def compute_scores(
    pipeline: Pipeline,
    filepath: Path,
    scorings: Sequence[ScoringType] = (
        "accuracy",
        "precision",
        "recall",
        "f1",
        "roc_auc",
    ),
    cross_validation: int = 3,
) -> None:
    """Compute scores on cross-validation split.

    Args:
        pipeline: The ML model pipeline.
        filepath: The training data filepath.
        scorings: The scoring metrics to compute.
            Defaults to ("accuracy", "precision", "recall", "f1", "roc_auc").
        cross_validation: The number of cross validation splits.
            Defaults to 3.

    """
    # : Get training data
    data = training_data(filepath)
    features = data.features
    target = data.target
    # : Compute scores on cross-validation splits
    logger.info(
        "[ML] ML model scores on %s cross-validation splits",
        cross_validation,
    )
    for scoring in scorings:
        grid_search = GridSearchCV(
            pipeline,
            param_grid={},
            scoring=scoring,
            cv=cross_validation,
        )
        grid_search.fit(features, target)
        result = grid_search.best_score_
        logger.info(
            "[ML] %s = %s",
            core.labelify(core.namify(scoring)),
            core.number2str(result),
        )
