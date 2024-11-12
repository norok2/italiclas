ifndef _COMMON_MAKEFILE
_COMMON_MAKEFILE = 1  # Define a variable to mark inclusion


# Common Definitions

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
# to be synced with other sources of truth
export TEMP_PATH ?= tmp_dir
export DOTENV_FILE ?= .env
export GIT_COMMIT_SHA1 ?= $(shell git rev-parse HEAD)
export UNIQUE_MAKEFILES := $(shell echo $(MAKEFILE_LIST) | tr ' ' '\n' | sort -u | tr '\n' ' ')


# ======================================================================
#* Display Help
# To display in `help` the target line must contain a comment starting with ##
.PHONY: help
help:  ## Display this help
	@echo "Please use \`${MAGENTA}make ${CYAN}<target>${NORMAL}\` where ${CYAN}<target>${NORMAL} is one of:"
	@grep -E '^[a-zA-Z0-9_\.\-\%]+\: .*?## .*$$' ${UNIQUE_MAKEFILES} | sed 's/^[^:]*://' | awk 'BEGIN {FS = ":.*?##"} {printf "${CYAN}%-24s${NORMAL} %s\n", $$1, $$2}'


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
		[ "$${IS_BREAKING}" -eq 0 ] && (echo -n "${WARN_MSG}") || (echo -n "${ERR_MSG}"); \
		echo ": ${YELLOW}$${VAR_NAME}${NORMAL} is empty"; \
		([ "$${IS_BREAKING}" -eq 0 ] && (true) || (exit 1)); \
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
		[ "$${IS_BREAKING}" -eq 0 ] && (echo -n "${WARN_MSG}") || (echo -n "${ERR_MSG}"); \
		echo ": ${YELLOW}$${VAR_NAME}${NORMAL}=\"${GREEN}$${VALUE}${NORMAL}\" NOT in allowlist"; \
		([ "$${IS_BREAKING}" -eq 0 ] && (true) || (exit 1)); \
	fi
endef

#** Check if file exists
define check_file_exists  # (FILE_PATH,IS_BREAKING) -> NULL
	@FILE_PATH=$(1); \
	IS_BREAKING=$(2); \
	if [ -f "$${FILE_PATH}" ]; then \
		echo "${INFO_MSG}: \`${MAGENTA}$${FILE_PATH}${NORMAL}\` found"; \
	else \
		[ "$${IS_BREAKING}" -eq 0 ] && (echo -n "${WARN_MSG}") || (echo -n "${ERR_MSG}"); \
		echo ": \`${MAGENTA}$${FILE_PATH}${NORMAL}\` NOT found"; \
		([ "$${IS_BREAKING}" -eq 0 ] && (true) || (exit 1)); \
	fi
endef


# ======================================================================
#* DotEnv Management
define update_var  # (VAR_FILE,VAR_NAME,VAR_VALUE) -> NULL
	@echo "${INFO_MSG}: Update \`${MAGENTA}$(1)${NORMAL}\` with \`${YELLOW}$(2)${NORMAL}=\"${GREEN}$(3)${NORMAL}\"\` (was \`${YELLOW}$(2)${NORMAL}=\"${GREEN}`grep '^$(2)=' $(1) | sed 's/^$(2)=//' | tr -d '"'`${NORMAL}\"\`)"
    @read -r -p "Proceed? (${GREEN}y${NORMAL}/${RED}N${NORMAL}) " CONFIRM; \
    if [ "$$CONFIRM" = "y" ]; then \
        ([ -f $(1) ] && grep -q '^$(2)=' $(1) && (sed 's/^$(2)=.*/$(2)="$(3)"/' $(1) > $(1).tmp && mv $(1).tmp $(1))) || echo '$(2)="$(3)"' >> $(1); echo "Updated ${GREEN}confirmed${NORMAL}."; \
    else \
        echo "Update ${YELLOW}cancelled${NORMAL}."; \
    fi
endef

define update_var_from_stdin  # (VAR_FILE,VAR_NAME) -> NULL
    $(call update_var,$(1),$(2),$(shell read -r -p "New value for $(2) = " VAR && echo $$VAR))
endef

.PHONY: init_dotenv
init_dotenv: .env.dev
	-cp --interactive .env.dev .env

.PHONY: dotenv
echo_dotenv:
	@echo "${INFO_MSG}: Populate the \`${MAGENTA}${DOTENV_FILE}${NORMAL}\`" file content
dotenv:  # Populate the DOTENV_FILE content
dotenv: \
		echo_dotenv \
		confirm_action \
		init_dotenv \
		update_env_vars
	@echo "${INFO_MSG}: Please use \`${CYAN}${BOLD}cat ${DOTENV_FILE}${NORMAL}\` to inspect the content of the file."

${DOTENV_FILE}:
	$(MAKE) dotenv

echo_update_env_var_%:
	@echo "${INFO_MSG}: Update \`${YELLOW}$*${NORMAL}\` on \`${MAGENTA}${DOTENV_FILE}${NORMAL}\`"


# ======================================================================
#* Cleaning
.PHONY: clean_logs
echo_clean_logs:
	@echo "${INFO_MSG}: Cleaning log files"
clean_logs: echo_clean_logs
	-rm *.log

.PHONY: clean_dotenv
echo_clean_dotenv:
	@echo "${WARN_MSG}: Cleaning \`${MAGENTA}${DOTENV_FILE}${NORMAL}\`"
clean_dotenv: echo_clean_dotenv confirm_action  # Clean DOTENV file
	-rm -rf ${DOTENV_FILE}

.PHONY: clean_common
echo_clean_common:
	@echo "${INFO_MSG}: Cleaning common files"
clean_common: echo_clean_common confirm_action clean_logs

.PHONY: clean_all_common
echo_clean_all_common:
	@echo "${INFO_MSG}: Cleaning all common files"
clean_all_common: echo_clean_all_common confirm_action clean_logs clean_dotenv


# ======================================================================
# ifndef _COMMON_MAKEFILE
endif
