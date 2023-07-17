#!/bin/bash

set -e

source ../lib/config.pg
source ../lib/functions.sh
source ../lib/config.bq

function Q() {
      local EPOCH=$1
      echo "
    SELECT fingerprint, policyid, name_bytes, epoch_no, minting
    FROM analytics.vw_bq_ma_minting
    WHERE epoch_no = ${EPOCH}"
}

# ma minting started in epoch 251
process_epoch_f Q "ma_minting" "${BQ_PROJECT}.db_sync" 251
