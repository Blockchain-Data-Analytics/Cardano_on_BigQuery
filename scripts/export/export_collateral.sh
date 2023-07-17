#!/bin/bash

set -e

source ../lib/config.pg
source ../lib/functions.sh
source ../lib/config.bq

function Q() {
      local EPOCH=$1
      echo "
    SELECT epoch_no, slot_no, txidx,
        epoch_no_out, slot_no_out, txidx_out, tx_out_index	
    FROM analytics.vw_bq_collateral
    WHERE epoch_no = ${EPOCH} "
}

# starts with epoch 290
process_epoch_f Q "collateral" "${BQ_PROJECT}.db_sync" 340
