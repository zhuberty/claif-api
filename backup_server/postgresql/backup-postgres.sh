#!/bin/bash

# Check if the required arguments are provided
if [ $# -lt 6 ]; then
  echo "Usage: $0 <node_ip> <node_port> <db_name> <db_user> <db_password> <backup_directory>"
  echo "Example: $0 192.168.30.10 30084 mydb myuser mypassword /mnt/postgres_backups"
  exit 1
fi

# Variables
NODE_IP=$1
NODE_PORT=$2
DB_NAME=$3
DB_USER=$4
DB_PASSWORD=$5
BACKUP_DIR=$6
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_$(date +%Y%m%d%H%M%S).sql"
LOG_FILE="/var/log/postgres_backup.log"

# Ensure the backup directory exists
mkdir -p "$BACKUP_DIR"

# Start logging
exec >> "$LOG_FILE" 2>&1
echo "Backup started at $(date) for database: $DB_NAME"

# Export the password for pg_dump
export PGPASSWORD=$DB_PASSWORD

# Perform the database dump
pg_dump -h "$NODE_IP" -p "$NODE_PORT" -U "$DB_USER" -d "$DB_NAME" -F c -f "$BACKUP_FILE"
if [ $? -ne 0 ]; then
  echo "Error backing up database: $DB_NAME"
  exit 1
else
  echo "Backup successful: $BACKUP_FILE"
fi

# Cleanup
unset PGPASSWORD

echo "Backup completed at $(date)"
