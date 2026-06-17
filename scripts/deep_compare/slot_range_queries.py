import os


def bq_slot_range_query(min_slot: int, max_slot: int, bq_project: str = None) -> str:
    if bq_project is None:
        bq_project = os.environ['BQ_PROJECT']
    p = bq_project
    sl = f"slot_no BETWEEN {min_slot} AND {max_slot}"
    ep_in = f"epoch_no IN (SELECT DISTINCT epoch_no FROM `{p}.cardano_mainnet.block` WHERE {sl})"

    parts = []

    # block
    parts.append(f"""SELECT 'block' AS table_name, innerq.cnt AS row_count, TO_BASE64(SHA256(innerq.hash_b64)) AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(TO_BASE64(SHA256(str)), ',') AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| slot_no ||','|| block_time ||','|| block_size ||','|| tx_count
         ||','|| sum_tx_fee ||','|| script_count ||','|| sum_script_size ||')' AS str
  FROM `{p}.cardano_mainnet.block`
  WHERE {sl}
  ORDER BY epoch_no, slot_no ASC)) AS innerq""")

    # block_hash
    parts.append(f"""SELECT 'block_hash' AS table_name, innerq.cnt AS row_count, TO_BASE64(SHA256(innerq.hash_b64)) AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(TO_BASE64(SHA256(str)), ',') AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| slot_no ||','|| block_hash ||')' AS str
  FROM `{p}.cardano_mainnet.block_hash`
  WHERE {sl}
  ORDER BY epoch_no, slot_no ASC)) AS innerq""")

    # collateral
    parts.append(f"""SELECT 'collateral' AS table_name, innerq.cnt AS row_count, TO_BASE64(SHA256(innerq.hash_b64)) AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(TO_BASE64(SHA256(str)), ',') AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| slot_no ||','|| txidx ||','|| epoch_no_out ||','|| slot_no_out
         ||','|| txidx_out ||','|| tx_out_index ||')' AS str
  FROM `{p}.cardano_mainnet.collateral`
  WHERE {sl}
  ORDER BY epoch_no, slot_no, txidx, epoch_no_out, slot_no_out, txidx_out, tx_out_index ASC)) AS innerq""")

    # delegation (epoch-derived) -- disabled until epoch-based check is added

    # ma_minting (epoch-derived) -- disabled until epoch-based check is added

    # pool_offline_data (epoch-derived) -- disabled until epoch-based check is added

    # pool_owner
    parts.append(f"""SELECT 'pool_owner' AS table_name, innerq.cnt AS row_count, TO_BASE64(SHA256(innerq.hash_b64)) AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(TO_BASE64(SHA256(str)), ',') AS hash_b64 FROM
 (SELECT '('|| pool_hash ||','|| epoch_no ||','|| addr_hash ||','|| slot_no ||','|| txidx ||')' AS str
  FROM `{p}.cardano_mainnet.pool_owner`
  WHERE {sl}
  ORDER BY epoch_no, slot_no, txidx, pool_hash, addr_hash ASC)) AS innerq""")

    # pool_retire
    parts.append(f"""SELECT 'pool_retire' AS table_name, innerq.cnt AS row_count, TO_BASE64(SHA256(innerq.hash_b64)) AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(TO_BASE64(SHA256(str)), ',') AS hash_b64 FROM
 (SELECT '('|| pool_hash ||','|| retiring_epoch ||','|| epoch_no ||','|| cert_index
         ||','|| announced_tx_hash ||','|| slot_no ||','|| announced_txidx ||')' AS str
  FROM `{p}.cardano_mainnet.pool_retire`
  WHERE {sl}
  ORDER BY epoch_no, slot_no, announced_txidx, pool_hash ASC)) AS innerq""")

    # pool_update (epoch-derived) -- disabled until epoch-based check is added

    # redeemer
    parts.append(f"""SELECT 'redeemer' AS table_name, innerq.cnt AS row_count, TO_BASE64(SHA256(innerq.hash_b64)) AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(TO_BASE64(SHA256(str)), ',') AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| slot_no ||','|| txidx ||','|| count ||')' AS str
  FROM `{p}.cardano_mainnet.redeemer`
  WHERE {sl}
  ORDER BY epoch_no, slot_no, txidx ASC)) AS innerq""")

    # rel_addr_txout (epoch-derived) -- disabled until epoch-based check is added

    # rel_stake_hash
    parts.append(f"""SELECT 'rel_stake_hash' AS table_name, innerq.cnt AS row_count, TO_BASE64(SHA256(innerq.hash_b64)) AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(TO_BASE64(SHA256(str)), ',') AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| slot_no ||','|| stake_address ||','|| stake_addr_hash ||')' AS str
  FROM `{p}.cardano_mainnet.rel_stake_hash`
  WHERE {sl}
  ORDER BY epoch_no, slot_no, stake_address ASC)) AS innerq""")

    # rel_stake_txout (epoch-derived) -- disabled until epoch-based check is added

    # reward (epoch-derived) -- disabled until epoch-based check is added

    # script
    parts.append(f"""SELECT 'script' AS table_name, innerq.cnt AS row_count, TO_BASE64(SHA256(innerq.hash_b64)) AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(TO_BASE64(SHA256(str)), ',') AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| slot_no ||','|| txidx ||','|| script_hash ||','|| `type`
         ||','|| COALESCE(TO_BASE64(`bytes`), 'null')
         ||','|| COALESCE(CAST(serialised_size AS STRING), 'null') ||')' AS str
  FROM `{p}.cardano_mainnet.script`
  WHERE {sl}
  ORDER BY epoch_no, slot_no, txidx, script_hash ASC)) AS innerq""")

    # stake_deregistration
    parts.append(f"""SELECT 'stake_deregistration' AS table_name, innerq.cnt AS row_count, TO_BASE64(SHA256(innerq.hash_b64)) AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(TO_BASE64(SHA256(str)), ',') AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| slot_no ||','|| txidx ||','|| stake_addr_hash ||','|| cert_index ||')' AS str
  FROM `{p}.cardano_mainnet.stake_deregistration`
  WHERE {sl}
  ORDER BY epoch_no, slot_no, txidx, stake_addr_hash, cert_index ASC)) AS innerq""")

    # stake_registration
    parts.append(f"""SELECT 'stake_registration' AS table_name, innerq.cnt AS row_count, TO_BASE64(SHA256(innerq.hash_b64)) AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(TO_BASE64(SHA256(str)), ',') AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| slot_no ||','|| txidx ||','|| stake_addr_hash ||','|| cert_index ||')' AS str
  FROM `{p}.cardano_mainnet.stake_registration`
  WHERE {sl}
  ORDER BY epoch_no, slot_no, txidx, stake_addr_hash, cert_index ASC)) AS innerq""")

    # tx
    parts.append(f"""SELECT 'tx' AS table_name, innerq.cnt AS row_count, TO_BASE64(SHA256(innerq.hash_b64)) AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(TO_BASE64(SHA256(str)), ',') AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| tx_hash ||','|| block_time ||','|| slot_no ||','|| txidx
         ||','|| out_sum ||','|| fee ||','|| deposit ||','|| size
         ||','|| COALESCE(CAST(invalid_before AS STRING), 'null')
         ||','|| COALESCE(CAST(invalid_after AS STRING), 'null')
         ||','|| valid_script ||','|| script_size ||','|| count_inputs ||','|| count_outputs ||')' AS str
  FROM `{p}.cardano_mainnet.tx`
  WHERE {sl}
  ORDER BY epoch_no, slot_no, txidx ASC)) AS innerq""")

    # tx_consumed_output (filter by producing tx slot_no)
    parts.append(f"""SELECT 'tx_consumed_output' AS table_name, innerq.cnt AS row_count, TO_BASE64(SHA256(innerq.hash_b64)) AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(TO_BASE64(SHA256(str)), ',') AS hash_b64 FROM
 (SELECT '('|| slot_no ||','|| txidx ||','|| `index` ||','|| consumed_in_slot_no ||','|| consumed_in_txidx ||')' AS str
  FROM `{p}.cardano_mainnet.tx_consumed_output`
  WHERE consumed_in_slot_no BETWEEN {min_slot} AND {max_slot}
  ORDER BY slot_no, txidx, `index` ASC)) AS innerq""")

    # tx_hash
    parts.append(f"""SELECT 'tx_hash' AS table_name, innerq.cnt AS row_count, TO_BASE64(SHA256(innerq.hash_b64)) AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(TO_BASE64(SHA256(str)), ',') AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| slot_no ||','|| txidx ||','|| tx_hash ||')' AS str
  FROM `{p}.cardano_mainnet.tx_hash`
  WHERE {sl}
  ORDER BY epoch_no, slot_no, txidx ASC)) AS innerq""")

    # tx_in_out
    parts.append(f"""SELECT 'tx_in_out' AS table_name, innerq.cnt AS row_count, TO_BASE64(SHA256(innerq.hash_b64)) AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(TO_BASE64(SHA256(str)), ',') AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| slot_no ||','|| txidx
         ||','|| TO_JSON_STRING(inputs)
         ||','|| COALESCE(TO_JSON_STRING(outputs), 'null') ||')' AS str
  FROM `{p}.cardano_mainnet.tx_in_out`
  WHERE {sl}
  ORDER BY epoch_no, slot_no, txidx ASC)) AS innerq""")

    # tx_metadata
    parts.append(f"""SELECT 'tx_metadata' AS table_name, innerq.cnt AS row_count, TO_BASE64(SHA256(innerq.hash_b64)) AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(TO_BASE64(SHA256(str)), ',') AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| slot_no ||','|| txidx ||','|| tx_hash ||','|| key ||')' AS str
  FROM `{p}.cardano_mainnet.tx_metadata`
  WHERE {sl}
  ORDER BY epoch_no, slot_no, txidx, tx_hash, key, JSON_VALUE(metadata) ASC)) AS innerq""")

    # withdrawal
    parts.append(f"""SELECT 'withdrawal' AS table_name, innerq.cnt AS row_count, TO_BASE64(SHA256(innerq.hash_b64)) AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(TO_BASE64(SHA256(str)), ',') AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| stake_addr_hash ||','|| amount ||','|| slot_no ||','|| txidx ||')' AS str
  FROM `{p}.cardano_mainnet.withdrawal`
  WHERE {sl}
  ORDER BY epoch_no, slot_no, txidx, stake_addr_hash ASC)) AS innerq""")

    return "\nUNION ALL\n\n".join(parts)


def pg_slot_range_query(min_slot: int, max_slot: int) -> str:
    sl = f"slot_no BETWEEN {min_slot} AND {max_slot}"
    ep_in = f"epoch_no IN (SELECT DISTINCT epoch_no FROM public.block WHERE {sl})"

    parts = []

    # block (no normalization)
    parts.append(f"""SELECT 'block' AS table_name, innerq.cnt AS row_count, encode(SHA256(innerq.hash_b64), 'base64') AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(encode(SHA256(subq.str::bytea), 'base64'), ',')::bytea AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| slot_no ||','|| block_time ||','|| block_size ||','|| tx_count
         ||','|| sum_tx_fee ||','|| script_count ||','|| sum_script_size ||')' AS str
  FROM analytics.vw_bq_block
  WHERE {sl}
  ORDER BY epoch_no, slot_no ASC) AS subq) AS innerq""")

    # block_hash (whitespace normalization)
    parts.append(f"""SELECT 'block_hash' AS table_name, innerq.cnt AS row_count, encode(SHA256(innerq.hash_b64), 'base64') AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(encode(SHA256(regexp_replace(regexp_replace(subq.str, '[\n]', '', 'g'), '[\\s]', '', 'g')::bytea), 'base64'), ',')::bytea AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| slot_no ||','|| block_hash ||')' AS str
  FROM analytics.vw_bq_block_hash
  WHERE {sl}
  ORDER BY epoch_no, slot_no ASC) AS subq) AS innerq""")

    # collateral (no normalization)
    parts.append(f"""SELECT 'collateral' AS table_name, innerq.cnt AS row_count, encode(SHA256(innerq.hash_b64), 'base64') AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(encode(SHA256(subq.str::bytea), 'base64'), ',')::bytea AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| slot_no ||','|| txidx ||','|| epoch_no_out ||','|| slot_no_out
         ||','|| txidx_out ||','|| tx_out_index ||')' AS str
  FROM analytics.vw_bq_collateral
  WHERE {sl}
  ORDER BY epoch_no, slot_no, txidx, epoch_no_out, slot_no_out, txidx_out, tx_out_index ASC) AS subq) AS innerq""")

    # delegation (epoch-derived) -- disabled until epoch-based check is added
    # ma_minting (epoch-derived) -- disabled until epoch-based check is added
    # pool_offline_data (epoch-derived) -- disabled until epoch-based check is added

    # pool_owner (no normalization)
    parts.append(f"""SELECT 'pool_owner' AS table_name, innerq.cnt AS row_count, encode(SHA256(innerq.hash_b64), 'base64') AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(encode(SHA256(subq.str::bytea), 'base64'), ',')::bytea AS hash_b64 FROM
 (SELECT '('|| pool_hash ||','|| epoch_no ||','|| addr_hash ||','|| slot_no ||','|| txidx ||')' AS str
  FROM analytics.vw_bq_pool_owner
  WHERE {sl}
  ORDER BY epoch_no, slot_no, txidx, pool_hash, addr_hash ASC) AS subq) AS innerq""")

    # pool_retire (no normalization)
    parts.append(f"""SELECT 'pool_retire' AS table_name, innerq.cnt AS row_count, encode(SHA256(innerq.hash_b64), 'base64') AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(encode(SHA256(subq.str::bytea), 'base64'), ',')::bytea AS hash_b64 FROM
 (SELECT '('|| pool_hash ||','|| retiring_epoch ||','|| epoch_no ||','|| cert_index
         ||','|| announced_tx_hash ||','|| slot_no ||','|| announced_txidx ||')' AS str
  FROM analytics.vw_bq_pool_retire
  WHERE {sl}
  ORDER BY epoch_no, slot_no, announced_txidx, pool_hash ASC) AS subq) AS innerq""")

    # pool_update (epoch-derived) -- disabled until epoch-based check is added

    # redeemer (no normalization)
    parts.append(f"""SELECT 'redeemer' AS table_name, innerq.cnt AS row_count, encode(SHA256(innerq.hash_b64), 'base64') AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(encode(SHA256(subq.str::bytea), 'base64'), ',')::bytea AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| slot_no ||','|| txidx ||','|| count ||')' AS str
  FROM analytics.vw_bq_redeemer
  WHERE {sl}
  ORDER BY epoch_no, slot_no, txidx ASC) AS subq) AS innerq""")

    # rel_addr_txout (epoch-derived) -- disabled until epoch-based check is added

    # rel_stake_hash (no normalization)
    parts.append(f"""SELECT 'rel_stake_hash' AS table_name, innerq.cnt AS row_count, encode(SHA256(innerq.hash_b64), 'base64') AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(encode(SHA256(subq.str::bytea), 'base64'), ',')::bytea AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| slot_no ||','|| stake_address ||','|| stake_addr_hash ||')' AS str
  FROM analytics.vw_bq_rel_stake_hash
  WHERE {sl}
  ORDER BY epoch_no, slot_no, stake_address ASC) AS subq) AS innerq""")

    # rel_stake_txout (epoch-derived) -- disabled until epoch-based check is added
    # reward (epoch-derived) -- disabled until epoch-based check is added

    # script (whitespace normalization)
    parts.append(f"""SELECT 'script' AS table_name, innerq.cnt AS row_count, encode(SHA256(innerq.hash_b64), 'base64') AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(encode(SHA256(regexp_replace(regexp_replace(subq.str, '[\n]', '', 'g'), '[\\s]', '', 'g')::bytea), 'base64'), ',')::bytea AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| slot_no ||','|| txidx ||','|| script_hash ||','|| "type"
         ||','|| COALESCE("bytes", 'null')
         ||','|| COALESCE(serialised_size::text, 'null') ||')' AS str
  FROM analytics.vw_bq_script
  WHERE {sl}
  ORDER BY epoch_no, slot_no, txidx, script_hash ASC) AS subq) AS innerq""")

    # stake_deregistration (no normalization)
    parts.append(f"""SELECT 'stake_deregistration' AS table_name, innerq.cnt AS row_count, encode(SHA256(innerq.hash_b64), 'base64') AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(encode(SHA256(subq.str::bytea), 'base64'), ',')::bytea AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| slot_no ||','|| txidx ||','|| stake_addr_hash ||','|| cert_index ||')' AS str
  FROM analytics.vw_bq_stake_deregistration
  WHERE {sl}
  ORDER BY epoch_no, slot_no, txidx, stake_addr_hash, cert_index ASC) AS subq) AS innerq""")

    # stake_registration (no normalization)
    parts.append(f"""SELECT 'stake_registration' AS table_name, innerq.cnt AS row_count, encode(SHA256(innerq.hash_b64), 'base64') AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(encode(SHA256(subq.str::bytea), 'base64'), ',')::bytea AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| slot_no ||','|| txidx ||','|| stake_addr_hash ||','|| cert_index ||')' AS str
  FROM analytics.vw_bq_stake_registration
  WHERE {sl}
  ORDER BY epoch_no, slot_no, txidx, stake_addr_hash, cert_index ASC) AS subq) AS innerq""")

    # tx (no normalization)
    parts.append(f"""SELECT 'tx' AS table_name, innerq.cnt AS row_count, encode(SHA256(innerq.hash_b64), 'base64') AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(encode(SHA256(subq.str::bytea), 'base64'), ',')::bytea AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| tx_hash ||','|| block_time ||','|| slot_no ||','|| txidx
         ||','|| out_sum ||','|| fee ||','|| deposit ||','|| size
         ||','|| COALESCE(invalid_before::text, 'null')
         ||','|| COALESCE(invalid_after::text, 'null')
         ||','|| valid_script ||','|| script_size ||','|| count_inputs ||','|| count_outputs ||')' AS str
  FROM analytics.vw_bq_tx
  WHERE {sl}
  ORDER BY epoch_no, slot_no, txidx ASC) AS subq) AS innerq""")

    # tx_consumed_output (filter by producing tx slot_no, no normalization)
    parts.append(f"""SELECT 'tx_consumed_output' AS table_name, innerq.cnt AS row_count, encode(SHA256(innerq.hash_b64), 'base64') AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(encode(SHA256(subq.str::bytea), 'base64'), ',')::bytea AS hash_b64 FROM
 (SELECT '('|| slot_no ||','|| txidx ||','|| "index" ||','|| consumed_in_slot_no ||','|| consumed_in_txidx ||')' AS str
  FROM analytics.vw_bq_tx_consumed_output
  WHERE consumed_in_slot_no BETWEEN {min_slot} AND {max_slot}
  ORDER BY slot_no, txidx, "index" ASC) AS subq) AS innerq""")

    # tx_hash (no normalization)
    parts.append(f"""SELECT 'tx_hash' AS table_name, innerq.cnt AS row_count, encode(SHA256(innerq.hash_b64), 'base64') AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(encode(SHA256(subq.str::bytea), 'base64'), ',')::bytea AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| slot_no ||','|| txidx ||','|| tx_hash ||')' AS str
  FROM analytics.vw_bq_tx_hash
  WHERE {sl}
  ORDER BY epoch_no, slot_no, txidx ASC) AS subq) AS innerq""")

    # tx_in_out (whitespace normalization)
    parts.append(f"""SELECT 'tx_in_out' AS table_name, innerq.cnt AS row_count, encode(SHA256(innerq.hash_b64), 'base64') AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(encode(SHA256(regexp_replace(regexp_replace(subq.str, '[\n]+', '', 'g'), '[\\s]+', '', 'g')::bytea), 'base64'), ',')::bytea AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| slot_no ||','|| txidx
         ||','|| inputs::text
         ||','|| COALESCE(outputs::text, 'null') ||')' AS str
  FROM analytics.vw_bq_tx_in_out
  WHERE {sl}
  ORDER BY epoch_no, slot_no, txidx ASC) AS subq) AS innerq""")

    # tx_metadata (direct table join, no normalization)
    parts.append(f"""SELECT 'tx_metadata' AS table_name, innerq.cnt AS row_count, encode(SHA256(innerq.hash_b64), 'base64') AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(encode(SHA256(subq.str::bytea), 'base64'), ',')::bytea AS hash_b64 FROM
 (SELECT '('|| ib.epoch_no ||','|| ib.slot_no ||','|| itx.block_index ||','|| encode(itx.hash,'hex') ||','|| tm.key ||')' AS str
  FROM public.tx_metadata tm
  JOIN public.tx itx ON itx.id = tm.tx_id
  JOIN public.block ib ON ib.id = itx.block_id
  WHERE ib.{sl}
  ORDER BY ib.epoch_no, ib.slot_no, itx.block_index, encode(itx.hash,'hex'), tm.key, tm.json::text ASC) AS subq) AS innerq""")

    # withdrawal (whitespace normalization)
    parts.append(f"""SELECT 'withdrawal' AS table_name, innerq.cnt AS row_count, encode(SHA256(innerq.hash_b64), 'base64') AS hash_val FROM
(SELECT COUNT(*) AS cnt, STRING_AGG(encode(SHA256(regexp_replace(regexp_replace(subq.str, '[\n]', '', 'g'), '[\\s]', '', 'g')::bytea), 'base64'), ',')::bytea AS hash_b64 FROM
 (SELECT '('|| epoch_no ||','|| stake_addr_hash ||','|| amount ||','|| slot_no ||','|| txidx ||')' AS str
  FROM analytics.vw_bq_withdrawal
  WHERE {sl}
  ORDER BY epoch_no, slot_no, txidx, stake_addr_hash ASC) AS subq) AS innerq""")

    return "\nUNION ALL\n\n".join(parts)
