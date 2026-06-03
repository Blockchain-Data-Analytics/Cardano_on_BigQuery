#!/usr/bin/env bash

set -e

source ./conf/config.pg
source ./conf/config.bq
source ./functions.sh

function Q() {
      local EPOCH=$1
        echo "
 SELECT active_epoch_no,
        pool_hash,
        cert_index,
        vrf_key_hash,
        pledge,
        reward_addr,
        margin,
        fixed_cost,
        registered_tx_hash,
        epoch_no,
        metadata_url,
        metadata_hash,
        metadata_registered_tx_hash
  FROM analytics.vw_bq_pool_update
  WHERE epoch_no = ${EPOCH} "
}

# do the query only once
process_one_epoch_f Q "pool_update" "${BQ_PROJECT}.db_sync" $1
