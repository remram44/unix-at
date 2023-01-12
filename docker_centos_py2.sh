#!/bin/bash

set -eux

yum install -yy epel-release
yum install -yy at python python-pip
atd &
cd /unix_at
pip install .
python tests.py
