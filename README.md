
<img src="https://github.com/Blockchain-Data-Analytics.png" alt="BCA Blockchain Applied" width="80"/>

# Cardano on BigQuery

Full Cardano mainnet on-chain data, fully verified and continuously synced from [cardano-db-sync](https://github.com/IntersectMBO/cardano-db-sync) into Google BigQuery for analytics at scale.

## Access

**Dataset is private since January 1, 2025.**

- **5-day free trial** available — no commitment required
- Subscribe or start your trial: [blockchain-applied.com/bca-cardano-on-bigquery](https://www.blockchain-applied.com/bca-cardano-on-bigquery/)
- Questions: [info@blockchain-applied.com](mailto:info@blockchain-applied.com)

## Dataset

**Project:** `blockchain-analytics-392322`  
**Dataset:** `cardano_mainnet`

[Open in BigQuery Console](https://console.cloud.google.com/bigquery?project=blockchain-analytics-392322&ws=!1m4!1m3!3m2!1sblockchain-analytics-392322!2scardano_mainnet)

## What's in the dataset

~30 tables covering the full on-chain history:

| Category | Tables |
|---|---|
| Chain | `block`, `block_hash`, `schema_version`, `meta` |
| Transactions | `tx`, `tx_hash`, `tx_in_out`, `tx_consumed_output`, `tx_metadata` |
| UTxOs | `rel_addr_txout`, `rel_stake_txout`, `rel_stake_hash`, `collateral` |
| Multi-assets | `ma_minting` |
| Scripts & Datums | `script`, `datum`, `redeemer` |
| Staking | `stake_registration`, `stake_deregistration`, `delegation`, `reward`, `reward_addr`, `reward_pool`, `withdrawal` |
| Pools | `pool_update`, `pool_retire`, `pool_owner`, `pool_offline_data` |
| Epochs | `epoch_stake`, `epoch_stake_addr`, `epoch_stake_pool`, `epoch_param`, `ada_pots`, `param_proposal`, `cost_model` |

Table schemas (BigQuery JSON format) are in [`schema/tables/`](./schema/tables/).

## Schema API for AI agents

Machine-readable schemas are published at **[schemas.blockchain-applied.com](https://schemas.blockchain-applied.com/)** to support AI-assisted query writing. Feed the schema endpoint to your LLM or agent to generate accurate BigQuery SQL against this dataset without manual schema lookup.

## Repository contents

- [`schema/`](./schema/)
  - [`tables/`](./schema/tables/) — BigQuery table schemas (JSON)
  - [`views/`](./schema/views/) — SQL views over db-sync Postgres for comparison
- [`scripts/`](./scripts/)
  - `update_*.sh` — Slot-level sync: db-sync → BigQuery
  - `update_epoch_*.sh` — Epoch-level sync
  - `export_*.sh` — Bulk backfill scripts
  - `run_bq_update.sh` — Aggregate updater (all slot-level tables)
  - `run_update_epoch.sh` — Aggregate updater (all epoch-level tables)
  - [`deep_compare/`](./scripts/deep_compare/) — Hash-based validation: BigQuery vs db-sync
- [`deployment/`](./deployment/)
  - [`bq-updater/`](./deployment/bq-updater/) — Kubernetes deployment for continuous sync
  - [`bq-deep-check/`](./deployment/bq-deep-check/) — Kubernetes deployment for validation

## Data pipeline

```
cardano-node → cardano-db-sync (Postgres) → export scripts → BigQuery
                                          ↑
                                    views/vw_bq_*.sql
```

The updater runs continuously, writing new blocks and transactions as they are confirmed. Epoch-boundary tables (rewards, epoch stake snapshots, etc.) update once per epoch (~5 days).

A deep-compare job hashes rows across both databases to verify one-to-one correspondence.

## Documentation

Full table and column documentation: [GitHub Wiki](https://github.com/Blockchain-Data-Analytics/Cardano_on_BigQuery/wiki)

## License

See [LICENSE](./LICENSE).
