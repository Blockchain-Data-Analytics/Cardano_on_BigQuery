#!/usr/bin/env bash
# this script expects environment variable $BQ_CONFIG to be set beforehand

set -e

[ -n "${BQ_CONFIG}" ] || { echo "missing \$BQ_CONFIG"; exit 1; }

BASEDIR=$(realpath $(dirname $0))
TEMPDIR=$(mktemp -d)

source ${BASEDIR}/conf/config.pg
source ${BASEDIR}/conf/config.bq

export BQUSER=$(jq -r .client_email <<< "$BQ_CONFIG")
echo $BQ_CONFIG > ${TEMPDIR}/key.json
gcloud auth activate-service-account $BQUSER --key-file ${TEMPDIR}/key.json 
${BQ} ls

res2=$(${PSQL} -c "SELECT max(slot_no) as max_slot, max(epoch_no) as max_epoch from public.block;")
ENDING_SLOT=$(echo ${res2} | ${SED} -ne 's/^max_slot | max_epoch --*+--* \([0-9][0-9]*\).*/\1/p;')
PG_EPOCH=$(echo ${res2} | ${SED} -ne 's/^max_slot | max_epoch --*+--* \([0-9][0-9]*\) | \([0-9][0-9]*\).*/\2/p;')
ENDING_SLOT_MINUS_GRACE=$((ENDING_SLOT - GRACE_SLOTS))

Q="BEGIN TRANSACTION;\n"

for TABLE in tx tx_in_out tx_consumed_output tx_hash tx_metadata block block_hash rel_addr_txout rel_stake_txout rel_stake_hash collateral ma_minting script pool_offline_data pool_owner pool_retire pool_update redeemer stake_registration stake_deregistration withdrawal delegation datum; do
  TABLENAME="${BQ_PROJECT}.cardano_mainnet.${TABLE}"
  echo $TABLENAME
  res=$(${BQ} --format=json query --nouse_legacy_sql "SELECT last_slot_no FROM ${BQ_PROJECT}.db_sync.last_index where tablename = '${TABLENAME}'")
  STARTING_SLOT=$(echo ${res} | jq -r '.[0].last_slot_no')

  SCRIPT="./update_${TABLE}.sh"
  echo "Updating ${TABLENAME} since ${STARTING_SLOT} slot until ${ENDING_SLOT}"
  OUTPUT=$(${SCRIPT} ${STARTING_SLOT} ${ENDING_SLOT})  # Capture script output
  # Append the script output to the Q string
  Q+="${OUTPUT}\n"
done
Q+="COMMIT TRANSACTION;"
# Print the query for debugging (optional)
# echo -e "$Q"

# DRYRUN="--dry_run"
DRYRUN=

# Execute the transaction
${BQ} query --bigqueryrc=$(pwd)/dot.bigqueryrc ${DRYRUN} --dataset_id=${DATASETID} --nouse_legacy_sql "${Q}" 2> logs/transaction-query.err > logs/transaction-query.out


echo "Updating db-sync slot_no to ${ENDING_SLOT} and epoch_no to ${PG_EPOCH} in BigQuery"
Q="UPDATE ${BQ_PROJECT}.db_sync.last_index set last_slot_no=${ENDING_SLOT}, last_epoch_no=${PG_EPOCH} WHERE tablename='db-sync';"
${BQ} query --nouse_legacy_sql "${Q}"

rm ${TEMPDIR}/key.json
rmdir ${TEMPDIR}

gcloud pubsub topics publish ${PUBSUB_TOPIC_NAME} --message "Updated BQ tables up to slot_no ${ENDING_SLOT} and epoch_no to ${PG_EPOCH}" --project $BQ_PROJECT

echo "All done."
