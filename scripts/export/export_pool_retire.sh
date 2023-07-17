#!/bin/bash

set -e

source ../lib/config.pg
source ../lib/functions.sh
source ../lib/config.bq

function Q() {
      local EPOCH=$1
      if [ $EPOCH -eq 99999 ]; then
        echo "
  SELECT pool_hash,
         retiring_epoch,
         epoch_no,
         cert_index,
         announced_tx_hash,
         slot_no,
         announced_txidx
  FROM analytics.vw_bq_pool_retire
        "
      else
	echo "SELECT NULL LIMIT 0"
      fi
}

# do the query only once
process_epoch_f Q "pool_retire" "${BQ_PROJECT}.db_sync" 99999
