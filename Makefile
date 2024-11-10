#* Config
include Makefile.common.mk


#** Project
PROJECT_NAME := $(shell ${PYTHON} -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['tool']['poetry']['name'])")
export API_PORT ?= 5000
export API_TIMEOUT_CONN ?= 6
export API_TIMEOUT ?= 6
export API_NUM_WORKERS ?= 4


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
	${POETRY} run coverage run -m pytest --doctest-modules

#* Coverage
.PHONY: coverage
coverage:  ## Display Code Coverage report
	${POETRY} run coverage report -m


# ======================================================================
#* Local Run
#** API
.PHONY: exec_api
# exec_api: export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
exec_api:
	${POETRY} run uvicorn \
		--workers ${API_NUM_WORKERS} \
		--port ${API_PORT} \
		--timeout-keep-alive ${API_TIMEOUT} \
		--reload \
		${PROJECT_NAME}.api.main:app