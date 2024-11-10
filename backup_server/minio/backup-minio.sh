#!/bin/bash

# Full path to mc
MC_PATH="/usr/local/bin/mc"

# Check if the required arguments are provided
if [ $# -lt 2 ]; then
  echo "Usage: $0 <minio_alias> <backup_directory>"
  echo "Example: $0 myminio /mnt/minio_backups"
  exit 1
fi

# Variables
MINIO_ALIAS=$1                          # MinIO alias passed as the first argument
BACKUP_ROOT=$2                          # Backup directory passed as the second argument
LOG_FILE="/tmp/minio_backup.log"   # Log file for backup operations

# Ensure the backup directory exists
mkdir -p "$BACKUP_ROOT"

# Start logging
exec >> "$LOG_FILE" 2>&1
echo "Backup started at $(date)"

# Get the list of buckets dynamically
echo "Fetching the list of buckets from $MINIO_ALIAS..."
BUCKETS=$($MC_PATH ls $MINIO_ALIAS | awk '{print $NF}' | tr -d '/')

# Check if fetching buckets was successful
if [ -z "$BUCKETS" ]; then
  echo "No buckets found or error retrieving bucket list from $MINIO_ALIAS."
  exit 1
fi

# Loop through each bucket and perform the mirror
for BUCKET_NAME in $BUCKETS
do
  echo "Backing up $BUCKET_NAME..."
  $MC_PATH mirror --md5 $MINIO_ALIAS/$BUCKET_NAME "$BACKUP_ROOT/$BUCKET_NAME"
  if [ $? -ne 0 ]; then
    echo "Error backing up $BUCKET_NAME"
    # Optionally, send an email or alert here
  else
    echo "Successfully backed up $BUCKET_NAME"
  fi
done

echo "Backup completed at $(date)"
