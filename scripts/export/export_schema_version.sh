#!/bin/bash

set -e

source ../lib/config.pg
source ../lib/functions.sh
source ../lib/config.bq

function Q() {
      local EPOCH=$1
      if [ $EPOCH -eq 99999 ]; then
        echo "
  SELECT stage_one,
         stage_two,
         stage_three
  FROM public.schema_version 
        "
      else
	echo "SELECT NULL LIMIT 0"
      fi
}

# do the query only once
process_epoch_f Q "schema_version" "${BQ_PROJECT}.db_sync" 99999
