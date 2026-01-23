# Hotel Management System - Project Structure

## 📁 Project Organization

hotel-management/
├── 🤖 bot/                    # Telegram Bot Components
│   ├── core/                  # Core bot functionality
│   │   └── บอทโรงแรมSQLite.py    # Main bot application
│   ├── handlers/              # Message and callback handlers
│   ├── utils/                 # Bot utilities
│   │   └── add_telegram_token.py
│   └── start_bot.py          # Bot startup script
│
├── 🌐 web/                    # Web Interface Components
│   ├── interface/             # Web UI files
│   │   └── database_web_interface.py  # Main web interface
│   ├── api/                   # API endpoints
│   └── static/                # Static assets (CSS, JS, images)
│
├── 💾 database/               # Database Components
│   ├── models/                # Database models and access
│   │   └── db_access.py       # Database utilities
│   ├── migrations/            # Database schema changes
│   ├── backups/               # Backup system
│   │   └── backup_system.py   # Automated backup
│   └── data/                  # Database files
│       └── โรงแรม.db           # Main SQLite database
│
├── ⚙️ config/                 # Configuration Files
│   ├── env/                   # Environment configurations
│   │   └── .env.example       # Environment template
│   ├── settings/              # Application settings
│   ├── requirements.txt       # Python dependencies
│   └── package.json          # Node.js dependencies
│
├── 🚀 scripts/                # Automation Scripts
│   ├── deployment/            # Deployment scripts
│   │   ├── deploy.sh          # Main deployment script
│   │   └── setup_hotel_project.sh
│   └── maintenance/           # Maintenance scripts
│
├── 📚 docs/                   # Documentation
│   ├── README.md              # Main documentation
│   ├── MAIN_FILES.md          # File descriptions
│   └── telegram-bot-setup.md # Setup instructions
│
├── 🧪 tests/                  # Test Files
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── fixtures/              # Test data
│
├── .github/                   # GitHub Configuration
│   └── workflows/             # CI/CD workflows
│       └── ci-cd.yml
│
├── .gitignore                 # Git ignore rules
└── Procfile                   # Process definitions

```

## 🎯 Component Descriptions

### 🤖 Bot Components
- **Core**: Main Telegram bot logic and message processing
- **Handlers**: Specific handlers for different types of interactions
- **Utils**: Helper functions and utilities for bot operations

### 🌐 Web Components
- **Interface**: Web UI for hotel management dashboard
- **API**: RESTful API endpoints for data access
- **Static**: Frontend assets (CSS, JavaScript, images)

### 💾 Database Components
- **Models**: Database schema and data access layers
- **Migrations**: Database version control and schema updates
- **Backups**: Automated backup and restore functionality
- **Data**: Actual database files and data storage

### ⚙️ Configuration
- **Environment**: Environment-specific configurations
- **Settings**: Application settings and parameters
- **Dependencies**: Package management files

### 🚀 Scripts
- **Deployment**: Scripts for deploying to various platforms
- **Maintenance**: Database maintenance and system utilities

### 📚 Documentation
- **Setup Guides**: Installation and configuration instructions
- **API Documentation**: Endpoint descriptions and usage
- **User Manuals**: End-user documentation

## 🔧 Quick Start

```bash
# Start Telegram Bot
python3 bot/core/บอทโรงแรมSQLite.py

# Start Web Interface
python3 web/interface/database_web_interface.py

# Run Backup
python3 database/backups/backup_system.py

# Deploy System
./scripts/deployment/deploy.sh
```

## 📊 System Status

- **Total Files**: Organized into logical components
- **Database**: 51 rooms across 3 buildings
- **Web Interface**: Responsive design with export filters
- **Bot**: Full-featured Telegram integration
- **Deployment**: Ready for production deployment
