ifndef _PYTHON_MAKEFILE
_PYTHON_MAKEFILE = 1  # Define a variable to mark inclusion


# Common Definitions
include Makefile.common.mk

# ======================================================================
#* Tools
PYTHON := python3
POETRY := poetry
POETRY_VERSION := 2.0.1

export POETRY_VIRTUALENVS_IN_PROJECT := true
export POETRY_VIRTUALENVS_CREATE := true


# ======================================================================
#* Files and dirs
PYTHON_FILES := $(wildcard $(shell find . -not -path '*/\.*' -name '*.py'))
RUFF_CONFIG_FILE := pyproject.toml
VENV_DIR := .venv/


# ======================================================================
#* Poetry
#* Install the tool
.PHONY: poetry_setup
poetry_setup: # Setup Poetry (locally using `pipx`)
	pipx install poetry

.PHONY: poetry_cleanup
poetry_cleanup: confirm_action  # Clean-up Poetry (locally using `pipx`)
	pipx uninstall ${POETRY}


#** Local install with Poetry
poetry.lock: pyproject.toml
	${POETRY} lock

${VENV_DIR}: poetry.lock
	${POETRY} install

.PHONY: install_py
install_py: pyproject.toml  # Install Poetry environment
	${POETRY} lock
	${POETRY} install


# ======================================================================
#* Automatic Fix and Check (Linter, Formatting)
show_ruff_version:
	${POETRY} run ruff --version

show_mypy_version:
	${POETRY} run mypy --version

#** Automatic fixing
fix_py_lint: show_ruff_version ${PYTHON_FILES}
	${POETRY} run ruff check --config ${RUFF_CONFIG_FILE} --fix .

fix_py_format: show_ruff_version ${PYTHON_FILES}
	${POETRY} run ruff format --config ${RUFF_CONFIG_FILE}  .

# when fixing: first lint, then format
fix_py: fix_py_lint fix_py_format

#** Checking only
check_py_format: show_ruff_version ${PYTHON_FILES}
	${POETRY} run ruff format --config ${RUFF_CONFIG_FILE} --check .

check_py_lint: show_ruff_version ${PYTHON_FILES}
	${POETRY} run ruff check --config ${RUFF_CONFIG_FILE} .

check_py_types: show_mypy_version ${PYTHON_FILES}
	${POETRY} run mypy --disable-error-code=import-untyped .

# when checking: first format, then lint
check_py: check_py_format check_py_lint check_py_types
check_all: check_py_format check_py_lint check_py_types


# ======================================================================
#* Test & Coverage
.PHONY: test
test_py:  # Run unit tests
	${POETRY} run coverage run -m pytest --doctest-modules src/ tests/

#* Coverage
.PHONY: coverage
coverage_py:  # Display Code Coverage report
	${POETRY} run coverage report -m


# ======================================================================
#* Cleaning
.PHONY: clean_checks_cache
clean_checks_cache:
	-rm -rf .ruff_cache
	-rm -rf .mypy_cache

.PHONY: clean_tests_cache
clean_tests_cache:
	-rm -rf .pytest_cache
	-rm -rf .coverage

.PHONY: clean_pycache
clean_pycache:
	-find . -name "__pycache__" -type d -exec rm -rf {} +

.PHONY: clean_venv
echo_clean_venv:
	@echo "${INFO_MSG}: Cleaning Virtual Environment from \`${MAGENTA}${VENV_DIR}${NORMAL}\`"
clean_venv: echo_clean_venv confirm_action  # Clean Virtual Environment
	-rm -rf ${VENV_DIR}

.PHONY: clean_py
echo_clean_py:
	@echo "${INFO_MSG}: Cleaning Python temporary data"
clean_py:  # Clean Python temporary data
clean_py: echo_clean_py confirm_action clean_checks_cache clean_tests_cache clean_pycache

.PHONY: clean_all_py
echo_clean_all_py:  # Clean all Python data
	@echo "${INFO_MSG}: Cleaning all Python data"
clean_all_py: echo_clean_all_py confirm_action clean_py clean_venv


# ======================================================================
# ifndef _PYTHON_MAKEFILE
endif
