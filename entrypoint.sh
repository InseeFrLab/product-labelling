#!/bin/bash
set -e
python /app/manage.py makemigrations --noinput
python /app/manage.py migrate --noinput
exec "$@"
