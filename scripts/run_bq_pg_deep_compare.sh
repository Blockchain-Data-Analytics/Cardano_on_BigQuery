#!/bin/bash

set -e

source ./conf/config.bq

DATE=$(date +"%s")
CHECK=$((DATE / 86400 % 5 ))
if [ $CHECK -ne 3 ]; then
    echo "Not an epoch boundary. Exiting..."
    exit 0
else
    echo "Epoch boundary, running BQ/PG deep comparison"
fi

export PGPASSWORD=$(jq -r .password <<< "$DB_CONFIG")
export PGHOST=$(jq -r .host <<< "$DB_CONFIG")
export PGDATABASE=$(jq -r .dbname <<< "$DB_CONFIG")
export PGDATABASE_TESTNET=$(jq -r .dbname_test <<< "$DB_CONFIG")
export PGPORT=$(jq -r .port <<< "$DB_CONFIG")
export PGUSER=$(jq -r .username <<< "$DB_CONFIG")

export BQUSER=$(jq -r .client_email <<< "$BQ_CONFIG")
echo $BQ_CONFIG > ./key.json

EPOCH_NO=$1
python3 ./deep_compare/bq_pg_deep_compare.py $EPOCH_NO
gcloud pubsub topics publish ${PUBSUB_TOPIC_NAME} --message "$(cat msg.txt)" --project $BQ_PROJECT
rm ./key.json

