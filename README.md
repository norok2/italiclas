# Italiclas: *ITALI*an *CLAS*sifier



## Overview

**Italiclas** is a simple machine learning model designed to classify text as being Italian or not.

## Implementation

The model is implemented using a [scikit-learn](https://scikit-learn.org/stable/).
It is not meant to be particularly performant.
The main objective of this project is to apply state-of-the-art software engineering practices.
The package provides both a command-line interface (CLI) and a REST API.
The REST API can be served both locally and from a Docker container.
The first run requires an active internet connection, as the data is not provided directly

## Architecture
[Insert a diagram or textual description of your model's architecture, including data preprocessing, feature extraction, model training, and prediction stages.]

## Endpoints

The API exposes mainly these endpoints:

* **POST `/predict`**: Takes a text input and returns a boolean indicating whether the text is Italian.
* **GET `/ping`**: Check service availability and display the version.
* **GET `/docs`**: Display Swagger Web UI documentation.

For detailed specifications, see [`openapi.yaml`](https://github.com/norok2/italiclas/blob/main/openapi.yaml).

## Setup

### Prerequisites
- [GNU Make](https://www.gnu.org/software/make/) (version 4.3)
- [pipx](https://pipx.pypa.io/) (version 1.7.1)


### Installation
1. Clone the repository:
   ```shell
   git clone https://github.com/norok2/italiclas.git
   ```
2. Move to the project dir:
   ```shell
   cd italiclas
   ```
3. Install [Poetry](https://python-poetry.org/) using `pipx`
   ```shell
   make poetry_setup
   ```
4. Install dependencies using Poetry:
   ```shell
   make install
   ```

## Run

### TL;DR
 - Local run API: `make exec_api`
 - Docker run API: `make run_api`
 - Local run CLI: `poetry run italiclas "{text_to_predict}"`

### Training

The training action will be run (and cached):
 - at setup time when running the server application
   ```shell
   make exec_api
   ```
 - before prediction when running the command-line interface (CLI)
   ```shell
   poetry run italiclas "{text_to_predict}"
   ```
 - when running the training script (requires the clean dataset to exist already):
   ```shell
   poetry run italiclas_ml_training
   ```

Note that it is not strictly needed to run the training script independently.

### Prediction
1. **Start the API:** Run the API server using a framework like FastAPI or Flask.
2. **Make Predictions:** Send HTTP POST requests to the `/predict` endpoint with the text to be classified.

## Testing

### Unit Tests
The unit tests are implemented using the common [`pytest`](https://www.pytest.org/) package.
There is one test file per module.
Additionally, a number of tests are included as examples and run using the [`doctest`](https://docs.python.org/3/library/doctest.html) functionality from the Python standard library.
Some tests are yet to be implemented.

To run only these tests:
```shell
poetry run pytest tests/unit
```

### Integration Tests
The integration tests revolve around the provided endpoints.

To run only these tests:
```shell
poetry run pytest tests/integration
```

### Functional Tests
The only functional test available relies on testing the application CLI script.
These are yet to be implemented.

To run only these tests:
```shell
poetry run pytest tests/functional
```

### Load Tests
The performance tests are implemented in [`locust`](https://locust.io/).

## Monitoring
No specific monitoring solution is in place yet beyond extensive logging.

## Development

