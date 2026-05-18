# syntax=docker/dockerfile:1.7
#
# Builds the static-file image for
#   https://schemas.blockchain-applied.com/cardano_on_bigquery
#
# The extractor runs as a build step. The GCP service-account key is passed
# in as a BuildKit *secret* — it is never written to a layer. The generated
# JSON/YAML files are baked into the final image.
#
# Build (single arch, local):
#
#     DOCKER_BUILDKIT=1 docker build \
#         --secret id=gcp_key,src=$HOME/.config/gcloud/bca-schema-reader.json \
#         -t bca/schemas-cardano:latest .
#
# The path you pass to --secret must be a real file on the host. Inside the
# build the secret is mounted at /run/secrets/gcp_key and we point
# GOOGLE_APPLICATION_CREDENTIALS at it.
#
# Multi-arch + push:
#
#     docker buildx build \
#         --platform linux/amd64,linux/arm64 \
#         --secret id=gcp_key,src=$HOME/.config/gcloud/bca-schema-reader.json \
#         -t registry.blockchain-applied.com/bca/schemas-cardano:$(git rev-parse --short HEAD) \
#         --push .
#
# CI: pass the secret via an env var instead of a file:
#
#     echo "$GCP_SA_KEY" | docker buildx build \
#         --secret id=gcp_key,env=GCP_SA_KEY \
#         ...
#
# restart: kubectl rollout restart deployment/schemas-cardano-bq -n bca-schemas


ARG  PYTHON_VERSION=3.12
ARG  NGINX_VERSION=1.27
ARG  BASE_URL=https://schemas.blockchain-applied.com/cardano_on_bigquery
ARG  GCP_PROJECT=blockchain-analytics-392322
ARG  BQ_DATASET=cardano_mainnet


# ─── Stage 1: extract schemas from BigQuery ─────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS extract

# Re-declare ARGs that this stage needs (Dockerfile scoping rule)
ARG BASE_URL
ARG GCP_PROJECT
ARG BQ_DATASET

WORKDIR /work

# Install only what's needed to run the extractor.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY extract_schemas.py ./

# Run the extractor with the SA key mounted as a BuildKit secret.
# `--mount=type=secret` exposes /run/secrets/gcp_key inside this RUN only;
# the file does not appear in any layer of the resulting image.
RUN --mount=type=secret,id=gcp_key,target=/run/secrets/gcp_key,required=true \
    GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/gcp_key \
    python extract_schemas.py \
        --project  "${GCP_PROJECT}" \
        --dataset  "${BQ_DATASET}" \
        --base-url "${BASE_URL}" \
        --out      /out/cardano_on_bigquery

# Sanity check: index.json must exist, otherwise the extraction silently
# produced nothing and we'd ship an empty image.
RUN test -f /out/cardano_on_bigquery/index.json && \
    echo "Generated $(find /out/cardano_on_bigquery -type f | wc -l) schema files:" && \
    ls /out/cardano_on_bigquery | head -20


# ─── Stage 2: final nginx image ─────────────────────────────────────────────
FROM nginxinc/nginx-unprivileged:${NGINX_VERSION}-alpine

ARG BASE_URL
ARG GCP_PROJECT
ARG BQ_DATASET

LABEL org.opencontainers.image.title="BCA schemas — Cardano on BigQuery"
LABEL org.opencontainers.image.description="Static JSON Schema, YAML and JSON-LD descriptors for the cardano_mainnet BigQuery dataset"
LABEL org.opencontainers.image.url="${BASE_URL}"
LABEL org.opencontainers.image.source="https://github.com/Blockchain-Data-Analytics/Cardano_on_BigQuery"
LABEL org.opencontainers.image.vendor="BCA — Blockchain Applied"
LABEL org.opencontainers.image.licenses="Apache-2.0"
LABEL bca.gcp-project="${GCP_PROJECT}"
LABEL bca.bq-dataset="${BQ_DATASET}"

# nginx config
USER root
RUN rm /etc/nginx/conf.d/default.conf
COPY --chown=101:101 schemas.conf /etc/nginx/conf.d/schemas.conf
COPY --chown=101:101 favicon.ico  /usr/share/nginx/html/favicon.ico
COPY --chown=101:101 index.html   /usr/share/nginx/html/index.html
COPY --chown=101:101 fonts/       /usr/share/nginx/html/fonts/

USER 101
# Schemas, generated in stage 1
COPY --from=extract --chown=101:101 /out/ /usr/share/nginx/html/

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost:8080/healthz || exit 1
