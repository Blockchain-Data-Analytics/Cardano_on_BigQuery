#!/bin/bash

set -e

source ../lib/config.pg
source ../lib/functions.sh
source ../lib/config.bq

function Q() {
      local EPOCH=$1
      echo "
SELECT epoch_no, stake_addr_hash, cert_index, slot_no, txidx  
FROM analytics.vw_bq_stake_deregistration
WHERE epoch_no = ${EPOCH}
        "
}

# stake deregistration started in epoch 209
process_epoch_f Q "stake_deregistration" "${BQ_PROJECT}.db_sync" 209
