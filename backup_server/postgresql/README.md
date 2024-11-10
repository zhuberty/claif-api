
# PostgreSQL Backup Script

This script connects to a PostgreSQL database exposed on a Kubernetes node and performs a database dump. The dump can be stored locally and optionally transferred to a backup server.

## Prerequisites

### Install Dependencies

- **Install PostgreSQL Client Tools**:
  Install `pg_dump` and related tools:
  ```bash
  sudo apt update
  sudo apt install postgresql-client -y
  ```

  Verify the installation:
  ```bash
  pg_dump --version
  ```

- **Install SCP for File Transfers**:
  Ensure `scp` is installed for transferring backup files:
  ```bash
  sudo apt install openssh-client -y
  ```

## Usage

```bash
./backup_postgres.sh <node_ip> <node_port> <db_name> <db_user> <db_password> <backup_directory> [<num_backups_to_keep>] [<log_file>]
```

### Example

To back up a database `mydb` running on `192.168.30.10:30084` and retain the last 10 backups:

```bash
./backup_postgres.sh 192.168.30.10 30084 mydb myuser mypassword /mnt/postgres-backups 10 /var/log/postgres-backup.log
```

### Logs

Logs are stored in `/var/log/postgres-backup.log` by default. You can monitor this file for backup status:

```bash
tail -f /var/log/postgres-backup.log
```

### Automating with Cronjob

Automate the script to run periodically using a cronjob:

1. Edit the crontab file:
   ```bash
   crontab -e
   ```

2. Add an entry to run the script daily at 2:00 AM:
   ```bash
   0 2 * * * /path/to/backup_postgres.sh 192.168.30.10 30084 mydb myuser mypassword /mnt/postgres-backups 10 /var/log/postgres-backup.log
   ```

3. Save and exit.

### Notes

- Ensure the backup directory has sufficient space.
- The script will attempt to manage backup retention by keeping the specified number of backups and deleting older ones.
- If using SCP for transferring backups, ensure SSH keys or passwords are configured for `scp` to work without manual input.

## Error Handling

- If the `pg_dump` command fails, the script exits with an error.
- If the backup retention management fails, the process will log an error but continue.

## Script Features

- Retains the last `N` backups (default is 10).
- Logs all operations to a specified log file (default is `/tmp/postgres_backup.log`).
- Ensures backup directory exists before starting.
