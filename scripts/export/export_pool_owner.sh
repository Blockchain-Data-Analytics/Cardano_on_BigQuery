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
         epoch_no,
         addr_hash,
         slot_no,
         txidx
  FROM analytics.vw_bq_pool_owner
        "
      else
	echo "SELECT NULL LIMIT 0"
      fi
}

# do the query only once
process_epoch_f Q "pool_owner" "${BQ_PROJECT}.db_sync" 99999
