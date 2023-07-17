#!/bin/bash

set -e

source ../lib/config.pg
source ../lib/functions.sh
source ../lib/config.bq

function Q() {
      local EPOCH=$1
      echo "
  SELECT epoch_no, stake_addr_hash, amount, slot_no, txidx
  FROM analytics.vw_bq_withdrawal
  WHERE epoch_no = ${EPOCH}
  "
}

# 209 is the first epoch with withdrawals
process_epoch_f Q "withdrawal" "${BQ_PROJECT}.db_sync" 209
