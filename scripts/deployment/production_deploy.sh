#!/bin/bash
"""
Production Deployment Script
"""

echo "🚀 Hotel Management System - Production Deployment"
echo "=================================================="

# Check system requirements
echo "📋 Checking system requirements..."
python3 --version
sqlite3 --version

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r config/requirements.txt

# Setup environment
echo "⚙️ Setting up environment..."
if [ ! -f "config/env/.env" ]; then
    cp config/env/.env.example config/env/.env
    echo "📝 Please edit config/env/.env with your settings"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p database/backups
mkdir -p web/static

# Set permissions
echo "🔐 Setting permissions..."
chmod +x scripts/deployment/*.sh
chmod +x scripts/maintenance/*.sh

# Initialize database
echo "💾 Initializing database..."
if [ ! -f "database/data/โรงแรม.db" ]; then
    echo "Creating new database..."
    python3 -c "
import sys
sys.path.append('database/models')
from db_access import create_database
create_database()
"
fi

# Test connections
echo "🧪 Testing system..."
python3 -c "
import sqlite3
import requests
import sys

# Test database
try:
    conn = sqlite3.connect('database/data/โรงแรม.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM ห้องพัก')
    rooms = cursor.fetchone()[0]
    conn.close()
    print(f'✅ Database: {rooms} rooms')
except Exception as e:
    print(f'❌ Database error: {e}')
    sys.exit(1)

print('✅ All tests passed!')
"

# Start services
echo "🎯 Starting services..."

# Start Telegram Bot
echo "🤖 Starting Telegram Bot..."
nohup python3 bot/core/บอทโรงแรมSQLite.py > logs/bot.log 2>&1 &
BOT_PID=$!
echo "Bot PID: $BOT_PID"

# Start Web Interface
echo "🌐 Starting Web Interface..."
nohup python3 web/interface/database_web_interface.py > logs/web.log 2>&1 &
WEB_PID=$!
echo "Web PID: $WEB_PID"

# Wait for services to start
sleep 5

# Check if services are running
echo "📊 Service status:"
if ps -p $BOT_PID > /dev/null; then
    echo "✅ Telegram Bot: Running (PID: $BOT_PID)"
else
    echo "❌ Telegram Bot: Failed to start"
fi

if ps -p $WEB_PID > /dev/null; then
    echo "✅ Web Interface: Running (PID: $WEB_PID)"
    echo "🌐 Access at: http://localhost:8081"
else
    echo "❌ Web Interface: Failed to start"
fi

# Setup monitoring
echo "📈 Setting up monitoring..."
cat > scripts/maintenance/check_services.sh << 'EOF'
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
EOF

chmod +x scripts/maintenance/check_services.sh

# Setup auto-backup
echo "💾 Setting up auto-backup..."
cat > scripts/maintenance/auto_backup.sh << 'EOF'
#!/bin/bash
# Auto backup script

echo "🔄 Starting auto backup - $(date)"
python3 database/backups/backup_system.py

# Keep only last 10 backups
cd database/backups
ls -t backup_*.zip | tail -n +11 | xargs -r rm
echo "✅ Backup completed"
EOF

chmod +x scripts/maintenance/auto_backup.sh

# Create systemd service files (optional)
echo "🔧 Creating service management..."
cat > scripts/deployment/install_services.sh << 'EOF'
#!/bin/bash
# Install as system services (requires sudo)

INSTALL_DIR=$(pwd)

# Telegram Bot Service
sudo tee /etc/systemd/system/hotel-bot.service > /dev/null << EOL
[Unit]
Description=Hotel Management Telegram Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/bot/core/บอทโรงแรมSQLite.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

# Web Interface Service
sudo tee /etc/systemd/system/hotel-web.service > /dev/null << EOL
[Unit]
Description=Hotel Management Web Interface
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/web/interface/database_web_interface.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

# Enable services
sudo systemctl daemon-reload
sudo systemctl enable hotel-bot.service
sudo systemctl enable hotel-web.service

echo "✅ Services installed. Use:"
echo "sudo systemctl start hotel-bot"
echo "sudo systemctl start hotel-web"
EOF

chmod +x scripts/deployment/install_services.sh

echo ""
echo "🎉 Deployment completed successfully!"
echo "===================================="
echo ""
echo "📊 System Status:"
echo "- 🤖 Telegram Bot: @HELLO_Hotel_bot"
echo "- 🌐 Web Interface: http://localhost:8081"
echo "- 💾 Database: $(sqlite3 database/data/โรงแรม.db 'SELECT COUNT(*) FROM ห้องพัก') rooms"
echo ""
echo "🛠️ Management Commands:"
echo "- Check services: ./scripts/maintenance/check_services.sh"
echo "- Backup database: ./scripts/maintenance/auto_backup.sh"
echo "- Install as services: ./scripts/deployment/install_services.sh"
echo ""
echo "📋 Log Files:"
echo "- Bot logs: logs/bot.log"
echo "- Web logs: logs/web.log"
echo ""
echo "✅ System is ready for production use!"
