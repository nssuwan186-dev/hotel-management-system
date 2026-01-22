#!/usr/bin/env python3
# Complete Hotel Management System in HF Space
import os
import sqlite3
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.request import HTTPXRequest 
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Configuration
TELEGRAM_TOKEN = os.getenv('TG_BOT_TOKEN_FINAL', '')

# Initialize Database
def init_database():
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT UNIQUE,
            name TEXT,
            phone TEXT,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id TEXT UNIQUE,
            room_type TEXT,
            daily_rate REAL,
            monthly_rate REAL,
            status TEXT DEFAULT 'available'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id TEXT UNIQUE,
            customer_id TEXT,
            room_id TEXT,
            check_in DATE,
            check_out DATE,
            total_price REAL,
            status TEXT DEFAULT 'confirmed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS utilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id TEXT,
            month_year TEXT,
            electric_old INTEGER,
            electric_new INTEGER,
            water_old INTEGER,
            water_new INTEGER,
            electric_cost REAL,
            water_cost REAL,
            total_cost REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert sample rooms
    sample_rooms = [
        ('RM001', 'standard', 400, 8000),
        ('RM002', 'deluxe', 500, 10000),
        ('RM003', 'suite', 800, 15000)
    ]
    
    for room in sample_rooms:
        cursor.execute('INSERT OR IGNORE INTO rooms (room_id, room_type, daily_rate, monthly_rate) VALUES (?, ?, ?, ?)', room)
    
    conn.commit()
    conn.close()

# Database functions
def generate_id(prefix):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"{prefix}{timestamp}"

def calculate_utilities(electric_old, electric_new, water_old, water_new):
    electric_units = electric_new - electric_old
    water_units = water_new - water_old
    
    # Electric calculation (progressive rates)
    if electric_units <= 150:
        electric_cost = electric_units * 3.27
    elif electric_units <= 400:
        electric_cost = 150 * 3.27 + (electric_units - 150) * 4.22
    else:
        electric_cost = 150 * 3.27 + 250 * 4.22 + (electric_units - 400) * 4.42
    
    # Water calculation (progressive rates)
    if water_units <= 8:
        water_cost = water_units * 8.50
    elif water_units <= 20:
        water_cost = 8 * 8.50 + (water_units - 8) * 9.50
    else:
        water_cost = 8 * 8.50 + 12 * 9.50 + (water_units - 20) * 11.50
    
    return {
        'electric_units': electric_units,
        'water_units': water_units,
        'electric_cost': round(electric_cost, 2),
        'water_cost': round(water_cost, 2),
        'total_cost': round(electric_cost + water_cost, 2)
    }

def add_booking(room_type, start_date, end_date):
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    
    booking_id = generate_id('BK')
    customer_id = generate_id('CUS')
    
    # Get room rate
    cursor.execute('SELECT daily_rate FROM rooms WHERE room_type = ? AND status = "available" LIMIT 1', (room_type,))
    room = cursor.fetchone()
    
    if room:
        daily_rate = room[0]
        # Simple calculation (you can make it more complex)
        total_price = daily_rate * 3  # Assume 3 days
        
        cursor.execute('''
            INSERT INTO bookings (booking_id, customer_id, room_id, check_in, check_out, total_price)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (booking_id, customer_id, f'RM_{room_type}', start_date, end_date, total_price))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'booking_id': booking_id,
            'customer_id': customer_id,
            'total_price': total_price
        }
    
    conn.close()
    return {'success': False, 'message': 'No available rooms'}

def save_utilities(room_id, electric_old, electric_new, water_old, water_new):
    conn = sqlite3.connect('hotel.db')
    cursor = conn.cursor()
    
    result = calculate_utilities(electric_old, electric_new, water_old, water_new)
    month_year = datetime.now().strftime('%Y-%m')
    
    cursor.execute('''
        INSERT INTO utilities (room_id, month_year, electric_old, electric_new, water_old, water_new, 
                              electric_cost, water_cost, total_cost)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (room_id, month_year, electric_old, electric_new, water_old, water_new,
          result['electric_cost'], result['water_cost'], result['total_cost']))
    
    conn.commit()
    conn.close()
    
    return result

# Bot handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🏨 จองห้องพัก", callback_data='booking')],
        [
            InlineKeyboardButton("💡 คำนวณค่าไฟน้ำ", callback_data='utilities'),
            InlineKeyboardButton("📊 รายงาน", callback_data='reports')
        ],
        [InlineKeyboardButton("🔍 ตรวจสอบห้อง", callback_data='check_rooms')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🏨 *VIPAT Hotel Management System*\n\n"
        "ยินดีต้อนรับครับ! เลือกบริการที่ต้องการ:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'booking':
        text = "📝 *การจองห้องพัก*\n\n" \
               "กรุณาส่งข้อมูลในรูปแบบ:\n" \
               "`จอง [ประเภทห้อง] [วันเริ่ม] [วันสิ้นสุด]`\n\n" \
               "ตัวอย่าง:\n" \
               "`จอง standard 25/1/2026 27/1/2026`\n\n" \
               "ประเภทห้อง: standard, deluxe, suite"
        
    elif query.data == 'utilities':
        text = "💡 *คำนวณค่าไฟน้ำ*\n\n" \
               "กรุณาส่งข้อมูลในรูปแบบ:\n" \
               "`ค่าไฟน้ำ [ห้อง] [ไฟเก่า] [ไฟใหม่] [น้ำเก่า] [น้ำใหม่]`\n\n" \
               "ตัวอย่าง:\n" \
               "`ค่าไฟน้ำ 101 1000 1150 50 65`"
        
    elif query.data == 'reports':
        conn = sqlite3.connect('hotel.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM bookings')
        total_bookings = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM utilities')
        total_utilities = cursor.fetchone()[0]
        
        conn.close()
        
        text = f"📊 *รายงานระบบ*\n\n" \
               f"📋 การจองทั้งหมด: {total_bookings} รายการ\n" \
               f"💡 บันทึกค่าไฟน้ำ: {total_utilities} รายการ\n\n" \
               f"💾 ข้อมูลเก็บใน SQLite Database"
        
    elif query.data == 'check_rooms':
        conn = sqlite3.connect('hotel.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT room_id, room_type, daily_rate, status FROM rooms')
        rooms = cursor.fetchall()
        
        room_list = "\n".join([f"• {room[0]} ({room[1]}): {room[2]:,.0f}฿/วัน - {room[3]}" for room in rooms])
        
        text = f"🏨 *สถานะห้องพัก*\n\n{room_list}"
        
        conn.close()
    
    await query.edit_message_text(text, parse_mode='Markdown')

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    
    if text.startswith('จอง'):
        parts = text.split()
        if len(parts) >= 4:
            room_type = parts[1]
            start_date = parts[2]
            end_date = parts[3]
            
            result = add_booking(room_type, start_date, end_date)
            
            if result['success']:
                response = f"✅ *การจองสำเร็จ!*\n\n" \
                          f"รหัสการจอง: `{result['booking_id']}`\n" \
                          f"รหัสลูกค้า: `{result['customer_id']}`\n" \
                          f"ประเภทห้อง: {room_type}\n" \
                          f"ราคารวม: {result['total_price']:,.0f} บาท\n\n" \
                          f"💾 บันทึกในฐานข้อมูลแล้ว"
            else:
                response = "❌ ไม่มีห้องว่าง"
        else:
            response = "❌ รูปแบบไม่ถูกต้อง\nใช้: `จอง [ประเภทห้อง] [วันเริ่ม] [วันสิ้นสุด]`"
            
    elif text.startswith('ค่าไฟน้ำ'):
        parts = text.split()
        if len(parts) >= 6:
            room_id = parts[1]
            electric_old = int(parts[2])
            electric_new = int(parts[3])
            water_old = int(parts[4])
            water_new = int(parts[5])
            
            result = save_utilities(room_id, electric_old, electric_new, water_old, water_new)
            
            response = f"💡 *ค่าสาธารณูปโภค ห้อง {room_id}*\n\n" \
                      f"⚡ ไฟ: {result['electric_units']} หน่วย = {result['electric_cost']:,.2f} บาท\n" \
                      f"💧 น้ำ: {result['water_units']} หน่วย = {result['water_cost']:,.2f} บาท\n\n" \
                      f"💰 *รวมทั้งสิ้น: {result['total_cost']:,.2f} บาท*\n\n" \
                      f"💾 บันทึกในฐานข้อมูลแล้ว"
        else:
            response = "❌ รูปแบบไม่ถูกต้อง\nใช้: `ค่าไฟน้ำ [ห้อง] [ไฟเก่า] [ไฟใหม่] [น้ำเก่า] [น้ำใหม่]`"
    else:
        response = "ไม่เข้าใจคำสั่ง กรุณาใช้ /start เพื่อดูเมนู"
    
    await update.message.reply_text(response, parse_mode='Markdown')

def main():
    # Initialize database
    init_database()
    
    # Create application
    request = HTTPXRequest(connection_pool_size=20, read_timeout=30, write_timeout=30)
    application = Application.builder().token(TELEGRAM_TOKEN).request(request).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # Start bot
    print("🤖 Hotel Management Bot Starting with SQLite Database...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
