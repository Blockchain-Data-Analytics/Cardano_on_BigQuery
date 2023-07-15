#!/bin/bash

set -e

source ../lib/config.pg
source ../lib/functions.sh

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
process_epoch_f Q "schema_version" "iog-data-analytics.db_sync" 99999
