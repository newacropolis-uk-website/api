#!/bin/bash
set +x

celery -A run_celery.celery worker --loglevel=INFO --concurrency=4
