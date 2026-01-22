#!/bin/bash
"""
Deployment Script for Hotel Management System
"""

echo "🚀 Hotel Management System Deployment"
echo "======================================"

# Check current status
echo "📊 Current Status:"
echo "- Bot Process: $(ps aux | grep บอทโรงแรมSQLite.py | grep -v grep | wc -l) running"
echo "- Web Process: $(ps aux | grep database_web_interface.py | grep -v grep | wc -l) running"
echo "- Database Size: $(du -h data/โรงแรม.db 2>/dev/null | cut -f1 || echo 'N/A')"

echo ""
echo "🌐 Deployment Options:"
echo "1. Railway (Recommended)"
echo "2. Heroku"
echo "3. GitHub Pages (Web only)"
echo "4. Local Development"

read -p "Choose deployment option (1-4): " choice

case $choice in
    1)
        echo "🚂 Railway Deployment"
        echo "1. Install Railway CLI: npm install -g @railway/cli"
        echo "2. Login: railway login"
        echo "3. Deploy: railway up"
        echo ""
        echo "Environment Variables needed:"
        echo "- TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-'your_bot_token'}"
        echo "- DATABASE_PATH=data/โรงแรม.db"
        echo "- WEB_PORT=8080"
        ;;
    2)
        echo "🟣 Heroku Deployment"
        echo "1. Install Heroku CLI"
        echo "2. heroku create hotel-management-app"
        echo "3. heroku config:set TELEGRAM_BOT_TOKEN=your_token"
        echo "4. git push heroku main"
        ;;
    3)
        echo "📄 GitHub Pages (Web Interface Only)"
        echo "1. Push to GitHub"
        echo "2. Enable GitHub Pages in repository settings"
        echo "3. Web interface will be available at: https://username.github.io/hotel-management"
        ;;
    4)
        echo "💻 Local Development"
        echo "Starting local services..."
        
        # Kill existing processes
        pkill -f บอทโรงแรมSQLite.py 2>/dev/null
        pkill -f database_web_interface.py 2>/dev/null
        
        # Start services
        echo "🤖 Starting Telegram Bot..."
        nohup python3 src/บอทโรงแรมSQLite.py > logs/bot.log 2>&1 &
        
        echo "🌐 Starting Web Interface..."
        nohup python3 src/database_web_interface.py > logs/web.log 2>&1 &
        
        sleep 3
        
        echo "✅ Services started:"
        echo "- Telegram Bot: @HELLO_Hotel_bot"
        echo "- Web Interface: http://localhost:8081"
        echo "- Logs: logs/bot.log, logs/web.log"
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac

echo ""
echo "📝 Next Steps:"
echo "1. Set up environment variables"
echo "2. Configure database"
echo "3. Test all features"
echo "4. Monitor logs"

echo ""
echo "🔗 Useful Links:"
echo "- Repository: https://github.com/yourusername/hotel-management"
echo "- Documentation: README.md"
echo "- Issues: https://github.com/yourusername/hotel-management/issues"
