
# MinIO Backup Script

This script dynamically fetches the list of buckets from a MinIO server alias and mirrors their contents to a specified backup directory. It ensures all buckets are backed up efficiently while logging the operation for auditing purposes.

## Features

- Dynamically retrieves all buckets from a MinIO alias using the `mc` (MinIO Client) command.
- Mirrors bucket contents to a user-specified backup directory.
- Logs all operations to `/tmp/minio_backup.log`.
- Accepts both the MinIO alias and backup directory as arguments for flexibility.

## Prerequisites

### Install Dependencies

- **Install MinIO Client (`mc`)**:
  ```bash
  wget https://dl.min.io/client/mc/release/linux-amd64/mc
  chmod +x mc
  sudo mv mc /usr/local/bin/
  ```

  Ensure the client is correctly installed by running:
  ```bash
  mc --version
  ```

- **Set Up MinIO Alias**:
  Configure the MinIO client with an alias:
  ```bash
  mc alias set claif-api-minio http://<minio-server> <access-key> <secret-key>
  ```

- Sufficient disk space in the specified backup directory.
- Script requires `bash` shell.

## Usage

Run the script with the MinIO alias and desired backup directory as arguments:

```bash
./backup_script.sh <minio_alias> <backup_directory>
```

### Example

To back up MinIO buckets from the alias `claif-api-minio` to `/mnt/minio_backups`:

```bash
./backup_script.sh claif-api-minio /mnt/minio_backups
```

### Logs

All operations are logged to `/tmp/minio_backup.log`. You can monitor this file to track the status of the backups:

```bash
tail -f /tmp/minio_backup.log
```

## Automating Backups with Cronjob

You can automate the script to run at regular intervals using a cronjob. Here's how to set it up:

1. Open the crontab file for editing:
   ```bash
   crontab -e
   ```

2. Add a new cronjob entry to run the script. For example:
   ```bash
   0 2 * * * /path/to/backup_script.sh claif-api-minio /mnt/minio_backups
   ```

   This example runs the script daily at 2:00 AM.

3. Save and exit the editor. The cronjob will now run the script automatically at the specified time.

### Verifying the Cronjob

- Check the cron log to confirm the job runs as expected:
  ```bash
  grep CRON /var/log/syslog
  ```

- Ensure the script has executable permissions:
  ```bash
  chmod +x /path/to/backup_script.sh
  ```

## Notes

- Ensure the `mc` alias (`claif-api-minio`) is configured and working before running the script.
- Verify that the backup directory has appropriate permissions and sufficient disk space.
- The script creates the backup directory if it does not already exist.
- Logs are stored in `/tmp/minio_backup.log`. You can customize this path in the script if needed.

## Error Handling

- If the bucket list retrieval fails, the script exits with an error.
- If the mirror operation for a bucket fails, the script logs an error for that specific bucket and continues with the next bucket.
