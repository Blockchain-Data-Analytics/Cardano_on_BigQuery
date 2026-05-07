#!/usr/bin/env python3
"""
Extract BigQuery schemas for every table in a dataset and emit:

  - <table>.json       JSON Schema (Draft 2020-12) for one row of the table
  - <table>.yaml       Same content, YAML serialization
  - <table>.bq.json    Raw BigQuery schema (TableFieldSchema list, useful for tooling)
  - <table>.jsonld     schema.org/Dataset JSON-LD block
  - index.json         Catalogue of all tables with metadata + links
  - index.yaml         Same, YAML

Usage:
    export GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa.json   # or use ADC
    python extract_schemas.py \
        --project blockchain-analytics-392322 \
        --dataset cardano_mainnet \
        --base-url https://schemas.blockchain-applied.com/cardano \
        --out ./out

The script is idempotent: re-running rewrites the output dir.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from google.cloud import bigquery


# ---------------------------------------------------------------------------
# BigQuery -> JSON Schema type mapping
# ---------------------------------------------------------------------------
#
# References:
#   https://cloud.google.com/bigquery/docs/reference/standard-sql/data-types
#   https://json-schema.org/draft/2020-12/json-schema-validation
#
# Notes on the awkward ones:
#   - INT64 fits in a JSON number, but JS clients lose precision past 2^53.
#     We type it as integer and add `format: int64` so consumers can opt in
#     to string-encoding if they need it.
#   - NUMERIC / BIGNUMERIC have arbitrary precision -> string + numeric pattern.
#   - BYTES are base64-encoded in JSON output by BigQuery.
#   - GEOGRAPHY is WKT/GeoJSON; we keep it as string and let consumers parse.
#   - JSON columns are passed through (any JSON value allowed).

_PRIMITIVE_MAP: dict[str, dict[str, Any]] = {
    "STRING":     {"type": "string"},
    "BYTES":      {"type": "string", "contentEncoding": "base64"},
    "INTEGER":    {"type": "integer", "format": "int64"},
    "INT64":      {"type": "integer", "format": "int64"},
    "FLOAT":      {"type": "number", "format": "double"},
    "FLOAT64":    {"type": "number", "format": "double"},
    "BOOLEAN":    {"type": "boolean"},
    "BOOL":       {"type": "boolean"},
    "TIMESTAMP":  {"type": "string", "format": "date-time"},
    "DATETIME":   {"type": "string", "format": "date-time"},
    "DATE":       {"type": "string", "format": "date"},
    "TIME":       {"type": "string", "format": "time"},
    "NUMERIC":    {"type": "string", "pattern": r"^-?\d+(\.\d+)?$",
                   "description": "BigQuery NUMERIC (38 digits, 9 fractional)"},
    "BIGNUMERIC": {"type": "string", "pattern": r"^-?\d+(\.\d+)?$",
                   "description": "BigQuery BIGNUMERIC (76.76 digits)"},
    "GEOGRAPHY":  {"type": "string",
                   "description": "WKT or GeoJSON; BigQuery GEOGRAPHY"},
    "JSON":       {},  # any JSON value
    "INTERVAL":   {"type": "string",
                   "description": "ISO-8601-ish BigQuery INTERVAL"},
}


def _field_to_json_schema(field: bigquery.SchemaField) -> dict[str, Any]:
    """Convert a single BigQuery SchemaField to a JSON Schema fragment."""
    field_type = field.field_type.upper()

    if field_type in ("RECORD", "STRUCT"):
        props: dict[str, Any] = {}
        required: list[str] = []
        for sub in field.fields:
            props[sub.name] = _field_to_json_schema(sub)
            if sub.mode == "REQUIRED":
                required.append(sub.name)
        node: dict[str, Any] = {
            "type": "object",
            "properties": props,
            "additionalProperties": False,
        }
        if required:
            node["required"] = required
    else:
        node = dict(_PRIMITIVE_MAP.get(field_type, {"type": "string"}))
        # Annotate unknown types so consumers can see what we received
        if field_type not in _PRIMITIVE_MAP:
            node["x-bigquery-type"] = field_type

    if field.description:
        # Don't clobber a description we set from the type map unless BQ has one
        node["description"] = field.description

    # Modes: NULLABLE (default), REQUIRED, REPEATED
    if field.mode == "REPEATED":
        return {
            "type": "array",
            "items": node,
            **({"description": field.description} if field.description else {}),
        }

    if field.mode == "NULLABLE":
        # Allow null in addition to the declared type. We use the
        # `["type", "null"]` form rather than `nullable: true` (OpenAPI-ism)
        # for strict JSON Schema compliance.
        if "type" in node and isinstance(node["type"], str):
            node["type"] = [node["type"], "null"]

    return node


def table_to_json_schema(
    table: bigquery.Table,
    base_url: str,
) -> dict[str, Any]:
    """Build a JSON Schema document describing ONE ROW of the table."""
    properties: dict[str, Any] = {}
    required: list[str] = []
    for field in table.schema:
        properties[field.name] = _field_to_json_schema(field)
        if field.mode == "REQUIRED":
            required.append(field.name)

    schema_id = f"{base_url.rstrip('/')}/{table.table_id}.json"
    doc: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": schema_id,
        "title": f"{table.dataset_id}.{table.table_id}",
        "description": table.description or
            f"Row schema for {table.project}.{table.dataset_id}.{table.table_id}",
        "type": "object",
        "properties": properties,
        "additionalProperties": False,
    }
    if required:
        doc["required"] = required

    # Useful BigQuery-specific metadata, namespaced under x-bigquery
    doc["x-bigquery"] = {
        "project":      table.project,
        "dataset":      table.dataset_id,
        "table":        table.table_id,
        "full_id":      f"{table.project}.{table.dataset_id}.{table.table_id}",
        "type":         table.table_type,    # TABLE / VIEW / MATERIALIZED_VIEW
        "num_rows":     table.num_rows,
        "num_bytes":    table.num_bytes,
        "created":      _iso(table.created),
        "modified":     _iso(table.modified),
        "labels":       dict(table.labels) if table.labels else {},
        "partitioning": _partitioning(table),
        "clustering":   list(table.clustering_fields or []),
    }
    return doc


def table_to_jsonld(
    table: bigquery.Table,
    base_url: str,
) -> dict[str, Any]:
    """Build a schema.org/Dataset JSON-LD document for the table."""
    full_id = f"{table.project}.{table.dataset_id}.{table.table_id}"
    schema_url = f"{base_url.rstrip('/')}/{table.table_id}.json"
    return {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": full_id,
        "alternateName": table.table_id,
        "description": table.description or
            f"BigQuery table {full_id}",
        "identifier": full_id,
        "url": schema_url,
        "isAccessibleForFree": False,
        "creator": {
            "@type": "Organization",
            "name": "BCA — Blockchain Applied",
            "url":  "https://blockchain-applied.com",
        },
        "distribution": [
            {
                "@type": "DataDownload",
                "encodingFormat": "application/schema+json",
                "contentUrl": f"{base_url.rstrip('/')}/{table.table_id}.json",
            },
            {
                "@type": "DataDownload",
                "encodingFormat": "application/yaml",
                "contentUrl": f"{base_url.rstrip('/')}/{table.table_id}.yaml",
            },
        ],
        "variableMeasured": [
            {
                "@type": "PropertyValue",
                "name": f.name,
                "description": f.description or "",
                "unitText": f.field_type,
            }
            for f in _flatten_fields(table.schema)
        ],
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def _partitioning(table: bigquery.Table) -> dict[str, Any] | None:
    if table.time_partitioning:
        tp = table.time_partitioning
        return {
            "kind":           "TIME",
            "type":           tp.type_,         # DAY / HOUR / MONTH / YEAR
            "field":          tp.field,
            "expiration_ms":  tp.expiration_ms,
            "require_filter": tp.require_partition_filter,
        }
    if table.range_partitioning:
        rp = table.range_partitioning
        return {
            "kind":  "RANGE",
            "field": rp.field,
            "range": {
                "start":    rp.range_.start,
                "end":      rp.range_.end,
                "interval": rp.range_.interval,
            },
        }
    return None


def _flatten_fields(
    fields: list[bigquery.SchemaField],
    prefix: str = "",
) -> list[bigquery.SchemaField]:
    """Flatten nested RECORDs to dotted paths for the JSON-LD variableMeasured."""
    out: list[bigquery.SchemaField] = []
    for f in fields:
        name = f"{prefix}{f.name}"
        if f.field_type.upper() in ("RECORD", "STRUCT") and f.fields:
            out.append(bigquery.SchemaField(
                name=name, field_type=f.field_type, mode=f.mode,
                description=f.description, fields=(),
            ))
            out.extend(_flatten_fields(list(f.fields), prefix=f"{name}."))
        else:
            out.append(bigquery.SchemaField(
                name=name, field_type=f.field_type, mode=f.mode,
                description=f.description,
            ))
    return out


def _bq_schema_raw(fields: list[bigquery.SchemaField]) -> list[dict[str, Any]]:
    """Faithful round-trippable BigQuery schema dump."""
    return [f.to_api_repr() for f in fields]


def _write(path: Path, data: Any, fmt: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "json":
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    elif fmt == "yaml":
        path.write_text(yaml.safe_dump(
            data, sort_keys=False, allow_unicode=True, width=100,
        ))
    else:
        raise ValueError(f"Unknown format {fmt}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", required=True)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--base-url", required=True,
                    help="Public URL prefix where these schemas will live, "
                         "e.g. https://schemas.blockchain-applied.com/cardano")
    ap.add_argument("--out", default="./out", type=Path)
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    client = bigquery.Client(project=args.project)
    dataset_ref = bigquery.DatasetReference(args.project, args.dataset)

    tables = list(client.list_tables(dataset_ref))
    if not tables:
        print(f"No tables found in {args.project}.{args.dataset}",
              file=sys.stderr)
        return 1

    index: list[dict[str, Any]] = []

    for tbl_ref in tables:
        table = client.get_table(tbl_ref.reference)
        full_id = f"{table.project}.{table.dataset_id}.{table.table_id}"
        print(f"  · {full_id}  ({table.table_type})", file=sys.stderr)

        json_schema = table_to_json_schema(table, args.base_url)
        jsonld      = table_to_jsonld(table, args.base_url)
        bq_raw      = _bq_schema_raw(list(table.schema))

        stem = args.out / table.table_id
        _write(stem.with_suffix(".json"),     json_schema, "json")
        _write(stem.with_suffix(".yaml"),     json_schema, "yaml")
        _write(stem.with_suffix(".bq.json"),  bq_raw,      "json")
        _write(stem.with_suffix(".jsonld"),   jsonld,      "json")

        index.append({
            "name":        table.table_id,
            "full_id":     full_id,
            "type":        table.table_type,
            "description": table.description,
            "num_rows":    table.num_rows,
            "num_bytes":   table.num_bytes,
            "modified":    _iso(table.modified),
            "links": {
                "json_schema": f"{args.base_url.rstrip('/')}/{table.table_id}.json",
                "yaml":        f"{args.base_url.rstrip('/')}/{table.table_id}.yaml",
                "bq_schema":   f"{args.base_url.rstrip('/')}/{table.table_id}.bq.json",
                "jsonld":      f"{args.base_url.rstrip('/')}/{table.table_id}.jsonld",
            },
        })

    catalogue = {
        "project":      args.project,
        "dataset":      args.dataset,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_url":     args.base_url,
        "table_count":  len(index),
        "tables":       index,
    }
    _write(args.out / "index.json", catalogue, "json")
    _write(args.out / "index.yaml", catalogue, "yaml")

    print(f"\nWrote {len(index)} tables to {args.out}/", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
