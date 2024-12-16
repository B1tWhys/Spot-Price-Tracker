#!/bin/bash

CONTAINER_NAME="spt-db"
IMAGE="timescale/timescaledb-ha:pg17"
docker run --name $CONTAINER_NAME -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust -d $IMAGE
