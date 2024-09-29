#!/bin/bash

# Start the seed scripts in the background as a single process
{
    echo "Waiting for FastAPI to start and be available..."
    until curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs | grep -q "200"; do
        echo "FastAPI is not ready yet - sleeping"
        sleep 5
    done
    echo "FastAPI is running and tables should be created."

    # Run the truncate and reset all tables for the api database
    echo "Running truncate and reset script..."
    PYTHONPATH=./ poetry run python seed_scripts/truncate_and_reset.py

    # Populate the database with seed (dummy) data
    echo "Seeding users..."
    PYTHONPATH=./ poetry run python seed_scripts/users.py

    echo "Seeding terminal recordings and annotations..."
    PYTHONPATH=./ poetry run python seed_scripts/terminal_recordings.py
} &

# Start the FastAPI application in the foreground
echo "Starting up FastAPI application to create tables..."
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
