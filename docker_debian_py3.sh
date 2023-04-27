#!/bin/bash

set -eux

apt-get update
apt-get install -yy at python3 python3-pip python3-venv
atd &
python3 -m venv venv
. venv/bin/activate
cd /unix_at
pip3 install .
python3 tests.py
