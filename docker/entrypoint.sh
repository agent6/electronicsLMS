#!/bin/sh
set -eu

wait_for_database() {
  if [ -z "${DATABASE_URL:-}" ] && [ -z "${DB_HOST:-}" ]; then
    return 0
  fi

  retries="${DJANGO_DB_WAIT_RETRIES:-30}"
  delay="${DJANGO_DB_WAIT_SECONDS:-2}"
  attempt=1

  while [ "$attempt" -le "$retries" ]; do
    if python - <<'PY'
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "obsoletehq.settings")

import django
from django.db import connection

django.setup()
connection.ensure_connection()
PY
    then
      return 0
    fi

    echo "Database is not ready yet (${attempt}/${retries}); retrying in ${delay}s..."
    attempt=$((attempt + 1))
    sleep "$delay"
  done

  echo "Database did not become ready in time."
  return 1
}

if [ "${DJANGO_RUN_MIGRATIONS:-true}" = "true" ]; then
  wait_for_database
  python manage.py migrate --noinput
fi

if [ "${DJANGO_SEED_ON_STARTUP:-true}" = "true" ]; then
  python manage.py seed_obsoletehq
fi

exec "$@"
