#!/bin/bash

set -e

source ./conf/config.bq
source ./conf/config.pg
source functions.sh

function Q() {
      local EPOCH=$1
      echo "
  SELECT epoch_no,
         stake_addr_hash,
         pool_hash,
         amount
  FROM analytics.vw_bq_epoch_stake
  WHERE epoch_no = ${EPOCH}
        "
}

# epoch_stake started in epoch 210
process_epoch_f Q "epoch_stake" "${BQ_PROJECT}.db_sync" 210
