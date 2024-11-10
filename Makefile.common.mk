# Common Definitions

# ======================================================================
#* Project files and dirs
PYTHON_FILES := $(wildcard $(shell find . -not -path '*/\.*' -name '*.py'))
RUFF_CONFIG_FILE := pyproject.toml
VENV_DIR := .venv/

# ======================================================================
#* Tools
PYTHON := python3
DOCKER := docker
POETRY := poetry

# ======================================================================
#* Colors
BLACK := $(shell tput setaf 0)
RED := $(shell tput setaf 1)
GREEN := $(shell tput setaf 2)
YELLOW := $(shell tput setaf 3)
BLUE := $(shell tput setaf 4)
MAGENTA := $(shell tput setaf 5)
CYAN := $(shell tput setaf 6)
WHITE := $(shell tput setaf 7)
BLACK_BG := $(shell tput setab 0)
RED_BG := $(shell tput setab 1)
GREEN_BG := $(shell tput setab 2)
YELLOW_BG := $(shell tput setab 3)
BLUE_BG := $(shell tput setab 4)
MAGENTA_BG := $(shell tput setab 5)
CYAN_BG := $(shell tput setab 6)
WHITE_BG := $(shell tput setab 7)
NORMAL := $(shell tput sgr0)
BOLD := $(shell tput bold)
UNDERLINE := $(shell tput smul)
BLINK := $(shell tput blink)
REVERSE := $(shell tput rev)

# ======================================================================
#* Message types
INFO_MSG := ${CYAN}Info${NORMAL}
WARN_MSG := ${YELLOW}Warning${NORMAL}
ERR_MSG := ${RED}Error${NORMAL}

# ======================================================================
#* Misc
# to be synced with `Dockerfile` and `.gitignore`
export TEMP_PATH ?= tmp_dir
export DOTENV_FILE ?= .env
export GIT_COMMIT_SHA1 ?= $(shell git rev-parse HEAD)

# ======================================================================
#* Display Help
# To display in `help` the target line must contain a comment starting with ##
.PHONY: help
help:  ## Display this help
	@echo "Please use \`${MAGENTA}make ${CYAN}<target>${NORMAL}\` where ${CYAN}<target>${NORMAL} is one of:"
	@grep -E '^[a-zA-Z_\.\-\%]+\: .*?## .*$$' ${MAKEFILE_LIST} | sed 's/^[^:]*://' | awk 'BEGIN {FS = ":.*?##"} {printf "${CYAN}%-24s${NORMAL} %s\n", $$1, $$2}'

# ======================================================================
#* Debug
# Display a variable
echo_var = $(info $(1) = $($(1)))

# Display ALL variables available to Make
.PHONY: print_all_vars
print_all_vars:
	@echo "(All variables)"
	$(foreach v, $(.VARIABLES), $(info $(v) = $(value $(v))))

# Display all variables defined in local Makefile(s)
.PHONY: print_local_vars
print_local_vars:
	@echo "(Makefile variables)"
	$(foreach v, \
		$(shell echo "$(filter-out .VARIABLES,$(.VARIABLES))" | tr ' ' '\n' | sort), \
		$(if $(filter file,$(origin $(v))), $(info $(shell printf "%24s" "$(v)") = $(value $(v)))) \
	)

# Display the value of a specific variable
# usage: `make print_XXX` to display the value of XXX: `XXX = <VALUE>`
print_%:
	@echo "${YELLOW}$*${NORMAL} = ${GREEN}${$*}${NORMAL}"


# ======================================================================
#* Utilities
#** Confirm Action
confirm_action:
	@echo "Are you sure [${GREEN}y${NORMAL}/${BOLD}${RED}N${NORMAL}] " && read ans && [ $${ans:-N} = y ]

#** Check var not empty
define check_var_not_empty  # (VAR_NAME,IS_BREAKING) -> NULL
	@VAR_NAME=$(1); \
	VALUE=$($(1)); \
	IS_BREAKING=$(2); \
	if [ -z "$${VALUE}" ]; then \
		echo "${WARN_MSG}: ${YELLOW}$${VAR_NAME}${NORMAL} is empty"; \
		([ "$${IS_BREAKING}" -eq 0 ] && (true) || (exit -1)); \
	else \
		echo "${INFO_MSG}: Using ${YELLOW}$${VAR_NAME}${NORMAL}=\"${GREEN}$${VALUE}${NORMAL}\""; \
	fi
endef

#** Check var is one of
define check_var_one_of # (VAR_NAME,IS_BREAKING,VALUES) -> NULL
	@VAR_NAME=$(1); \
	VALUE=$($(1)); \
	IS_BREAKING=$(2); \
	VALUES=$(3); \
	VALID=0; \
	for val in $${VALUES[@]}; do \
		if [ "$${VALUE}" = "$${val}" ]; then \
			VALID=1; \
			break; \
		fi; \
	done; \
	if [ $${VALID} -eq 1 ]; then \
		echo "${INFO_MSG}: ${YELLOW}$${VAR_NAME}${NORMAL}=\"${GREEN}$${VALUE}${NORMAL}\" in allowlist"; \
	else \
		echo "${WARN_MSG}: ${YELLOW}$${VAR_NAME}${NORMAL}=\"${GREEN}$${VALUE}${NORMAL}\" NOT in allowlist"; \
		([ "$${IS_BREAKING}" -eq 0 ] && (true) || (exit -1)); \
	fi
endef

#** Check if file exists
define check_file_exists  # (FILE_PATH,IS_BREAKING) -> NULL
	@FILE_PATH=$(1); \
	IS_BREAKING=$(2); \
	if [ -f "$${FILE_PATH}" ]; then \
		echo "${INFO_MSG}: \`${MAGENTA}$${FILE_PATH}${NORMAL}\` found"; \
	else \
		echo "${WARN_MSG}: \`${MAGENTA}$${FILE_PATH}${NORMAL}\` NOT found"; \
		([ "$${IS_BREAKING}" -eq 0 ] && (true) || (exit -1)); \
	fi
endef


# ======================================================================
#* Poetry
.PHONY: poetry_setup
poetry_setup: ## Setup Poetry (locally using `pipx`)
	pipx install poetry

.PHONY: poetry_cleanup
poetry_cleanup: confirm_action  ## Clean-up Poetry (locally using `pipx`)
	pipx uninstall ${POETRY}


# ======================================================================
#* Automatic Fix and Check (Linter, Formatting)
show_ruff_version:
	${POETRY} run ruff --version

#** Automatic fixing
fix_py_lint: show_ruff_version ${PYTHON_FILES}
	${POETRY} run ruff check --config ${RUFF_CONFIG_FILE} --fix .

fix_py_format: show_ruff_version ${PYTHON_FILES}
	${POETRY} run ruff format --config ${RUFF_CONFIG_FILE}  .

# when fixing: first lint, then format
fix_py: fix_py_lint fix_py_format
fix_all: fix_py_lint fix_py_format
fix: fix_py  ## Automatically Fix Formatting and Lint

#** Checking only
check_py_format: show_ruff_version ${PYTHON_FILES}
	${POETRY} run ruff format --config ${RUFF_CONFIG_FILE} --check .

check_py_lint: show_ruff_version ${PYTHON_FILES}
	${POETRY} run ruff check --config ${RUFF_CONFIG_FILE} .

# when checking: first format, then lint
check_py: check_py_format check_py_lint
check_all: check_py_format check_py_lint 
check: check_py  ## Check Formatting and Lint


# ======================================================================
#* Cleaning
.PHONY: clean_checks_cache
clean_checks_cache:
	-rm -rf .ruff_cache

.PHONY: clean_tests_cache
clean_tests_cache:
	-rm -rf .pytest_cache
	-rm -rf .coverage

.PHONY: clean_pycache
clean_pycache:
	-find . -name "__pycache__" -type d -exec rm -rf {} +

echo_clean_cache:
	@echo "${INFO_MSG}: Cleaning cached data"
clean_cache:  ## Clean cached data
clean_cache: echo_clean_cache confirm_action clean_checks_cache clean_tests_cache clean_pycache

.PHONY: clean_logs
echo_clean_logs:  ## Clean log files
	@echo "${INFO_MSG}: Cleaning log files"
clean_tmp: echo_clean_logs
	-rm *.log

.PHONY: clean_venv
echo_clean_venv:
	@echo "${INFO_MSG}: Cleaning Virtual Environment from \`${MAGENTA}${VENV_DIR}${NORMAL}\`"
clean_venv: echo_clean_venv confirm_action  ## Clean Virtual Environment
	-rm -rf ${VENV_DIR}

.PHONY: clean_dotenv
echo_clean_dotenv:
	@echo "${INFO_MSG}: Cleaning \`${MAGENTA}${DOTENV_FILE}${NORMAL}\`"
clean_dotenv: echo_clean_dotenv confirm_action  ## Clean DOTENV file
	-rm -rf ${DOTENV_FILE}

.PHONY: clean_docker
clean_docker: confirm_action
	-${DOCKER} system prune --all --volumes --force

.PHONY: clean_all
echo_clean_all:
	@echo "${INFO_MSG}: Cleaning all byproduct files"
clean_all:  ## Clean all byproduct files
clean_all: echo_clean_all confirm_action clean_cache clean_tmp clean_venv clean_dotenv clean_img
