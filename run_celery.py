#!/usr/bin/env python

from flask import Flask

from app import celery, create_app  # noqa


application = create_app()
application.app_context().push()
