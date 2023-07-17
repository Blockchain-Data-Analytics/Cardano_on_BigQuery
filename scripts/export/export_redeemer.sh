#!/bin/bash

set -e

source ../lib/config.pg
source ../lib/functions.sh
source ../lib/config.bq

function Q() {
      local EPOCH=$1
      echo "
    SELECT epoch_no, slot_no, txidx, count, redeemers
    FROM analytics.vw_bq_redeemer 
    WHERE epoch_no = ${EPOCH} "
}

# starting from epoch 290
process_epoch_f Q "redeemer" "${BQ_PROJECT}.db_sync" 290
