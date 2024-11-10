#!/bin/bash

# Check if the required arguments are provided
if [ $# -lt 6 ]; then
  echo "Usage: $0 <node_ip> <node_port> <db_name> <db_user> <db_password> <backup_file> [<log_file>]"
  echo "Example: $0 192.168.30.10 30084 mydb myuser mypassword /mnt/postgres_backups/mydb_20211001010101.sql /var/log/postgres_restore.log"
  exit 1
fi

# Variables
NODE_IP=$1
NODE_PORT=$2
DB_NAME=$3
DB_USER=$4
DB_PASSWORD=$5
BACKUP_FILE=$6
LOG_FILE=${7:-/tmp/postgres_restore.log} # Default to /tmp/postgres_restore.log if not provided

# Check if the backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
  echo "Backup file $BACKUP_FILE does not exist."
  exit 1
fi

# Confirmation prompt
echo "WARNING: This operation will restore the database '$DB_NAME' on '$NODE_IP:$NODE_PORT' from backup file '$BACKUP_FILE'."
read -p "Are you sure you want to proceed? This will overwrite the existing database. (y/n): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "Restore operation canceled."
  exit 0
fi

# Start logging
exec >> "$LOG_FILE" 2>&1
echo "Restore started at $(date) for database: $DB_NAME"

# Export the password for pg_restore
export PGPASSWORD=$DB_PASSWORD

# Drop the existing database
echo "Dropping the existing database '$DB_NAME'..."
psql -h "$NODE_IP" -p "$NODE_PORT" -U "$DB_USER" -c "DROP DATABASE IF EXISTS \"$DB_NAME\";"
if [ $? -ne 0 ]; then
  echo "Error dropping the database '$DB_NAME'."
  unset PGPASSWORD
  exit 1
fi

# Create a new database
echo "Creating a new database '$DB_NAME'..."
psql -h "$NODE_IP" -p "$NODE_PORT" -U "$DB_USER" -c "CREATE DATABASE \"$DB_NAME\";"
if [ $? -ne 0 ]; then
  echo "Error creating the database '$DB_NAME'."
  unset PGPASSWORD
  exit 1
fi

# Restore the database from the backup file
echo "Restoring the database from backup file '$BACKUP_FILE'..."
pg_restore -h "$NODE_IP" -p "$NODE_PORT" -U "$DB_USER" -d "$DB_NAME" -v "$BACKUP_FILE"
if [ $? -ne 0 ]; then
  echo "Error restoring the database '$DB_NAME' from '$BACKUP_FILE'."
  unset PGPASSWORD
  exit 1
else
  echo "Restore successful."
fi

# Cleanup
unset PGPASSWORD

echo "Restore completed at $(date)"
