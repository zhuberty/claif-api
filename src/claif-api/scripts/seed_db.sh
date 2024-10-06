#!/bin/bash

log() {
    echo -e "seed_db.sh:$1:\t$2"
}

# Start the seed scripts in the background as a single process
{
    log INFO "Waiting for FastAPI to start and be available..."
    until curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs | grep -q "200"; do
        log INFO "FastAPI is not ready yet - sleeping"
        sleep 5
    done
    log INFO "FastAPI is running and tables should be created."

    # Run the truncate and reset all tables for the api database
    log INFO "Running truncate and reset script..."
    PYTHONPATH=./ poetry run python scripts/truncate_and_reset.py

    # Populate the database with seed (dummy) data
    log INFO "Seeding users..."
    PYTHONPATH=./ poetry run python scripts/seed_users.py

    log INFO "Running integration tests..."
    PYTHONPATH=./ poetry run pytest -s -v ./tests
} &

# Start the FastAPI application in the foreground
log INFO "Starting up FastAPI application to create tables..."
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
