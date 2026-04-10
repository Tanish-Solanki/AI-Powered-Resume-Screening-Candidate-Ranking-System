#!/bin/bash
set -e

echo "Running Database Migrations natively..."
alembic upgrade head

echo "Starting FastAPI Production Server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000
