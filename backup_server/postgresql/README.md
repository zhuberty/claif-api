
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
./backup_postgres.sh <node_ip> <node_port> <db_name> <db_user> <db_password> <backup_directory>
```

### Example

To back up a database `mydb` running on `192.168.30.10:30084`:

```bash
./backup_postgres.sh 192.168.30.10 30084 mydb myuser mypassword /mnt/postgres_backups
```

### Logs

Logs are stored in `/var/log/postgres_backup.log`. You can monitor this file for backup status:

```bash
tail -f /var/log/postgres_backup.log
```

### Automating with Cronjob

Automate the script to run periodically using a cronjob:

1. Edit the crontab file:
   ```bash
   crontab -e
   ```

2. Add an entry to run the script daily at 2:00 AM:
   ```bash
   0 2 * * * /path/to/backup_postgres.sh 192.168.30.10 30084 mydb myuser mypassword /mnt/postgres_backups
   ```

3. Save and exit.

### Notes

- Ensure the backup directory has sufficient space.
- The script will attempt to transfer the backup to the backup server (`192.168.30.245`). Update the path and user in the script if needed.
- Ensure SSH keys or passwords are configured for `scp` to work without manual input.

## Error Handling

- If the `pg_dump` command fails, the script exits with an error.
- If the file transfer fails, the backup remains stored locally.
