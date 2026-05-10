#!/bin/sh
# Database backup script for Karyaradhane

set -e

# Configuration
BACKUP_DIR="/opt/karyaradhane/backups"
DB_NAME="karyaradhane"
DB_USER="karyaradhane_user"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${DATE}.sql"
RETENTION_DAYS=30

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "Starting database backup..."

# Create backup
pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"
BACKUP_FILE="${BACKUP_FILE}.gz"

echo "Backup created: $BACKUP_FILE"

# Remove old backups
find "$BACKUP_DIR" -name "*.sql.gz" -type f -mtime +$RETENTION_DAYS -delete
echo "Old backups removed (older than $RETENTION_DAYS days)"

# Optional: Upload to cloud storage
# gsutil cp "$BACKUP_FILE" gs://your-backup-bucket/karyaradhane/

echo "Backup completed successfully!"
