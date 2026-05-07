# Build and publish the schemas-cardano-bq image.
#
# The build runs extract_schemas.py inside a builder stage, so the resulting
# image always contains the latest schema. The GCP service-account key is
# passed in via a BuildKit secret mount and is never written to a layer.
#
# Usage:
#   make build                                # local single-arch build
#   make run                                  # run locally on :8080
#   make smoke                                # curl a few endpoints
#   make push                                 # multi-arch buildx + push
#
# Override on the command line as needed:
#   make build SA_KEY=/path/to/key.json TAG=v1.2.3
#   make push  REGISTRY=ghcr.io/blockchain-data-analytics

REGISTRY ?= code.blockchain-applied.com/bca
IMAGE    ?= schemas-cardano-bq
TAG      ?= $(shell git rev-parse --short HEAD 2>/dev/null || echo dev)
FULL     := $(REGISTRY)/$(IMAGE):$(TAG)
LATEST   := $(REGISTRY)/$(IMAGE):latest

# Path to the GCP service-account key. Override with SA_KEY=... on the CLI.
SA_KEY    ?= $(HOME)/.config/gcloud/bca-schema-reader.json

# Build args
BASE_URL    ?= https://schemas.blockchain-applied.com/cardano_on_bigquery
GCP_PROJECT ?= blockchain-analytics-392322
BQ_DATASET  ?= cardano_mainnet

# Multi-arch targets
PLATFORMS ?= linux/amd64,linux/arm64

# Common build args, expanded into --build-arg flags
BUILD_ARGS := \
	--build-arg BASE_URL=$(BASE_URL) \
	--build-arg GCP_PROJECT=$(GCP_PROJECT) \
	--build-arg BQ_DATASET=$(BQ_DATASET)

.PHONY: help check-key build run smoke push clean

help:
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

check-key:
	@test -f "$(SA_KEY)" || \
	  (echo "ERROR: SA key not found at $(SA_KEY)"; \
	   echo "       Set SA_KEY=/path/to/key.json or place the key at the default path."; \
	   exit 1)

build: check-key ## Build for the local arch only
	DOCKER_BUILDKIT=1 docker build \
		$(BUILD_ARGS) \
		--secret id=gcp_key,src=$(SA_KEY) \
		-t $(IMAGE):$(TAG) \
		-t $(IMAGE):latest \
		.

run: ## Run locally on http://localhost:8080
	docker run --rm -p 8080:8080 --name $(IMAGE) $(IMAGE):latest

smoke: ## Hit the running container and check headers
	@echo "Testing http://localhost:8080 ..."
	@curl -sS -o /dev/null -w "GET /healthz                                  → %{http_code}\n" http://localhost:8080/healthz
	@curl -sS -o /dev/null -w "GET /                                         → %{http_code} (302 expected)\n" http://localhost:8080/
	@curl -sS -o /dev/null -w "GET /cardano_on_bigquery/index.json           → %{http_code}\n" http://localhost:8080/cardano_on_bigquery/index.json
	@curl -sS -o /dev/null -w "GET /cardano_on_bigquery/missing.json         → %{http_code} (404 expected)\n" http://localhost:8080/cardano_on_bigquery/missing.json
	@echo
	@echo "Content-Type checks:"
	@curl -sSI http://localhost:8080/cardano_on_bigquery/index.json | grep -i '^content-type' || true

push: check-key ## Multi-arch build and push
	docker buildx build \
		--platform $(PLATFORMS) \
		$(BUILD_ARGS) \
		--secret id=gcp_key,src=$(SA_KEY) \
		-t $(FULL) \
		-t $(LATEST) \
		--push \
		.
	@echo "Pushed: $(FULL)"
	@echo "        $(LATEST)"

clean: ## Remove local images
	-docker rmi $(IMAGE):$(TAG) $(IMAGE):latest 2>/dev/null
