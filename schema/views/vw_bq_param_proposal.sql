-- View: analytics.vw_bq_param_proposal

-- DROP VIEW analytics.vw_bq_param_proposal;

CREATE OR REPLACE VIEW analytics.vw_bq_param_proposal
 AS
 SELECT epoch_no,
    to_json(t.*) AS params
   FROM param_proposal t
  ORDER BY epoch_no, id;

ALTER TABLE analytics.vw_bq_param_proposal
    OWNER TO cardano;

GRANT SELECT ON TABLE analytics.vw_bq_param_proposal TO PUBLIC;
GRANT ALL ON TABLE analytics.vw_bq_param_proposal TO cardano;
