#!/bin/bash

set -e

source ./conf/config.pg
source ./conf/config.bq
source ./functions.sh

function Q() {
      local EPOCH=$1
      echo "
    SELECT fingerprint, policyid, name_bytes, epoch_no, minting
    FROM analytics.vw_bq_ma_minting
    WHERE epoch_no = ${EPOCH}"
}

# ma minting started in epoch 251
process_epoch_f Q "ma_minting" "${BQ_PROJECT}.db_sync" 251
