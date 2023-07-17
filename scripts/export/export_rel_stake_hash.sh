#!/bin/bash

set -e

source ../lib/config.pg
source ../lib/functions.sh
source ../lib/config.bq

function Q() {
      local EPOCH=$1
      echo "SELECT epoch_no, slot_no, stake_address, stake_addr_hash
            FROM analytics.vw_bq_rel_stake_hash sa
            WHERE epoch_no = ${EPOCH} "
}

# the first delegation was in epoch 208
process_epoch_f Q "rel_stake_hash" "${BQ_PROJECT}.db_sync" 242
