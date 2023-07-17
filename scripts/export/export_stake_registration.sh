#!/bin/bash

set -e

source ../lib/config.pg
source ../lib/functions.sh
source ../lib/config.bq

function Q() {
      local EPOCH=$1
      echo "
SELECT epoch_no, stake_addr_hash, cert_index, slot_no, txidx  
FROM analytics.vw_bq_stake_registration
WHERE epoch_no = ${EPOCH}
        "
}

# stake registration started in epoch 208
process_epoch_f Q "stake_registration" "${BQ_PROJECT}.db_sync" 208
