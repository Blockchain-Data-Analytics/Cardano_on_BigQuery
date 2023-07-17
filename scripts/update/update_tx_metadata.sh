#!/bin/bash

if [ $# -lt 2 ]; then
	echo "$0 bq_block_height pg_block_height"
	exit 1
fi

set -e

source ../lib/config.pg
source ../lib/config.bq
source ../lib/functions.sh

TNAME="tx_metadata"

# BQ block height (TBD)
ACT_SLOT_NO=$1

# DB_SYNC block height (TBD)
CURR_SLOT_NO=$2

DELTA=$((CURR_SLOT_NO - ACT_SLOT_NO))
if [ $DELTA -lt 0 ]; then
	echo "something weird: bq@${ACT_SLOT_NO} pg@${CURR_SLOT_NO}!"
	exit 1
fi
if [ $DELTA -gt $CAP_SLOTS ]; then
	echo "too many slots in update, cap at $CAP_SLOTS"
	CURR_SLOT_NO=$((ACT_SLOT_NO + CAP_SLOTS))
fi

CLEAN_SLOT_NO=$((ACT_SLOT_NO - DELETE_SLOTS))
MAX_SLOT_NO=$((CURR_SLOT_NO - GRACE_SLOTS))

echo "BQ @ ${ACT_SLOT_NO}"
echo "   loading up to $MAX_SLOT_NO"
echo "   deleting from $CLEAN_SLOT_NO"

CSVNAME="update_${TNAME}-q1"
if [ -e "${CSVNAME}.csv" ]; then rm -f "${CSVNAME}.csv"; fi
SCHEMA="${TNAME}"
DATASETID="${BQ_PROJECT}:db_sync"

## 1 delete slots 

## 2 insert slots (clean until max) into table
TMPTBL="tmp_${TNAME}_1"
Q="
    SELECT block.epoch_no, encode(tx.hash,'hex') AS \"tx_hash\",
           block.slot_no, tx.block_index AS txidx, subq.metadata
    FROM (
        SELECT tx_id,
            json_agg(('{\"index\":'||key::text||',\"meta\":'||json::text||'}')::json) AS metadata
        FROM public.tx_metadata
        JOIN public.tx itx ON itx.id = tx_id
        JOIN public.block ib ON ib.id = itx.block_id
        WHERE ib.slot_no >= ${CLEAN_SLOT_NO}
        AND ib.slot_no <= ${MAX_SLOT_NO}
        GROUP BY tx_id
        ORDER BY tx_id ASC
    ) AS subq
    JOIN public.tx ON tx.id = subq.tx_id
    JOIN public.block ON block.id = tx.block_id "
NREAD=$(pg_query_to_csv "${Q}" "$CSVNAME")
if [ -z "${NREAD}" -o $NREAD -le 0 ]; then echo "Q: returned ${NREAD}."; (exit 1); fi
bq_load_csv "$CSVNAME" "$TMPTBL" "$SCHEMA" "$DATASETID"

# run the transaction
SRCDATASET="${BQ_PROJECT}.db_sync"
TARGETTBL="${BQ_PROJECT}.cardano_mainnet.${TNAME}"
Q="
   BEGIN TRANSACTION;
   -- 1 delete slots
   DELETE FROM ${TARGETTBL} WHERE slot_no >= ${CLEAN_SLOT_NO};
   -- 2 insert new slots
   INSERT INTO ${TARGETTBL}
   SELECT * FROM ${SRCDATASET}.${TMPTBL};
   -- 3 update the last index table
   UPDATE db_sync.last_index set last_slot_no=${MAX_SLOT_NO} WHERE tablename='${TARGETTBL}';
   COMMIT TRANSACTION;
"

#DRYRUN="--dry_run"
DRYRUN=

${BQ} query --bigqueryrc=$(pwd)/dot.bigqueryrc ${DRYRUN} --dataset_id=${DATASETID} --nouse_legacy_sql "${Q}" 2> logs/update_${TNAME}-query.err > logs/update_${TNAME}-query.out

echo
echo "table's ${TNAME} new block height: ${MAX_SLOT_NO}"
echo "all done."
