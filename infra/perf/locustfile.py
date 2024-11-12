"""Load Test API Endpoint /predict."""

import numpy as np
from locust import HttpUser, between, tag, task

from italiclas import ml
from italiclas.config import cfg

GLOBAL_RNG = np.random.default_rng(seed=42)


def _get_random_text() -> str:
    """Get random text from training dataset."""
    data = ml.model.training_data(cfg.data_dir / cfg.clean_filename)
    return data.features.sample(1, random_state=GLOBAL_RNG).iloc[0]


class LocustUser(HttpUser):
    """Simple configuration for Locust test suite."""

    wait_time = between(1, 5)

    @tag("ping")
    @task(1)
    def ping(self) -> None:
        """Use GET /ping endpoint."""
        self.client.get("/ping")

    @tag("predict")
    @task(100)
    def predict(self) -> None:
        """Use POST /predict endpoint."""
        self.client.post("/predict", json={"text": _get_random_text()})
