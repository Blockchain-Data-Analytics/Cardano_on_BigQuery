#!/bin/bash

set -e

source ../lib/config.pg
source ../lib/functions.sh
source ../lib/config.bq

function Q() {
      local EPOCH=$1
      if [ $EPOCH -eq 99999 ]; then
        echo "
  SELECT 
         pool_hash,
         epoch_no,
         ticker_name,
         json,
         metadata_url,
         metadata_hash,
         metadata_registered_tx_hash
  FROM analytics.vw_bq_pool_offline_data 
        "
      else
	echo "SELECT NULL LIMIT 0"
      fi
}

# do the query only once
process_epoch_f Q "pool_offline_data" "${BQ_PROJECT}.db_sync" 99999