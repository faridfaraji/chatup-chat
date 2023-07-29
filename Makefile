# Project configuration
PROJECT_NAME = chatup-chat
DOCKER_REGISTRY_REPO = northamerica-northeast1-docker.pkg.dev/iron-burner-389219/awesoon

# General Parameters
TOPDIR = $(shell git rev-parse --show-toplevel)
CONDA_SH := $(shell find ~/*conda*/etc -name conda.sh | tail -1)
ACTIVATE := source $(CONDA_SH) && conda activate $(PROJECT_NAME)
ifeq ($(shell uname -p), arm)
DOCKER_PLATFORM = --platform linux/amd64
else
DOCKER_PLATFORM =
endif

default: help

help: # Display help
	@awk -F ':|##' \
		'/^[^\t].+?:.*?##/ {\
			printf "\033[36m%-30s\033[0m %s\n", $$1, $$NF \
		}' $(MAKEFILE_LIST) | sort

run-local: ## run locally the service on default port 500
	cd $(TOPDIR) && \
	python chatup_chat/chat.py

run: ## Run the service with gunicorn
	cd $(TOPDIR) && \
	FLASK_APP=chatup_chat.chat \
	./entrypoint.sh

build-docker: ## Build the docker image
	docker build $(DOCKER_PLATFORM) -t $(PROJECT_NAME) .

tag-docker: ## Tag the docker image
	docker tag $(PROJECT_NAME) $(DOCKER_REGISTRY_REPO)/$(PROJECT_NAME):latest

push-docker: ## push the image to registry
	docker push $(DOCKER_REGISTRY_REPO)/$(PROJECT_NAME):latest

run-docker: ## Run the docker image
	@docker-compose -f deploy/docker_compose/docker-compose.dev.yaml up

stop-docker: # Stop and remove containers and networks
	@docker-compose -f deploy/docker_compose/docker-compose.dev.yaml down

test: ## Run tox
	tox

clean-code: ## Remove unwanted files in this project (!DESTRUCTIVE!)
	@cd $(TOPDIR) && git clean -ffdx && git reset --hard

clean-docker: ## Remove all docker artifacts for this project (!DESTRUCTIVE!)
	@docker image rm -f $(shell docker image ls --filter reference='$(DOCKER_REPO)' -q) || true

setup: ## Setup the full environment (default)
	conda env update -f environment.yml

setup-mamba: ## Setup the full environment (default)
	mamba env update -f environment.yml

release-publish: ## push release to git after git flow release publish
	git checkout main
	git push
	git checkout develop
	git push
	git push --tags

.PHONY: default debug help start start-dev build-docker run-docker stop-docker test clean-code clean-docker code setup release-publish
