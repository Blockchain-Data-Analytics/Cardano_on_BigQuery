#!/bin/bash

set -e

source ../lib/config.pg
source ../lib/functions.sh
source ../lib/config.bq

function Q() {
      local EPOCH=$1
      echo "
  SELECT epoch_no, slot_no, block_time, block_size, tx_count, sum_tx_fee, script_count, sum_script_size, pool_hash
  FROM analytics.vw_bq_block
  WHERE epoch_no = ${EPOCH} "
}

process_epoch_f Q "block" "${BQ_PROJECT}.db_sync" 0
