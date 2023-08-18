-- View: analytics.vw_bq_epoch_stake

-- DROP VIEW analytics.vw_bq_epoch_stake;

CREATE OR REPLACE VIEW analytics.vw_bq_epoch_stake
AS
SELECT es.epoch_no,
       encode(sa.hash_raw, 'hex') AS stake_addr_hash,
       encode(ph.hash_raw, 'hex') AS pool_hash,
       es.amount
FROM public.epoch_stake es
         JOIN public.stake_address sa ON es.addr_id = sa.id
         JOIN public.pool_hash ph ON es.pool_id = ph.id
ORDER BY epoch_no, stake_addr_hash, pool_hash ASC;

ALTER TABLE analytics.vw_bq_epoch_stake
    OWNER TO cardano;

GRANT SELECT ON TABLE analytics.vw_bq_epoch_stake TO PUBLIC;
GRANT ALL ON TABLE analytics.vw_bq_epoch_stake TO cardano;
