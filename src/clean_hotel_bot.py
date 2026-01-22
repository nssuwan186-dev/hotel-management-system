#!/usr/bin/env python3
"""
Clean Hotel Management Bot - Production Ready
"""
import gradio as gr
import requests
import threading
import time
import json
from datetime import datetime

class HotelBot:
    def __init__(self):
        self.token = "8227507211:AAEGs1_BnDaJUvcK07a91MO9YK0LcosPq9I"
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.offset = 0
        self.running = False
        
        # Hotel data
        self.rooms = {
            "standard": {"price": 800, "available": 10, "total": 10},
            "deluxe": {"price": 1200, "available": 5, "total": 5},
            "suite": {"price": 2000, "available": 2, "total": 2}
        }
        
        self.bookings = []
        self.utilities = {"rate": 4.5}  # บาท/หน่วย
        
    def send_message(self, chat_id, text, keyboard=None):
        """Send message to Telegram"""
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        if keyboard:
            payload["reply_markup"] = keyboard
            
        try:
            response = requests.post(f"{self.base_url}/sendMessage", 
                                   json=payload, timeout=10)
            return response.json().get('ok', False)
        except:
            return False
    
    def get_main_keyboard(self):
        """Main menu keyboard"""
        return {
            "keyboard": [
                ["🏠 ห้องว่าง", "📋 รายการจอง"],
                ["💡 ค่าไฟน้ำ", "📊 สถิติ"],
                ["ℹ️ ช่วยเหลือ"]
            ],
            "resize_keyboard": True
        }
    
    def handle_start(self, chat_id, user_name):
        """Handle /start command"""
        welcome = f"""🏨 <b>ยินดีต้อนรับ {user_name}!</b>

🔹 <b>การจอง:</b> จอง [ชื่อ] [เบอร์] [ประเภท]
🔹 <b>ค่าไฟน้ำ:</b> ค่าไฟน้ำ [หน่วย]
🔹 <b>ห้องว่าง:</b> ดูห้องที่ว่าง
🔹 <b>รายการจอง:</b> ดูการจองทั้งหมด

<b>ประเภทห้อง:</b>
• standard (800฿)
• deluxe (1,200฿) 
• suite (2,000฿)"""
        
        self.send_message(chat_id, welcome, self.get_main_keyboard())
    
    def handle_booking(self, chat_id, text):
        """Handle booking request"""
        parts = text.split()
        if len(parts) < 4:
            self.send_message(chat_id, 
                "❌ <b>รูปแบบไม่ถูกต้อง</b>\n\n📝 ใช้: จอง [ชื่อ] [เบอร์] [ประเภทห้อง]")
            return
            
        _, name, phone, room_type = parts[:4]
        
        if room_type not in self.rooms:
            self.send_message(chat_id, 
                "❌ <b>ประเภทห้องไม่ถูกต้อง</b>\n\n✅ ใช้: standard, deluxe, suite")
            return
            
        if self.rooms[room_type]["available"] <= 0:
            self.send_message(chat_id, f"❌ <b>ห้อง {room_type} เต็มแล้ว</b>")
            return
        
        # Create booking
        booking_id = len(self.bookings) + 1
        booking = {
            "id": booking_id,
            "name": name,
            "phone": phone,
            "room_type": room_type,
            "price": self.rooms[room_type]["price"],
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "chat_id": chat_id
        }
        
        self.bookings.append(booking)
        self.rooms[room_type]["available"] -= 1
        
        response = f"""✅ <b>จองสำเร็จ!</b>

🆔 <b>รหัส:</b> #{booking_id:03d}
👤 <b>ชื่อ:</b> {name}
📞 <b>เบอร์:</b> {phone}
🏠 <b>ห้อง:</b> {room_type}
💰 <b>ราคา:</b> {booking['price']:,} บาท
📅 <b>วันที่:</b> {booking['date']}"""
        
        self.send_message(chat_id, response)
    
    def handle_utilities(self, chat_id, text):
        """Handle utilities calculation"""
        parts = text.split()
        if len(parts) < 2:
            self.send_message(chat_id, 
                "❌ <b>รูปแบบไม่ถูกต้อง</b>\n\n📝 ใช้: ค่าไฟน้ำ [จำนวนหน่วย]")
            return
            
        try:
            units = float(parts[1])
            cost = units * self.utilities["rate"]
            
            response = f"""💡 <b>ค่าไฟน้ำ</b>

🔢 <b>หน่วย:</b> {units:,.1f}
💰 <b>ค่าไฟ:</b> {cost:,.2f} บาท
📊 <b>อัตรา:</b> {self.utilities['rate']} บาท/หน่วย"""
            
            self.send_message(chat_id, response)
        except ValueError:
            self.send_message(chat_id, "❌ <b>กรุณาใส่ตัวเลขที่ถูกต้อง</b>")
    
    def handle_rooms_status(self, chat_id):
        """Show available rooms"""
        response = "🏠 <b>สถานะห้องพัก</b>\n\n"
        
        for room_type, info in self.rooms.items():
            available = info["available"]
            total = info["total"]
            price = info["price"]
            
            status = "✅" if available > 0 else "❌"
            response += f"{status} <b>{room_type}</b>\n"
            response += f"   💰 {price:,} บาท\n"
            response += f"   🏠 ว่าง: {available}/{total} ห้อง\n\n"
        
        self.send_message(chat_id, response)
    
    def handle_bookings_list(self, chat_id):
        """Show all bookings"""
        if not self.bookings:
            self.send_message(chat_id, "📋 <b>ยังไม่มีการจอง</b>")
            return
            
        response = "📋 <b>รายการจอง</b>\n\n"
        
        for booking in self.bookings[-10:]:  # Show last 10
            response += f"🆔 #{booking['id']:03d} - <b>{booking['name']}</b>\n"
            response += f"   🏠 {booking['room_type']} ({booking['price']:,}฿)\n"
            response += f"   📞 {booking['phone']}\n"
            response += f"   📅 {booking['date']}\n\n"
        
        if len(self.bookings) > 10:
            response += f"... และอีก {len(self.bookings) - 10} รายการ"
            
        self.send_message(chat_id, response)
    
    def handle_statistics(self, chat_id):
        """Show hotel statistics"""
        total_bookings = len(self.bookings)
        total_revenue = sum(b["price"] for b in self.bookings)
        
        occupied_rooms = sum(r["total"] - r["available"] for r in self.rooms.values())
        total_rooms = sum(r["total"] for r in self.rooms.values())
        
        response = f"""📊 <b>สถิติโรงแรม</b>

📋 <b>การจอง:</b> {total_bookings} รายการ
💰 <b>รายได้:</b> {total_revenue:,} บาท
🏠 <b>ห้องพัก:</b> {occupied_rooms}/{total_rooms} ห้อง
📈 <b>อัตราเข้าพัก:</b> {(occupied_rooms/total_rooms*100):.1f}%"""

        self.send_message(chat_id, response)
    
    def handle_help(self, chat_id):
        """Show help information"""
        help_text = """ℹ️ <b>คำสั่งทั้งหมด</b>

🔹 <b>จอง [ชื่อ] [เบอร์] [ประเภท]</b>
   ตัวอย่าง: จอง สมชาย 081-234-5678 standard

🔹 <b>ค่าไฟน้ำ [หน่วย]</b>
   ตัวอย่าง: ค่าไฟน้ำ 150

🔹 <b>ห้องว่าง</b> - ดูห้องที่ว่าง
🔹 <b>รายการจอง</b> - ดูการจองทั้งหมด
🔹 <b>สถิติ</b> - ดูสถิติโรงแรม

<b>ประเภทห้อง:</b>
• standard - 800 บาท
• deluxe - 1,200 บาท
• suite - 2,000 บาท"""

        self.send_message(chat_id, help_text)
    
    def process_message(self, message):
        """Process incoming message"""
        chat_id = message['chat']['id']
        text = message.get('text', '').strip()
        user_name = message['from'].get('first_name', 'Guest')
        
        # Convert to lowercase for command matching
        text_lower = text.lower()
        
        if text_lower == '/start':
            self.handle_start(chat_id, user_name)
        elif text_lower.startswith('จอง'):
            self.handle_booking(chat_id, text)
        elif text_lower.startswith('ค่าไฟน้ำ'):
            self.handle_utilities(chat_id, text)
        elif 'ห้องว่าง' in text_lower or '🏠' in text:
            self.handle_rooms_status(chat_id)
        elif 'รายการจอง' in text_lower or '📋' in text:
            self.handle_bookings_list(chat_id)
        elif 'สถิติ' in text_lower or '📊' in text:
            self.handle_statistics(chat_id)
        elif 'ช่วยเหลือ' in text_lower or 'help' in text_lower or 'ℹ️' in text:
            self.handle_help(chat_id)
        else:
            self.send_message(chat_id, 
                "❓ <b>ไม่เข้าใจคำสั่ง</b>\n\n📝 พิมพ์ /start เพื่อดูคำสั่งทั้งหมด")
    
    def get_updates(self):
        """Get updates from Telegram"""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {"offset": self.offset, "timeout": 30}
            
            response = requests.get(url, params=params, timeout=35)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def start_polling(self):
        """Start bot polling"""
        self.running = True
        print("🤖 Hotel Bot started...")
        
        while self.running:
            try:
                updates = self.get_updates()
                if updates and updates.get('ok'):
                    for update in updates.get('result', []):
                        self.offset = update['update_id'] + 1
                        if 'message' in update:
                            self.process_message(update['message'])
                            
            except Exception as e:
                print(f"Polling error: {e}")
                time.sleep(5)
    
    def stop(self):
        """Stop bot"""
        self.running = False

# Initialize bot
bot = HotelBot()

# Start bot in background
bot_thread = threading.Thread(target=bot.start_polling, daemon=True)
bot_thread.start()

# Gradio interface
def get_bot_status():
    """Get bot status for Gradio"""
    try:
        response = requests.get(f"{bot.base_url}/getMe", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                return f"✅ Bot @{data['result']['username']} is online!"
        return "❌ Bot is offline"
    except:
        return "❌ Cannot check bot status"

def get_hotel_stats():
    """Get hotel statistics for Gradio"""
    total_bookings = len(bot.bookings)
    total_revenue = sum(b["price"] for b in bot.bookings)
    occupied = sum(r["total"] - r["available"] for r in bot.rooms.values())
    total = sum(r["total"] for r in bot.rooms.values())
    
    return f"""📊 Hotel Statistics:
• Total Bookings: {total_bookings}
• Total Revenue: {total_revenue:,} THB
• Occupied Rooms: {occupied}/{total}
• Occupancy Rate: {(occupied/total*100):.1f}%"""

# Create Gradio interface
with gr.Blocks(title="Hotel Management Bot", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🏨 Hotel Management Bot")
    gr.Markdown("**Bot:** [@HELLO_Hotel_bot](https://t.me/HELLO_Hotel_bot)")
    
    with gr.Row():
        with gr.Column():
            status_btn = gr.Button("🔍 Check Bot Status", variant="primary")
            status_output = gr.Textbox(label="Bot Status", interactive=False)
            
        with gr.Column():
            stats_btn = gr.Button("📊 Hotel Statistics", variant="secondary")
            stats_output = gr.Textbox(label="Statistics", interactive=False)
    
    gr.Markdown("""
    ## 🎯 How to Use:
    1. Go to [@HELLO_Hotel_bot](https://t.me/HELLO_Hotel_bot) in Telegram
    2. Send `/start` to begin
    3. Use commands like:
       - `จอง สมชาย 081-234-5678 standard`
       - `ค่าไฟน้ำ 150`
       - `ห้องว่าง`
    """)
    
    status_btn.click(get_bot_status, outputs=status_output)
    stats_btn.click(get_hotel_stats, outputs=stats_output)

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)
