-- View: analytics.vw_bq_epoch_param

-- DROP VIEW analytics.vw_bq_epoch_param;

CREATE OR REPLACE VIEW analytics.vw_bq_epoch_param
 AS
 SELECT ep.epoch_no,
    ep.min_fee_a,
    ep.min_fee_b,
    ep.max_block_size,
    ep.max_tx_size,
    ep.max_bh_size,
    ep.key_deposit,
    ep.pool_deposit,
    ep.max_epoch,
    ep.optimal_pool_count,
    ep.influence,
    ep.monetary_expand_rate,
    ep.treasury_growth_rate,
    ep.decentralisation,
    encode(ep.extra_entropy::bytea, 'hex'::text) AS extra_entropy,
    ep.protocol_major,
    ep.protocol_minor,
    ep.min_utxo_value,
    ep.min_pool_cost,
    encode(ep.nonce::bytea, 'hex'::text) AS nonce,
    ep.coins_per_utxo_size,
    cm.costs AS cost_model,
    ep.price_mem,
    ep.price_step,
    ep.max_tx_ex_mem,
    ep.max_tx_ex_steps,
    ep.max_block_ex_mem,
    ep.max_block_ex_steps,
    ep.max_val_size,
    ep.collateral_percent,
    ep.max_collateral_inputs
   FROM epoch_param ep
     LEFT JOIN cost_model cm ON cm.id = ep.cost_model_id
  ORDER BY ep.epoch_no;

ALTER TABLE analytics.vw_bq_epoch_param
    OWNER TO cardano;

GRANT SELECT ON TABLE analytics.vw_bq_epoch_param TO PUBLIC;
GRANT ALL ON TABLE analytics.vw_bq_epoch_param TO cardano;
