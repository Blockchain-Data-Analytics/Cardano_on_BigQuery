-- record block times as they are inserted into the db
CREATE TABLE analytics.block_time
(
    block_no bigint NOT NULL,
    block_created timestamp with time zone NOT NULL,
    block_inserted_to_db_sync timestamp with time zone NOT NULL
);


-- the function that is called on every new block
CREATE OR REPLACE FUNCTION analytics.record_blocktime()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE NOT LEAKPROOF
AS $BODY$
BEGIN
INSERT INTO analytics.block_time (block_no, block_created, block_inserted_to_db_sync)
VALUES (new.block_no, (new.time AT TIME ZONE 'UTC'), CURRENT_TIMESTAMP);
RETURN NULL;
END;
$BODY$;

-- add the trigger to db-sync's block table
CREATE TRIGGER block_time
    AFTER INSERT
    ON public.block
    FOR EACH ROW
    EXECUTE PROCEDURE analytics.record_blocktime();
