#!/bin/bash

if [ "$#" != 0 ]; then
    IMAGE="$1"
    SCRIPT="$2"
    LOG="$(docker run -t --rm \
           -v "$PWD/$SCRIPT:/test.sh" -v "$PWD:/unix_at" \
           "$IMAGE" bash /test.sh 2>&1)"
    STATUS=$?
    echo "----------"; echo "$IMAGE"
    echo "$LOG"; echo "end $IMAGE"; echo
    exit $STATUS
fi

set -eu

PIDS=()

bash "$0" centos:7 docker_centos_py2.sh &
PIDS+=($!)
#bash "$0" centos:6 docker_centos_py2.sh &  # python==2.6, dateutil doesn't work
#PIDS+=($!)
bash "$0" ubuntu:16.04 docker_debian_py2.sh &
PIDS+=($!)
bash "$0" ubuntu:22.04 docker_debian_py3.sh &
PIDS+=($!)
bash "$0" debian:10 docker_debian_py2.sh &
PIDS+=($!)
bash "$0" debian:11 docker_debian_py3.sh &
PIDS+=($!)
bash "$0" debian:testing docker_debian_py3.sh &
PIDS+=($!)

for pid in ${PIDS[*]}; do
    wait $pid
done
