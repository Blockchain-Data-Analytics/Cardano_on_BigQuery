-- View: analytics.vw_bq_param_proposal

-- DROP VIEW analytics.vw_bq_param_proposal;

CREATE OR REPLACE VIEW analytics.vw_bq_param_proposal
 AS
 SELECT pp.epoch_no,
    encode(pp.key::bytea, 'hex'::text) AS key,
    pp.min_fee_a,
    pp.min_fee_b,
    pp.max_block_size,
    pp.max_tx_size,
    pp.max_bh_size,
    pp.key_deposit,
    pp.pool_deposit,
    pp.max_epoch,
    pp.optimal_pool_count,
    pp.influence,
    pp.monetary_expand_rate,
    pp.treasury_growth_rate,
    pp.decentralisation,
    encode(pp.entropy::bytea, 'hex'::text) AS entropy,
    pp.protocol_major,
    pp.protocol_minor,
    pp.min_utxo_value,
    pp.min_pool_cost,
    pp.coins_per_utxo_size,
    cm.costs AS cost_model,
    pp.price_mem,
    pp.price_step,
    pp.max_tx_ex_mem,
    pp.max_tx_ex_steps,
    pp.max_block_ex_mem,
    pp.max_block_ex_steps,
    pp.max_val_size,
    pp.collateral_percent,
    pp.max_collateral_inputs,
    block.slot_no AS registered_tx_slot_no,
    tx.block_index AS registered_tx_index
   FROM param_proposal pp
     JOIN tx tx ON tx.id = pp.registered_tx_id
     JOIN block block ON block.id = tx.block_id
     LEFT JOIN cost_model cm ON cm.id = pp.cost_model_id
  ORDER BY pp.epoch_no, block.slot_no, tx.block_index, pp.key;

ALTER TABLE analytics.vw_bq_param_proposal
    OWNER TO cardano;

GRANT SELECT ON TABLE analytics.vw_bq_param_proposal TO PUBLIC;
GRANT ALL ON TABLE analytics.vw_bq_param_proposal TO cardano;
