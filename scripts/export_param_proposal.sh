#!/usr/bin/env bash

set -e

source ./conf/config.pg
source ./conf/config.bq
source ./functions.sh

function Q() {
      local EPOCH=$1
      if [ $EPOCH -eq 99999 ]; then
        echo "
    SELECT epoch_no, params
    FROM analytics.vw_bq_param_proposal
          "
      else
	echo "SELECT NULL LIMIT 0"
      fi
}

# do the query only once
process_epoch_f Q "param_proposal" "${BQ_PROJECT}.db_sync" 99999
