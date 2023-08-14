#!/bin/bash

set -e

source ./conf/config.pg
source ./conf/config.bq

DATE=$(date +"%s")
CHECK=$((DATE / 86400 % 5 ))
if [ $CHECK -ne 3 ]; then
    echo "Not an epoch boundary. Exiting..."
#    exit 0
else
    echo "Epoch boundary, running BQ/PG deep comparison"
fi

export BQUSER=$(jq -r .client_email <<< "$BQ_CONFIG")
echo $BQ_CONFIG > ./key.json

#EPOCH_NO=$1
# calculate last full epoch number from time difference to start of mainchain
EPOCH_NO=$(( ($(date '+%s') - 1506203091) / 3600 / 24 / 5 - 1))
python3 ./deep_compare/bq_pg_deep_compare.py $EPOCH_NO
gcloud pubsub topics publish ${PUBSUB_TOPIC_NAME} --message "$(cat msg.txt)" --project $BQ_PROJECT
rm ./key.json

