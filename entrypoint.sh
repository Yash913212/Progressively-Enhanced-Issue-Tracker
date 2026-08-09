#!/bin/sh
set -e

echo "[entrypoint] Waiting for PostgreSQL to be ready..."
python - <<'PY'
import os
import time

import psycopg2

db_url = os.environ.get("DATABASE_URL", "")
conn_params = {}
if db_url:
    # django-environ style URL: postgres://user:pass@host:port/dbname
    from urllib.parse import urlparse

    parsed = urlparse(db_url)
    conn_params = {
        "host": parsed.hostname or "db",
        "port": parsed.port or 5432,
        "user": parsed.username or "tracker_user",
        "password": parsed.password or "tracker_password",
        "dbname": parsed.path.lstrip("/") or "tracker_db",
    }
else:
    conn_params = {
        "host": os.environ.get("POSTGRES_HOST", "db"),
        "port": os.environ.get("POSTGRES_PORT", 5432),
        "user": os.environ.get("POSTGRES_USER", "tracker_user"),
        "password": os.environ.get("POSTGRES_PASSWORD", "tracker_password"),
        "dbname": os.environ.get("POSTGRES_DB", "tracker_db"),
    }

for attempt in range(60):
    try:
        conn = psycopg2.connect(**conn_params)
        conn.close()
        print("[entrypoint] PostgreSQL is ready.")
        break
    except psycopg2.OperationalError:
        if attempt == 59:
            raise
        time.sleep(1)
else:
    raise SystemExit("Could not connect to PostgreSQL after 60 attempts.")
PY

echo "[entrypoint] Running migrations..."
python manage.py migrate --noinput

echo "[entrypoint] Seeding database..."
python manage.py seed_data

echo "[entrypoint] Collecting static files..."
python manage.py collectstatic --noinput

echo "[entrypoint] Starting Gunicorn..."
exec gunicorn issuetracker.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
