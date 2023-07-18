#!/bin/bash

set -e

source ./conf/config.pg
source ./conf/config.bq
source ./functions.sh

function Q() {
      local EPOCH=$1
      if [ $EPOCH -eq 99999 ]; then
        echo "
  SELECT start_time,
         network_name,
         version
  FROM public.meta 
        "
      else
	echo "SELECT NULL LIMIT 0"
      fi
}

# do the query only once
process_epoch_f Q "meta" "${BQ_PROJECT}.db_sync" 99999
