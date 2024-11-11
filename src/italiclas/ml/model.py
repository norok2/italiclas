"""ML Model."""

import functools
from pathlib import Path

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from italiclas.logger import logger
from italiclas.utils import core


# ======================================================================
def base_pipeline() -> Pipeline:
    """Get the ML model pipeline."""
    # TODO @norok2: # noqa: FIX002, TD003
    #   - read optimized parameters from configuration
    return Pipeline(
        [
            ("vect", CountVectorizer(strip_accents="unicode")),
            ("clf", MultinomialNB()),
        ],
    )


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
