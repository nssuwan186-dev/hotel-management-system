#!/bin/bash
# Auto backup script

echo "🔄 Starting auto backup - $(date)"
python3 database/backups/backup_system.py

# Keep only last 10 backups
cd database/backups
ls -t backup_*.zip | tail -n +11 | xargs -r rm
echo "✅ Backup completed"
