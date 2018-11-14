#!/bin/bash

dnf install -yy at python python-pip
atd &
cd /unix_at
pip install .
python tests.py
