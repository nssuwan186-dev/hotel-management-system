# Hotel Management System

ระบบจัดการโรงแรมด้วย Telegram Bot + SQLite Database + Web Interface

## 🚀 Features

- 🤖 **Telegram Bot** - จัดการผ่าน @HELLO_Hotel_bot
- 🌐 **Web Interface** - ดูข้อมูลผ่านเว็บ
- 💾 **SQLite Database** - เก็บข้อมูลผู้เข้าพัก, ห้องพัก
- 📊 **Dashboard** - สถิติและรายงาน
- 💾 **Auto Backup** - สำรองข้อมูลอัตโนมัติ

## 📁 Project Structure

```
hotel-management/
├── src/                    # Source code
│   ├── บอทโรงแรมSQLite.py      # Main Telegram Bot
│   ├── database_web_interface.py # Web Interface
│   ├── db_access.py           # Database utilities
│   └── backup_system.py       # Backup system
├── data/                   # Database files
│   └── โรงแรม.db              # Main SQLite database
├── backup/                 # Backup files
├── docs/                   # Documentation
└── MAIN_FILES.md          # Main files guide
```

## 🛠️ Installation

### Local Development

```bash
# Clone repository
git clone <repository-url>
cd hotel-management

# Install dependencies
pip install requests

# Run Telegram Bot
python3 src/บอทโรงแรมSQLite.py

# Run Web Interface
python3 src/database_web_interface.py
```

### Environment Variables

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export DATABASE_PATH="data/โรงแรม.db"
export WEB_PORT="8081"
```

## 🌐 Deployment Options

### 1. Railway (Recommended)
- Easy deployment
- Free tier available
- Automatic HTTPS

### 2. Heroku
- Git-based deployment
- Add-ons available

### 3. GitHub Pages + Actions
- Static web interface only
- Free hosting

## 📊 Database Schema

- **ผู้เข้าพัก** - Guest information
- **ห้องพัก** - Room management
- **รายการตรวจสอบ** - Checklists
- **ข้อเสนอแนะ** - Suggestions

## 🔧 API Endpoints

- `GET /` - Web interface
- `GET /api/tables` - List all tables
- `GET /api/data?table=<name>` - Get table data
- `GET /api/query?sql=<query>` - Execute SQL query

## 📱 Telegram Commands

- `/start` - Show dashboard
- Inline buttons for all features

## 🚀 Quick Start

1. Set up Telegram Bot Token
2. Run the bot: `python3 src/บอทโรงแรมSQLite.py`
3. Access web interface: `http://localhost:8081`
4. Start managing your hotel!

## 📝 License

MIT License
