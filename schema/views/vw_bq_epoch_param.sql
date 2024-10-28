-- View: analytics.vw_bq_epoch_param

-- DROP VIEW analytics.vw_bq_epoch_param;

CREATE OR REPLACE VIEW analytics.vw_bq_epoch_param
 AS
  SELECT epoch_no,
    to_json(t.*) AS params
   FROM epoch_param t
  ORDER BY epoch_no;

ALTER TABLE analytics.vw_bq_epoch_param
    OWNER TO cardano;

GRANT SELECT ON TABLE analytics.vw_bq_epoch_param TO PUBLIC;
GRANT ALL ON TABLE analytics.vw_bq_epoch_param TO cardano;
