#* Build the Docker image for servinAPI
#** Specify base image resources
ARG BASE_IMAGE=python
ARG BASE_VERSION=3.12-slim

# ======================================================================
#* `base` stage
FROM ${BASE_IMAGE}:${BASE_VERSION} as base

ENV \
    PROJECT_NAME=italiclas \
    POETRY_VERSION=1.8.4 \
    USERNAME=data-science \
    BASE_PATH=/app \
    VENV_DIR=.venv \
    POETRY_NO_INTERACTION=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_CACHE_DIR=/tmp/poetry_cache
# path used by Poetry to locate the Virtual Environment to use
ENV VIRTUAL_ENV=${BASE_PATH}/${VENV_DIR}

RUN pip3 install poetry==${POETRY_VERSION} && poetry --version


# ======================================================================
#* `builder` stage
FROM base as builder
WORKDIR /

#** Install Environment
COPY pyproject.toml poetry.lock /
RUN poetry install --no-root --only main,api

# ======================================================================
#* `runtime` stage
FROM base as runtime
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
WORKDIR ${BASE_PATH}

#** Lower privileges for entrypoint
RUN \
    # Add user
    useradd --shell /sbin/nologin --create-home "${USERNAME}" \
    # User to own the base path
    && chown -R "${USERNAME}":"${USERNAME}" "${BASE_PATH}"

#** Install runtime binary pre-requisites
RUN \
    apt-get clean \
    && rm -rf /var/lib/apt/lists/*

#** Copy project code
COPY --link src/ src/
COPY --link tests/ tests/
COPY --link artifacts/ artifacts/
COPY --link \
    LICENSE.md README.md .env.app openapi.yaml \
    Makefile Makefile.common.mk \
    pyproject.toml poetry.lock \
    ./

#** Initialize Virtual Env from builder
COPY --from=builder ${POETRY_CACHE_DIR} ${POETRY_CACHE_DIR}

#** Install environment with package
RUN poetry install --only main,api

#** Update PATH and PYTHONPATH
ENV PATH=${VIRTUAL_ENV}/bin:${PATH}

#** Set API serving env vars
ENV \
    API_NUM_WORKERS=2 \
    API_HOST=0.0.0.0 \
    API_PORT=5000 \
    API_TIMEOUT=5

USER ${USERNAME}

ENTRYPOINT ["/bin/sh", "-c"]
CMD ["exec poetry run uvicorn --workers ${API_NUM_WORKERS} --host ${API_HOST} --port ${API_PORT} --timeout-keep-alive ${API_TIMEOUT} ${PROJECT_NAME}.api.main:app"]
