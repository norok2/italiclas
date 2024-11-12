#* Config
include Makefile.common.mk
include Makefile.py.mk
include Makefile.docker.mk
export UNIQUE_MAKEFILES := $(shell echo $(MAKEFILE_LIST) | tr ' ' '\n' | sort -u | tr '\n' ' ')


#** Project
export PROJECT_NAME := $(shell ${PYTHON} -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['tool']['poetry']['name'])")
export PROJECT_SLUG := $(subst _,-,${PROJECT_NAME})

export DOCKER_IMAGE := ${PROJECT_SLUG}-image
export DOCKER_INSTANCE := ${PROJECT_SLUG}-instance

export PKG_DIR := ${PROJECT_NAME}
export API_HOST ?= 0.0.0.0
export API_PORT ?= 5000
export API_TIMEOUT ?= 6
export API_NUM_WORKERS ?= 4
export TEST_API_HOST ?= http://localhost
export TEST_API_PORT ?= 5000


.DEFAULT_GOAL: help


# ======================================================================
#* Run
.PHONY: run
run: run_api  ## Run containerized app


# ======================================================================
#* Installation
.PHONY: install
install: poetry_setup install_py  ## Install local execution environment
.PHONY: uninstall
uninstall: clean_venv  ## Uninstall local execution environment


# ======================================================================
#* More Execution
.PHONY: exec
exec: exec_api  ## Execute app locally
.PHONY: sh
sh: run_img_sh  # Run a shell inside the container


# ======================================================================
#* Automatic Fix and Check (Linter, Formatting)
.PHONY: fix
fix: ${VENV_DIR} fix_py fix_docker  ## Fix style and formatting

.PHONY: check
check: ${VENV_DIR} check_py check_docker  ## Check style and formatting


# ======================================================================
#* Test & Coverage
.PHONY: test
test: ${VENV_DIR} test_py  ## Run unit tests

.PHONY: coverage
coverage: ${VENV_DIR} coverage_py  ## Display Code Coverage report


# ======================================================================
#* Continuous Integration (CI)
.PHONY: ci
ci: check fix test coverage  ## Continuous Integration (CI)


# ======================================================================
#* Local Run
#** API
.PHONY: exec_api
# exec_api: export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
exec_api:  # Run API locally
	${POETRY} run uvicorn \
		--workers ${API_NUM_WORKERS} \
		--host ${API_HOST} \
		--port ${API_PORT} \
		--timeout-keep-alive ${API_TIMEOUT} \
		--reload \
		${PROJECT_NAME}.api.main:app


.PHONY: test_load_api
test_load_api:
	${POETRY} run locust --locustfile locustfile.py --host ${TEST_API_HOST}:${TEST_API_PORT}


# ======================================================================
#* Docker Run
.PHONY: run_api
run_api: ${DOTENV_FILE} build_img  # Run API from Docker image
	${DOCKER} run \
		--publish $(API_PORT):$(API_PORT) \
		--volume ./${DOTENV_FILE}:/app/${DOTENV_FILE}:ro \
		--volume ./artifacts:/app/artifacts:rw \
		--env GIT_COMMIT_SHA1=${GIT_COMMIT_SHA1} \
		$(DOCKER_IMAGE)


# ======================================================================
#* Cleaning
.PHONY: clean
clean:  ## Clean temporary files
clean: clean_common clean_py clean_docker

.PHONY: clean_all
clean_all:  ## Clean all files (use with caution!)
clean_all: echo_clean_dotenv echo_clean_venv clean_all_common clean_all_py clean_all_docker

# ======================================================================
#* Misc
update_env_vars: \
		update_env_var_JWT_KEY

update_env_var_JWT_KEY: confirm_action
	@$(call update_var_from_stdin,${DOTENV_FILE},API_KEY)


openapi.yaml: ${PYTHON_FILES}
	${POETRY} run src/${PKG_DIR}/api/gen_openapi.py
