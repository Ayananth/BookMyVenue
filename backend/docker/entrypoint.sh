#!/bin/sh
set -e

cd /app/core

# Only the web server runs migrations; Celery reuses this image.
if [ "$1" != "celery" ]; then
  python manage.py migrate --noinput
fi

exec "$@"
