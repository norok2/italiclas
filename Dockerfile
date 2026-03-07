#* Build the Docker image for servinAPI
#** Specify base image resources
ARG BASE_IMAGE=python
ARG BASE_VERSION=3.12-slim

# ======================================================================
#* `base` stage
FROM ${BASE_IMAGE}:${BASE_VERSION} as base

ENV \
    PROJECT_NAME=italiclas \
    UV_VERSION=0.10.9 \
    USERNAME=data-science \
    BASE_PATH=/app \
    VENV_DIR=.venv \
    UV_NO_INTERACTION=true \
    UV_CACHE_DIR=/tmp/uv_cache
# path used by uv to locate the Virtual Environment to use
ENV VIRTUAL_ENV=${BASE_PATH}/${VENV_DIR}

RUN pip3 install uv && uv --version


# ======================================================================
#* `builder` stage
FROM base as builder
WORKDIR /

#** Install Environment (makes runtime installation faster)
COPY pyproject.toml uv.lock /
RUN uv sync --extra main --extra api

# ======================================================================
#* `runtime` stage
FROM base as runtime
# ensure pipeline failure if a single pipeline step fails
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
    pyproject.toml uv.lock \
    ./

#** Initialize Virtual Env from builder
COPY --from=builder .venv .venv

#** Install environment with package
RUN uv sync --extra main --extra api

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
CMD ["exec uv run uvicorn --workers ${API_NUM_WORKERS} --host ${API_HOST} --port ${API_PORT} --timeout-keep-alive ${API_TIMEOUT} ${PROJECT_NAME}.api.main:app"]
