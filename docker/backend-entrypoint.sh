#!/bin/sh
set -e

echo "[backend-entrypoint] running database migrations"
alembic upgrade head

echo "[backend-entrypoint] seeding demo data"
python seed.py

echo "[backend-entrypoint] starting api server on port ${PORT:-8000}"
exec python -m uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
