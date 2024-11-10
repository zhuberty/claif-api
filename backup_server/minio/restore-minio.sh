#!/bin/bash

# Full path to mc
MC_PATH="/usr/local/bin/mc"

# Check if the required arguments are provided
if [ $# -lt 2 ]; then
  echo "Usage: $0 <minio_alias> <backup_directory>"
  echo "Example: $0 claif-api-minio /mnt/minio_backups"
  exit 1
fi

# Variables
MINIO_ALIAS=$1                          # MinIO alias passed as the first argument
BACKUP_ROOT=$2                          # Backup directory passed as the second argument
LOG_FILE="/tmp/minio_restore.log"       # Log file for restore operations

# Ensure the backup directory exists
if [ ! -d "$BACKUP_ROOT" ]; then
  echo "Backup directory $BACKUP_ROOT does not exist."
  exit 1
fi

# Confirmation prompt
echo "WARNING: This operation will restore data from '$BACKUP_ROOT' to '$MINIO_ALIAS'."
read -p "Are you sure you want to proceed? (y/n): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "Restore operation canceled."
  exit 0
fi

# Start logging
exec >> "$LOG_FILE" 2>&1
echo "Restore started at $(date)"

# Get the list of buckets from the backup directory
echo "Fetching the list of buckets from $BACKUP_ROOT..."
BUCKETS=$(find "$BACKUP_ROOT" -mindepth 1 -maxdepth 1 -type d -printf "%f\n")

# Check if fetching buckets was successful
if [ -z "$BUCKETS" ]; then
  echo "No buckets found in backup directory $BACKUP_ROOT."
  exit 1
fi

# Loop through each bucket and perform the mirror
for BUCKET_NAME in $BUCKETS
do
  echo "Restoring $BUCKET_NAME..."

  # Check if bucket exists in MinIO
  $MC_PATH ls $MINIO_ALIAS/$BUCKET_NAME > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    echo "Bucket $BUCKET_NAME does not exist in $MINIO_ALIAS. Creating bucket..."
    $MC_PATH mb $MINIO_ALIAS/$BUCKET_NAME
    if [ $? -ne 0 ]; then
      echo "Failed to create bucket $BUCKET_NAME in $MINIO_ALIAS."
      continue
    else
      echo "Bucket $BUCKET_NAME created."
    fi
  else
    echo "Bucket $BUCKET_NAME already exists in $MINIO_ALIAS."
  fi

  # Mirror the content from backup to MinIO bucket
  $MC_PATH mirror --overwrite --md5 "$BACKUP_ROOT/$BUCKET_NAME" $MINIO_ALIAS/$BUCKET_NAME
  if [ $? -ne 0 ]; then
    echo "Error restoring $BUCKET_NAME"
    # Optionally, send an email or alert here
  else
    echo "Successfully restored $BUCKET_NAME"
  fi
done

echo "Restore completed at $(date)"
