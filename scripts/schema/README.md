# BCA — BigQuery schema extractor

Dumps every table in a BigQuery dataset as machine-readable schema artefacts,
ready to be served as static files (e.g. behind `schemas.blockchain-applied.com`)
and discovered by AI agents. Designed for the
[Cardano_on_BigQuery](https://github.com/Blockchain-Data-Analytics/Cardano_on_BigQuery)
repo: drops files into `./schema/`, refreshed daily via GitHub Actions.

## What it produces, per table

| File              | Format                          | Audience                                      |
| ----------------- | ------------------------------- | --------------------------------------------- |
| `<table>.json`    | JSON Schema 2020-12             | LLMs / agents, validators, OpenAPI generation |
| `<table>.yaml`    | Same content, YAML              | Humans, fewer tokens for LLM context          |
| `<table>.bq.json` | Raw BigQuery `TableFieldSchema` | `bq mk --schema=…`, round-tripping            |
| `<table>.jsonld`  | `schema.org/Dataset` JSON-LD    | Crawlers, dataset search, SEO                 |

Plus a top-level `index.json` / `index.yaml` catalogue.

## Type mapping

| BigQuery       | JSON Schema                                                |
| -------------- | ---------------------------------------------------------- |
| `STRING`       | `string`                                                   |
| `BYTES`        | `string` + `contentEncoding: base64`                       |
| `INT64`        | `integer` + `format: int64`                                |
| `FLOAT64`      | `number` + `format: double`                                |
| `BOOL`         | `boolean`                                                  |
| `TIMESTAMP`    | `string` + `format: date-time`                             |
| `DATE`         | `string` + `format: date`                                  |
| `TIME`         | `string` + `format: time`                                  |
| `DATETIME`     | `string` + `format: date-time`                             |
| `NUMERIC`      | `string` + decimal pattern (precision-safe across clients) |
| `BIGNUMERIC`   | `string` + decimal pattern                                 |
| `JSON`         | any                                                        |
| `GEOGRAPHY`    | `string` (WKT/GeoJSON)                                     |
| `INTERVAL`     | `string`                                                   |
| `RECORD/STRUCT`| `object` with `additionalProperties: false`                |
| `REPEATED`     | wraps the above in an `array`                              |
| `NULLABLE`     | adds `"null"` to the `type` union                          |
| `REQUIRED`     | listed under the parent's `required`                       |

NUMERIC/BIGNUMERIC have arbitrary precision — there is no safe JSON number
representation, so we string-encode and add a regex. INT64 fits in JSON, but
JS clients silently lose precision past 2^53; we keep it as `integer` with
`format: int64` so strict consumers can opt into string-encoding.

## Local usage

```bash
pip install -r requirements.txt
gcloud auth application-default login

./run.sh
# or:
python3 extract_schemas.py \
    --project  blockchain-analytics-392322 \
    --dataset  cardano_mainnet \
    --base-url https://schemas.blockchain-applied.com/cardano \
    --out      ./schema
```

## CI: scheduled refresh on GitHub Actions

The workflow `.github/workflows/extract-schemas.yml`:

- runs daily at 06:00 UTC (well after Cardano epoch boundaries settle around 21:45 UTC)
- can also be triggered manually via the Actions tab with overrides for
  project, dataset, base URL, output directory, and commit mode
- re-runs on pushes that modify the extractor itself, as a smoke test
- writes results into `./schema/`
- by default opens a PR against `released` (you review the diff before merge);
  switch to `direct_commit` mode via workflow_dispatch input if you'd rather

### One-time auth setup (Workload Identity Federation)

Recommended over service-account keys — no long-lived secrets in GitHub.

```bash
# Run locally with gcloud authenticated as project IAM admin
bash setup-wif.sh
```

The script creates:
- A service account `schema-reader@blockchain-analytics-392322.iam.gserviceaccount.com`
- Dataset-scoped `roles/bigquery.metadataViewer` on `cardano_mainnet`
- A Workload Identity Pool + OIDC provider trusting **only** the
  `Blockchain-Data-Analytics` org via `attribute-condition`
- An IAM binding so only the `Cardano_on_BigQuery` repo can impersonate the SA

Then in GitHub → Settings → Secrets and variables → Actions → **Variables** tab,
add:
- `GCP_WORKLOAD_IDENTITY_PROVIDER` (printed by the setup script)
- `GCP_SERVICE_ACCOUNT` (also printed)

These are **variables**, not secrets — they're not sensitive; the security
boundary is the IAM binding on the SA, not the values themselves.

### Alternative: service-account JSON key

If WIF is overkill, generate a key for the same SA, store it as a repo
secret called `GCP_SA_KEY` (paste the whole JSON), and swap the auth step
in the workflow as commented in the YAML.

### Branch protection note

If `released` has branch protection requiring reviews from CODEOWNERS
(your repo has a `CODEOWNERS` file), the auto-PR will sit waiting for your
approval — that's the intended behaviour. The bot won't be able to
self-merge.

If you want commits to appear as "verified" in GitHub, the
`peter-evans/create-pull-request` action supports signed commits via a
GitHub App token; add an app, store its credentials as secrets, and pass
them as `token`. Optional, not required.

## Publishing on Ghost

Don't paste these files into Ghost posts — the editor will mangle them.
Serve them as static files from `schemas.blockchain-applied.com` (a tiny
nginx pod in your K3s cluster, same pattern as `bca-ghost`) with the right
content types:

```nginx
types {
    application/schema+json json;
    application/yaml        yaml;
    application/ld+json     jsonld;
}
add_header Access-Control-Allow-Origin "*" always;
add_header Cache-Control "public, max-age=300";
```

The nginx pod can mount the `schema/` directory directly from the GitHub
repo via a sidecar `git-sync` container, or you can build a CD step that
syncs to a GCS bucket and serves from there.

For agent discovery, add an `llms.txt` at the root of `blockchain-applied.com`
pointing at the index, and consider exposing `get_table_schema(table_name)`
through your existing MCP server at `mcp.blockchain-applied.com`.
