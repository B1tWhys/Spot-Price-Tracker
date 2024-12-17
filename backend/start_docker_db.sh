#!/bin/bash

# Note: This is only for local development, see the k8s configs for the production database setup

CONTAINER_NAME="spt-db"

docker stop $CONTAINER_NAME 2>/dev/null
docker rm $CONTAINER_NAME 2>/dev/null

IMAGE="timescale/timescaledb-ha:pg17"
docker run --name $CONTAINER_NAME \
  -p 5432:5432 \
  -e POSTGRES_HOST_AUTH_METHOD=trust \
  -d \
   -v "$(pwd)/pg-data:/home/postgres/pgdata/data" \
  $IMAGE

echo "Waiting 5 seconds for the container to start up"
sleep 5
echo "Bootstrapping the DB schema"

export DATABASE_URL="timescaledb://postgres@localhost:5432/postgres"
poetry run alembic upgrade head