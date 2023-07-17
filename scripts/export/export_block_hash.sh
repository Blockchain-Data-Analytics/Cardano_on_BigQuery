#!/bin/bash

set -e

source ../lib/config.pg
source ../lib/functions.sh
source ../lib/config.bq

function Q() {
      local EPOCH=$1
      echo "
  SELECT epoch_no, slot_no, block_hash
  FROM analytics.vw_bq_block_hash
  WHERE epoch_no = ${EPOCH}"
}

process_epoch_f Q "block_hash" "${BQ_PROJECT}.db_sync" 330

