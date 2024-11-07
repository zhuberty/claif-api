#!/bin/bash
set -e

echo "Starting database setup script..."

# Check and display environment variables (excluding passwords)
echo "Environment Variables:"
echo "  POSTGRESQL_USERNAME: $POSTGRESQL_USERNAME"
echo "  POSTGRESQL_DATABASE: $POSTGRESQL_DATABASE"
echo "  DB_USER: $DB_USER"
echo "  DB_NAME: $DB_NAME"
echo

# Verify that required environment variables are set
MISSING_VARS=false
for VAR_NAME in POSTGRESQL_USERNAME POSTGRESQL_PASSWORD POSTGRESQL_DATABASE DB_USER DB_PASSWORD DB_NAME; do
  if [ -z "${!VAR_NAME}" ]; then
    echo "Error: Environment variable $VAR_NAME is not set."
    MISSING_VARS=true
  fi
done

if [ "$MISSING_VARS" = true ]; then
  echo "One or more required environment variables are missing. Exiting."
  exit 1
fi

# Export the password so psql can use it without prompting
export PGPASSWORD="$POSTGRESQL_PASSWORD"

echo "Connecting to PostgreSQL database '$POSTGRESQL_DATABASE' as user '$POSTGRESQL_USERNAME'..."
echo

# Execute SQL commands with verbose output
psql -v ON_ERROR_STOP=1 --username "$POSTGRESQL_USERNAME" --dbname "$POSTGRESQL_DATABASE" <<EOSQL
\echo 'Creating user $DB_USER...'
CREATE USER "$DB_USER" WITH PASSWORD '$DB_PASSWORD';

\echo 'Creating database $DB_NAME...'
CREATE DATABASE "$DB_NAME";

\echo 'Granting all privileges on database $DB_NAME to user $DB_USER...'
GRANT ALL PRIVILEGES ON DATABASE "$DB_NAME" TO "$DB_USER";
EOSQL

if [ $? -eq 0 ]; then
  echo
  echo "Database setup completed successfully."
else
  echo
  echo "Database setup failed."
  exit 1
fi

unset PGPASSWORD
