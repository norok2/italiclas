#* Config
include Makefile.common.mk


#** Project
PROJECT_NAME := $(shell ${PYTHON} -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['tool']['poetry']['name'])")
IMAGE_NAME := $(subst _,-,${PROJECT_NAME})
DOCKERFILE := infra/container/Dockerfile
export PKG_DIR := src/${PROJECT_NAME}
export API_HOST ?= 0.0.0.0
export API_PORT ?= 5000
export API_TIMEOUT_CONN ?= 6
export API_TIMEOUT ?= 6
export API_NUM_WORKERS ?= 4
export TEST_API_HOST ?= http://localhost
export TEST_API_PORT ?= 5000


.DEFAULT_GOAL: help


# ======================================================================
#* Installation
poetry.lock: pyproject.toml
	${POETRY} lock

install: export POETRY_VIRTUALENVS_IN_PROJECT=true
install: export POETRY_VIRTUALENVS_CREATE=true
install: poetry.lock  ## Install Poetry environment
	${POETRY} install

uninstall:
	rm -rf .venv


# ======================================================================
#* Test & Coverage
.PHONY: test
test:  ## Run unit tests
	${POETRY} run coverage run -m pytest --doctest-modules src/ tests/

#* Coverage
.PHONY: coverage
coverage:  ## Display Code Coverage report
	${POETRY} run coverage report -m

.PHONY: test_api
test_api:  ## Run load tests
	${POETRY} run locust --locustfile infra/perf/locustfile.py --host ${TEST_API_HOST}:${TEST_API_PORT}

# ======================================================================
#* Local Run
#** API
.PHONY: exec_api
# exec_api: export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
exec_api:
	${POETRY} run uvicorn \
		--workers ${API_NUM_WORKERS} \
		--host ${API_HOST} \
		--port ${API_PORT} \
		--timeout-keep-alive ${API_TIMEOUT} \
		--reload \
		${PROJECT_NAME}.api.main:app


# ======================================================================
#* Misc
openapi.yaml: ${PYTHON_FILES}
	${POETRY} run ${PKG_DIR}/api/gen_openapi.py
