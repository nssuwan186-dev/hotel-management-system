@echo off
echo 🏨 Starting VIPAT Hotel ERP v2.0...

:: Set PYTHONPATH to include the current directory
set PYTHONPATH=%PYTHONPATH%;%CD%

:: Run Schema Upgrade (optional but recommended to ensure DB is ready)
echo 📊 Ensuring Database is up to date...
python database\models\upgrade_to_erp_v2.py auto

:: Seed Rooms / Migrate JSON Data
echo 🏗️ Migrating data and seeding rooms...
python scripts\migrate_json_to_sql.py
python scripts\seed_rooms.py

:: Start Web Interface
echo 🌐 Starting Web Interface at http://localhost:8000...
start "" python web\interface\database_web_interface_new.py

echo.
echo ✅ ERP System started!
echo 🔗 Access the dashboard at: http://localhost:8000
echo.
pause
