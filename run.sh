#!/bin/bash
uwsgi --ini uwsgi.ini
celery -A app.api.celery worker --loglevel=info