#!/bin/bash

set -eux

apt-get update
apt-get install -yy at python python-pip
atd &
cd /unix_at
pip install .
python tests.py
