ifndef _DOCKER_MAKEFILE
_DOCKER_MAKEFILE = 1  # Define a variable to mark inclusion


# Common Definitions
include Makefile.common.mk

# ======================================================================
#* Files and dirs
DOCKERFILE := Dockerfile
DOCKERFILE_FILES := $(wildcard $(shell find . -not -path '*/\.*' -name '*Dockerfile*'))
DOCKER_IMAGE := docker-image
DOCKER_INSTANCE := docker-instance


# ======================================================================
#* Tools
DOCKER := docker


# ======================================================================
#* Automatic Fix and Check (Linter, Formatting)
#** Automatic fixing
fix_docker_lint: ${DOCKERFILE_FILES}
	@echo "${WARN_MSG}: Docker linter not installed"

fix_docker_format: ${DOCKERFILE_FILES}
	@echo "${WARN_MSG}: Docker formatter not installed"

# when fixing: first lint, then format
fix_docker: fix_docker_lint fix_docker_format

#** Checking only
check_docker_format: ${DOCKERFILE_FILES}
	@echo "${WARN_MSG}: Docker formatter not installed"

check_docker_lint: ${DOCKERFILE_FILES}
	@echo "${WARN_MSG}: Docker linter not installed"

# when checking: first format, then lint
check_docker: check_docker_format check_docker_lint


# ======================================================================
#* Containers Management (with Docker)
build_img: ${DOCKERFILE}
	${DOCKER} build \
		--file ${DOCKERFILE} \
		--tag ${DOCKER_IMAGE} \
		.

stop_img: export IMAGES=$(shell docker ps -aq --filter ancestor=${DOCKER_IMAGE})
stop_img:
	@echo "${INFO_MSG}: Stopping \`${YELLOW}${DOCKER_IMAGE}${NORMAL}\` Docker image(s)"
	@if [ -n "${IMAGES}" ]; then \
		echo "${INFO_MSG}: Stopping Docker image(s): \`${MAGENTA}${IMAGES}${NORMAL}\`"; \
		${DOCKER} stop ${IMAGES}; \
	fi

.PHONY: run_img_sh
run_img_sh: ${DOTENV_FILE} build_img
	${DOCKER} run --interactive --tty --rm --volume .:/app --name $(DOCKER_INSTANCE) $(DOCKER_IMAGE) /bin/bash

.PHONY: run_img
run_img: ${DOTENV_FILE} build_img
	${DOCKER} run --volume .:/app $(DOCKER_IMAGE)


# ======================================================================
#* Cleaning
.PHONY: clean_docker
clean_docker: confirm_action
	-${DOCKER} system prune --all --volumes --force --filter "label=${DOCKER_IMAGE}"

.PHONY: clean_all_docker
clean_all_docker: confirm_action
	-${DOCKER} system prune --all --volumes --force


# ======================================================================
# ifndef _DOCKER_MAKEFILE
endif
