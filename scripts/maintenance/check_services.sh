#!/bin/bash
# Service health check script

echo "🔍 Service Health Check - $(date)"
echo "================================"

# Check Telegram Bot
if pgrep -f "บอทโรงแรมSQLite.py" > /dev/null; then
    echo "✅ Telegram Bot: Running"
else
    echo "❌ Telegram Bot: Not running"
    echo "🔄 Restarting bot..."
    nohup python3 bot/core/บอทโรงแรมSQLite.py > logs/bot.log 2>&1 &
fi

# Check Web Interface
if pgrep -f "database_web_interface.py" > /dev/null; then
    echo "✅ Web Interface: Running"
else
    echo "❌ Web Interface: Not running"
    echo "🔄 Restarting web interface..."
    nohup python3 web/interface/database_web_interface.py > logs/web.log 2>&1 &
fi

# Check database
if [ -f "database/data/โรงแรม.db" ]; then
    ROOMS=$(sqlite3 database/data/โรงแรม.db "SELECT COUNT(*) FROM ห้องพัก")
    echo "✅ Database: $ROOMS rooms"
else
    echo "❌ Database: File not found"
fi

# Check disk space
DISK_USAGE=$(df -h . | awk 'NR==2 {print $5}')
echo "💾 Disk usage: $DISK_USAGE"

echo "================================"
