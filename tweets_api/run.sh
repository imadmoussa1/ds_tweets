#!/bin/bash
celery -E -A app.api.celery worker --loglevel=error &
uwsgi --ini uwsgi.ini