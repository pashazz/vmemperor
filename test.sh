#!/bin/sh
export PYTHONPATH=$PWD
cd tests
python3 -m unittest test_xenadapter$@
cd -
