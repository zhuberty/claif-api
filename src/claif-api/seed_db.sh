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

# Run the truncate and reset all tables for the api database
# as a convenience for onboarding, development, and testing.
echo "Running truncate and reset script..."
PYTHONPATH=./ poetry run python seed_scripts/truncate_and_reset.py

# Now we'll populate the database with seed (dummy) data for
# development and testing purposes.
echo "Seeding users..."
PYTHONPATH=./ poetry run python seed_scripts/users.py

echo "Seeding terminal recordings and annotations..."
PYTHONPATH=./ poetry run python seed_scripts/terminal_recordings.py
