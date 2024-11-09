
# MinIO Backup Script

This script dynamically fetches the list of buckets from a MinIO server alias and mirrors their contents to a specified backup directory. It ensures all buckets are backed up efficiently while logging the operation for auditing purposes.

## Features

- Dynamically retrieves all buckets from a MinIO alias using the `mc` (MinIO Client) command.
- Mirrors bucket contents to a user-specified backup directory.
- Logs all operations to `/var/log/mirror_backup.log`.
- Accepts both the MinIO alias and backup directory as arguments for flexibility.

## Prerequisites

- [MinIO Client (mc)](https://min.io/docs/minio/linux/reference/minio-mc.html) installed and configured.
  - Ensure an alias (e.g., `myminio`) is set up using:
    ```bash
    mc alias set myminio http://<minio-server> <access-key> <secret-key>
    ```
- Sufficient disk space in the specified backup directory.
- Script requires `bash` shell.

## Usage

Run the script with the MinIO alias and desired backup directory as arguments:

```bash
./backup_script.sh <minio_alias> <backup_directory>
```

### Example

To back up MinIO buckets from the alias `myminio` to `/mnt/minio_backups`:

```bash
./backup_script.sh myminio /mnt/minio_backups
```

### Logs

All operations are logged to `/var/log/mirror_backup.log`. You can monitor this file to track the status of the backups:

```bash
tail -f /var/log/mirror_backup.log
```

## Automating Backups with Cronjob

You can automate the script to run at regular intervals using a cronjob. Here's how to set it up:

1. Open the crontab file for editing:
   ```bash
   crontab -e
   ```

2. Add a new cronjob entry to run the script. For example:
   ```bash
   0 2 * * * /path/to/backup_script.sh myminio /mnt/minio_backups
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

## Error Handling

- If no buckets are found or there is an error retrieving the bucket list, the script will exit with an error message.
- If a backup operation fails for a specific bucket, the script logs the error and continues with the next bucket.

## Backup Location Considerations

Choose a backup directory based on your system setup:
- **Local Disk**: `/mnt/minio_backups` or a similar dedicated directory.
- **Network Storage**: Use a NAS mount point, e.g., `/mnt/nas/backups`.
- **External Storage**: Mount an external drive, e.g., `/media/backup_drive`.

Ensure the directory has adequate disk space and is accessible by the script.

## Notes

- Ensure the `mc` alias (`myminio`) is configured and working before running the script.
- Verify that the backup directory has appropriate permissions and sufficient disk space.
- The script creates the backup directory if it does not already exist.
