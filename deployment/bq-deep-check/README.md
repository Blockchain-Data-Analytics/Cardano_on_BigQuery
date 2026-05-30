# Deep comparison on slot range

* runs every 6 hours
* covers 6.5 hours of last slots up to "HH:20"

## Docker image

```sh
docker buildx build --platform linux/amd64,linux/arm64 --tag code.blockchain-applied.com/bca/bq-deep-check:latest --tag code.blockchain-applied.com/bca/bq-deep-check:1.0.0  --push -f Dockerfile.bq-deep-check .
```


## Secrets

```sh
kubectl create secret generic credentials-pg \
  -n bq-monitoring \
  --from-literal=PGDATABASE="" \
  --from-literal=PGHOST="" \
  --from-literal=PGPORT="" \
  --from-literal=PGUSER="" \
  --from-literal=PGPASSWORD=""
```

```sh
kubectl create secret generic credentials-bq \
  -n bq-monitoring \
  --from-literal=BQ_PROJECT="" \
  --from-literal=BQ_REGION="" \
  --from-literal=PUBSUB_TOPIC_NAME=""
```

```sh
kubectl create secret generic credentials-zammad \
  -n bq-monitoring \
  --from-literal=ZAMMAD_URL="" \
  --from-literal=ZAMMAD_TOKEN=""
```

```sh
kubectl create secret generic key-bq \
  -n bq-monitoring \
  --from-file="key.json"=""
```
