# BCA — BigQuery schema extractor

Dumps every table in a BigQuery dataset as machine-readable schema artefacts,
ready to be served as static files on `schemas.blockchain-applied.com`
and discovered by AI agents. Designed for the
[Cardano_on_BigQuery](https://github.com/Blockchain-Data-Analytics/Cardano_on_BigQuery)
repo.

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
