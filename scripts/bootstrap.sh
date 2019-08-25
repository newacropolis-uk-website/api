#!/bin/bash
sudo pip install virtualenv --upgrade
pip install -U setuptools

if [ ! -d "venv" ]; then
    virtualenv venv
fi

if [ -z "$VIRTUAL_ENV" ] && [ -d venv ]; then
  echo 'activate venv'
  source ./venv/bin/activate
fi

pip install -r requirements_tests.txt
pip install google-cloud-logging==1.11.0
