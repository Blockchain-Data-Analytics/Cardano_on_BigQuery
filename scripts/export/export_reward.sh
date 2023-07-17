#!/bin/bash

set -e

source ../lib/config.pg
source ../lib/functions.sh
source ../lib/config.bq

function Q() {
      local EPOCH=$1
      echo "
  SELECT epoch_no, stake_addr_hash, type, amount, earned_epoch, pool_hash
  FROM analytics.vw_bq_reward
  WHERE epoch_no = ${EPOCH} "
}

# 209 is the first epoch with spendable rewards
process_epoch_f Q "reward" "${BQ_PROJECT}.db_sync" 209
