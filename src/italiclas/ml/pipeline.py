"""ML Pipeline."""

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline


# ======================================================================
def get_pipeline() -> Pipeline:
    """Get the ML pipeline."""
    # TODO @norok2: # noqa: FIX002, TD003
    #   - read optimized parameters from configuration
    return Pipeline(
        [
            ("vect", CountVectorizer(strip_accents="unicode")),
            ("clf", MultinomialNB()),
        ],
    )
