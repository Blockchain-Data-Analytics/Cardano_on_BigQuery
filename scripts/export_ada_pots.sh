#!/bin/bash

set -e

source ./conf/config.pg
source ./conf/config.bq
source ./functions.sh

TNAME="ada_pots"

function Q() {
      local EPOCH=$1
      if [ $EPOCH -eq 99999 ]; then
        echo "
  SELECT epoch_no, slot_no,
         treasury, reserves, rewards, utxo,
         deposits, fees
  FROM public.${TNAME}
        "
      else
	echo "SELECT NULL LIMIT 0"
      fi
}

# do the query only once
process_epoch_f Q "${TNAME}" "${BQ_PROJECT}.db_sync" 99999
