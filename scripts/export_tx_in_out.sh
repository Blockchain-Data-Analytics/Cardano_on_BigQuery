#!/bin/bash

set -e

source ./conf/config.pg
source ./conf/config.bq
source ./functions.sh

function Q() {
      local EPOCH=$1
      echo "
   SELECT epoch_no, slot_no, txidx, inputs, outputs
   FROM analytics.vw_bq_tx_in_out
   WHERE epoch_no = ${EPOCH} "
}

process_epoch_f Q "tx_in_out" "${BQ_PROJECT}.db_sync" 287
