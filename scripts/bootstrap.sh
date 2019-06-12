#!/bin/bash
if [ ! -d "venv" ]; then
    virtualenv venv
fi

if [ -z "$VIRTUAL_ENV" ] && [ -d venv ]; then
  echo 'activate venv'
  source ./venv/bin/activate
fi

pip install google-cloud-logging
pip install -r requirements_tests.txt
