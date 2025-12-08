#!/bin/bash

set -eux

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -yy at python python-pip
atd &
cd /unix_at
pip install .
python tests.py
