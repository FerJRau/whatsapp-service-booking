#!/bin/bash
set -e

echo "Starting WhatsApp Service Booking application..."
echo "Python version: $(python --version)"
echo "Poetry version: $(poetry --version)"

exec poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
