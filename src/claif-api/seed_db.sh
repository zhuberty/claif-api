#!/bin/bash

# Start the FastAPI application and let it create the tables
echo "Starting FastAPI application..."
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1 &

# Wait for FastAPI to be available (check if /docs is accessible)
echo "Waiting for FastAPI to start and be available..."
until curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs | grep -q "200"; do
    echo "FastAPI is not ready yet - sleeping"
    sleep 5
done
echo "FastAPI is running and tables should be created."

# Run the truncate and reset script
echo "Running truncate and reset script..."
PYTHONPATH=./ poetry run python seed_scripts/truncate_and_reset.py

# Seed the database with users
echo "Seeding users..."
PYTHONPATH=./ poetry run python seed_scripts/users.py
