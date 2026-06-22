#!/usr/bin/env bash
set -o errexit

python manage.py migrate --noinput
python manage.py collectstatic --noinput

gunicorn student_management.wsgi --preload --workers 4 --timeout 120 --access-logfile - --error-logfile -
