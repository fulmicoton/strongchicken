#!/bin/bash

VIRTUALENV_DIR=`pwd`/../../virtualenv_test_strongchicken
virtualenv --no-site-packages $VIRTUALENV_DIR
source $VIRTUALENV_DIR/bin/activate
cd ../ && python setup.py install
# TODO test more than just import
python -c "from strongchicken import *"
rm -fr $VIRTUALENV_DIR
