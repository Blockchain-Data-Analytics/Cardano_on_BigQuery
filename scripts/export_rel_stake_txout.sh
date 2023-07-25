#!/bin/bash

set -e

source ./conf/config.pg
source ./conf/config.bq
source ./functions.sh

function Q() {
      local EPOCH=$1
      echo "
   SELECT *
   FROM analytics.vw_bq_rel_stake_txout(${EPOCH})
      "
}

# the first delegation was in epoch 208
process_epoch_f Q "rel_stake_txout" "${BQ_PROJECT}.db_sync" 208

