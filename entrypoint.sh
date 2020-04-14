#!/bin/bash
set -e
python /app/manage.py migrate --noinput
exec "$@"
