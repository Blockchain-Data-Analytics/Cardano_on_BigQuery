#!/bin/bash

if [ $# -lt 2 ]; then
	echo "$0 bq_epoch_no pg_epoch_no"
	exit 1
fi

set -e

source ./conf/config.pg
source ./functions.sh

TNAME="ma_minting"

BQ_EPOCH_NO=$1
PG_EPOCH_NO=$2

if [ "$BQ_EPOCH_NO" -eq "$PG_EPOCH_NO" ]; then
	echo "Last epoch in BigQuery is $BQ_EPOCH_NO. Nothing to do."
	exit 1
elif [ "$BQ_EPOCH_NO" -ge "$PG_EPOCH_NO" ]; then
  echo "Last epoch in BigQuery is $BQ_EPOCH_NO >= $PG_EPOCH_NO (epoch in Postgres)"
  exit 1
else
  # update the past epoch number (reference: db_sync)
  EPOCH_NO=$(( PG_EPOCH_NO - 1 ))
  echo "BQ @ ${BQ_EPOCH_NO}"
  echo "   reloading for epoch $EPOCH_NO"
fi

CSVNAME="update_${TNAME}-q1"
if [ -e "${CSVNAME}.csv" ]; then rm -f "${CSVNAME}.csv"; fi
SCHEMA="${TNAME}"
DATASETID="${BQ_PROJECT}:db_sync"

## 1 insert epoch into tmp table
TMPTBL="tmp_${TNAME}_1"
Q="
  SELECT fingerprint, policyid, name_bytes, epoch_no, minting
  FROM analytics.vw_bq_ma_minting
  WHERE epoch_no = ${EPOCH_NO}"
NREAD=$(pg_query_to_csv "${Q}" "$CSVNAME")
if [ -z "${NREAD}" -o $NREAD -lt 0 ]
then 
  echo "Q: returned ${NREAD}."; 
  exit 1;
elif [ $NREAD -eq 0 ]
then
  echo "Q: returned ${NREAD}. Nothing to do"; 
  exit 0;
fi
bq_load_csv "$CSVNAME" "$TMPTBL" "$SCHEMA" "$DATASETID"

# run the transaction
SRCDATASET="${BQ_PROJECT}.db_sync"
TARGETTBL="${BQ_PROJECT}.cardano_mainnet.${TNAME}"
Q="
   BEGIN TRANSACTION;
   -- 1 delete epoch data
   DELETE FROM ${TARGETTBL}
   WHERE epoch_no = ${EPOCH_NO};
   -- 2 insert epoch data (new)
   INSERT INTO ${TARGETTBL}
   SELECT fingerprint,policyid,name_bytes,epoch_no,minting FROM ${SRCDATASET}.${TMPTBL};
   -- 3 update the last index table
   UPDATE db_sync.last_index set last_epoch_no=${EPOCH_NO} WHERE tablename='${TARGETTBL}';
   COMMIT TRANSACTION;
"

#DRYRUN="--dry_run"
DRYRUN=

${BQ} query --bigqueryrc=$(pwd)/dot.bigqueryrc ${DRYRUN} --dataset_id=${DATASETID} --nouse_legacy_sql "${Q}" 2> logs/update_${TNAME}-query.err > logs/update_${TNAME}-query.out

echo
echo "values inserted successfully for epoch: ${EPOCH_NO}"
echo "all done."
