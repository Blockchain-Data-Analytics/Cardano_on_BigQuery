#!/bin/bash

set -e

source ../lib/config.pg
source ../lib/functions.sh
source ../lib/config.bq

function Q() {
      local EPOCH=$1
      echo "
  SELECT epoch_no, stake_addr_hash, delegations
  FROM analytics.vw_bq_delegation
  WHERE epoch_no = ${EPOCH}
        "
}

# delegations started in epoch 208
process_epoch_f Q "delegation" "${BQ_PROJECT}.db_sync" 208
