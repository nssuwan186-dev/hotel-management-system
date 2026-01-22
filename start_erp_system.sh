#!/bin/bash
# VIPAT ERP - Integrated Startup Script

echo "🏨 Starting VIPAT Hotel ERP System..."

# 1. Kill existing processes if any
pkill -f "database_web_interface_new.py"
pkill -f "บอทโรงแรมSQLite.py"

# 2. Start Web Interface (Port 8000)
echo "🌐 Starting Web Interface on http://localhost:8000..."
python3 web/interface/database_web_interface_new.py > web_output.log 2>&1 &

# 3. Start Telegram Bot
echo "🤖 Starting Telegram Bot..."
export PYTHONPATH=$PYTHONPATH:$(pwd)
python3 bot/core/บอทโรงแรมSQLite.py > bot_output.log 2>&1 &

echo "✅ ERP System is running in background!"
echo "   - Web Log: web_output.log"
echo "   - Bot Log: bot_output.log"
echo "="*30
