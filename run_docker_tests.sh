#!/bin/bash

set -eu

start_test() {
    set +eu
    IMAGE="$1"
    SCRIPT="$2"
    LOG="$(docker run -t --rm \
           -v "$PWD/$SCRIPT:/test.sh" -v "$PWD:/unix_at" \
           "$IMAGE" bash /test.sh 2>&1)"
    STATUS=$?
    echo "----------"; echo "$IMAGE"
    echo "$LOG"; echo "end $IMAGE"; echo
    exit $STATUS
}

PIDS=()

start_test centos:7 docker_centos.sh &
PIDS+=($!)
start_test centos:6 docker_centos.sh
PIDS+=($!)
start_test ubuntu:16.04 docker_debian.sh &
PIDS+=($!)
start_test debian:8 docker_debian.sh &
PIDS+=($!)

for pid in ${PIDS[*]}; do
    wait $pid
done
