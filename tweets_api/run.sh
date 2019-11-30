#!/bin/bash
celery -E -A app.api.celery worker -B --loglevel=error &
# celery -A app.api.celery beat --loglevel=error &
uwsgi --ini uwsgi.ini