#!/bin/bash

set -e

source ../lib/config.pg
source ../lib/functions.sh
source ../lib/config.bq

function Q() {
      local EPOCH=$1
      echo "
  SELECT epoch_no, slot_no, txidx, tx_hash
  FROM analytics.vw_bq_tx_hash
  WHERE epoch_no = ${EPOCH} "
}

process_epoch_f Q "tx_hash" "${BQ_PROJECT}.db_sync" 0
