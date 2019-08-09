#!/bin/bash
set +x

if [ -z "$VIRTUAL_ENV" ] && [ -d venv ]; then
  echo 'activate venv for celery'
  source ./venv/bin/activate
  nooutput=' >&- 2>&- <&- &'
fi

eval "celery -A run_celery.celery worker --loglevel=INFO --concurrency=1"$nooutput
