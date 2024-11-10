#!/bin/bash

# Check if the required arguments are provided
if [ $# -lt 6 ]; then
  echo "Usage: $0 <node_ip> <node_port> <db_name> <db_user> <db_password> <backup_directory> [<num_backups_to_keep>]"
  echo "Example: $0 192.168.30.10 30084 mydb myuser mypassword /mnt/postgres_backups 10"
  exit 1
fi

# Variables
NODE_IP=$1
NODE_PORT=$2
DB_NAME=$3
DB_USER=$4
DB_PASSWORD=$5
BACKUP_DIR=$6
NUM_BACKUPS=${7:-10} # Default to 10 if not provided
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_$(date +%Y%m%d%H%M%S).sql"
LOG_FILE="/tmp/postgres_backup.log"

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
  unset PGPASSWORD
  exit 1
else
  echo "Backup successful: $BACKUP_FILE"
fi

# Cleanup
unset PGPASSWORD

# Manage backup retention
echo "Managing backup retention to keep the last $NUM_BACKUPS backups."
echo "Looking for backups with pattern: ${DB_NAME}_*.sql in ${BACKUP_DIR}"
BACKUPS=($(find "${BACKUP_DIR}" -name "${DB_NAME}_*.sql" -type f | sort -r))

if [ ${#BACKUPS[@]} -gt 0 ]; then
  echo "Found ${#BACKUPS[@]} backups."
  if [ ${#BACKUPS[@]} -gt $NUM_BACKUPS ]; then
    DELETE_COUNT=$((${#BACKUPS[@]} - $NUM_BACKUPS))
    echo "Deleting $DELETE_COUNT old backups."
    for ((i=$NUM_BACKUPS; i<${#BACKUPS[@]}; i++)); do
      echo "Deleting old backup: ${BACKUPS[$i]}"
      rm -f "${BACKUPS[$i]}"
    done
  else
    echo "No old backups to delete."
  fi
else
  echo "No backups found to manage."
fi

echo "Backup completed at $(date)"
