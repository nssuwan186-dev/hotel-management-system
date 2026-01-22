#!/usr/bin/env python3
"""
Add Telegram Token to Bot
"""
import os

def add_telegram_token():
    """Add Telegram bot token from environment variable"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ Please set TELEGRAM_BOT_TOKEN environment variable")
        return False
    
    print("✅ Token loaded from environment")
    return token

if __name__ == "__main__":
    add_telegram_token()
