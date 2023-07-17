#!/bin/bash

set -e

source ../lib/config.pg
source ../lib/functions.sh
source ../lib/config.bq

function Q() {
      local EPOCH=$1
      echo "
   SELECT *
   FROM analytics.vw_bq_rel_addr_txout(${EPOCH})
      "
}
function transform_csv() {
	local FNAME=$1
    $SED -i -e ':a /",/ { bb; }; /,"[^"]\+$/ { N; s/\n//g; ba; }; :b' ${FNAME}
    return 0
}

process_epoch_f Q "rel_addr_txout" "${BQ_PROJECT}.db_sync" 0
