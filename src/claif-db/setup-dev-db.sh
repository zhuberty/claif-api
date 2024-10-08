#!/bin/bash
set -e

# Export the password so psql can use it without prompting
export PGPASSWORD=$POSTGRESQL_PASSWORD

psql -v ON_ERROR_STOP=1 --username "$POSTGRESQL_USERNAME" --dbname "$POSTGRESQL_DATABASE" <<-EOSQL
    CREATE USER claif_db_user WITH PASSWORD 'claif_db_password';
    CREATE DATABASE claif_db;
    GRANT ALL PRIVILEGES ON DATABASE claif_db TO claif_db_user;
EOSQL

# Unset the password after it's used for security reasons
unset PGPASSWORD
