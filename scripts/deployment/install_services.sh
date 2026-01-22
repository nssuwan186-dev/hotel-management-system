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
