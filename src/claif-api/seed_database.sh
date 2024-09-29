#!/bin/bash

# Check if the database host is provided as an argument
if [ -z "$1" ]; then
  echo "Error: No database host provided."
  echo "Usage: ./seed_database.sh <database_host>"
  exit 1
fi

DB_HOST=$1

# Wait for the database to be available
./wait-for-db-availability.sh $DB_HOST

# Run the truncate and reset script
echo "Running truncate and reset script..."
PYTHONPATH=./ poetry run python seed_scripts/truncate_and_reset.py

# Seed the database with users
echo "Seeding users..."
PYTHONPATH=./ poetry run python seed_scripts/users.py

# Start the FastAPI app
echo "Starting FastAPI application..."
poetry run uvicorn main:app --host 0.0.0.0 --port 8000
