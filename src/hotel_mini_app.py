#!/usr/bin/env python3
"""
Complete Hotel Management Mini App in Telegram Chat
All-in-one: CRUD, Reports, Export, Import, Dashboard
"""
import os
import requests
import threading
import time
import json
import csv
from datetime import datetime, timedelta
from io import StringIO, BytesIO

class HotelMiniApp:
    def __init__(self):
        self.token = "8227507211:AAEGs1_BnDaJUvcK07a91MO9YK0LcosPq9I"
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.offset = 0
        self.running = False
        
        # Complete hotel database
        self.hotel_db = {
            "guests": [],
            "rooms": {
                "101": {"type": "standard", "status": "available", "guest_id": None, "price": 800},
                "102": {"type": "standard", "status": "occupied", "guest_id": 1, "price": 800},
                "103": {"type": "standard", "status": "available", "guest_id": None, "price": 800},
                "201": {"type": "deluxe", "status": "available", "guest_id": None, "price": 1200},
                "202": {"type": "deluxe", "status": "maintenance", "guest_id": None, "price": 1200},
                "301": {"type": "suite", "status": "occupied", "guest_id": 2, "price": 2000}
            },
            "bookings": [],
            "payments": [],
            "staff": [],
            "services": [],
            "reports": []
        }
        
        # Sample data
        self.init_sample_data()
        
        # User sessions for multi-step operations
        self.user_sessions = {}
        
        self.data_file = "hotel_miniapp_db.json"
        self.load_data()
        
    def init_sample_data(self):
        """Initialize with sample data"""
        # Sample guests
        self.hotel_db["guests"] = [
            {"id": 1, "name": "นายสมชาย ใจดี", "phone": "081-234-5678", "email": "somchai@email.com", "checkin": "2025-01-20", "checkout": "2025-01-23", "room": "102"},
            {"id": 2, "name": "นางสาวมาลี สวยงาม", "phone": "082-345-6789", "email": "malee@email.com", "checkin": "2025-01-21", "checkout": "2025-01-25", "room": "301"}
        ]
        
        # Sample bookings
        self.hotel_db["bookings"] = [
            {"id": 1, "guest_id": 1, "room": "102", "checkin": "2025-01-20", "checkout": "2025-01-23", "status": "confirmed", "total": 2400},
            {"id": 2, "guest_id": 2, "room": "301", "checkin": "2025-01-21", "checkout": "2025-01-25", "status": "confirmed", "total": 8000}
        ]
        
        # Sample staff
        self.hotel_db["staff"] = [
            {"id": 1, "name": "นางสาวสุดา", "position": "แม่บ้าน", "shift": "เช้า", "salary": 15000},
            {"id": 2, "name": "นายสมศักดิ์", "position": "รปภ.", "shift": "กลางคืน", "salary": 18000}
        ]
    
    def load_data(self):
        """Load data from file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.hotel_db = json.load(f)
        except:
            pass
        self.save_data()
    
    def save_data(self):
        """Save data to file"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.hotel_db, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def send_message(self, chat_id, text, keyboard=None, parse_mode="HTML"):
        """Send message with keyboard"""
        payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
        if keyboard:
            payload["reply_markup"] = keyboard
        try:
            response = requests.post(f"{self.base_url}/sendMessage", json=payload, timeout=10)
            return response.json().get('ok', False)
        except:
            return False
    
    def send_document(self, chat_id, file_content, filename, caption=""):
        """Send file"""
        try:
            files = {'document': (filename, file_content, 'text/csv')}
            data = {'chat_id': chat_id, 'caption': caption}
            response = requests.post(f"{self.base_url}/sendDocument", files=files, data=data, timeout=30)
            return response.json().get('ok', False)
        except:
            return False
    
    def get_main_menu(self):
        """Main menu - Mini App style"""
        return {
            "keyboard": [
                ["👥 ผู้เข้าพัก", "🏠 ห้องพัก", "📋 การจอง"],
                ["👨‍💼 พนักงาน", "💰 การเงิน", "🛎️ บริการ"],
                ["📊 รายงาน", "📁 Export", "📥 Import"],
                ["⚙️ ตั้งค่า", "ℹ️ ช่วยเหลือ"]
            ],
            "resize_keyboard": True
        }
    
    def get_crud_menu(self, entity_type):
        """CRUD operations menu"""
        return {
            "keyboard": [
                [f"➕ เพิ่ม{entity_type}", f"📋 ดู{entity_type}ทั้งหมด"],
                [f"✏️ แก้ไข{entity_type}", f"🗑️ ลบ{entity_type}"],
                [f"🔍 ค้นหา{entity_type}", "🔙 กลับเมนูหลัก"]
            ],
            "resize_keyboard": True
        }
    
    def show_dashboard(self, chat_id):
        """Show hotel dashboard"""
        # Calculate statistics
        total_rooms = len(self.hotel_db["rooms"])
        occupied_rooms = sum(1 for room in self.hotel_db["rooms"].values() if room["status"] == "occupied")
        available_rooms = sum(1 for room in self.hotel_db["rooms"].values() if room["status"] == "available")
        maintenance_rooms = sum(1 for room in self.hotel_db["rooms"].values() if room["status"] == "maintenance")
        
        total_guests = len(self.hotel_db["guests"])
        total_bookings = len(self.hotel_db["bookings"])
        total_revenue = sum(booking.get("total", 0) for booking in self.hotel_db["bookings"])
        
        dashboard = f"""🏨 <b>Hotel Management Dashboard</b>

📊 <b>สถิติห้องพัก:</b>
🏠 ทั้งหมด: {total_rooms} ห้อง
🔴 เข้าพัก: {occupied_rooms} ห้อง ({(occupied_rooms/total_rooms*100):.1f}%)
🟢 ว่าง: {available_rooms} ห้อง ({(available_rooms/total_rooms*100):.1f}%)
🟡 ซ่อมแซม: {maintenance_rooms} ห้อง

👥 <b>ผู้เข้าพัก:</b>
📋 ทั้งหมด: {total_guests} คน
📅 การจอง: {total_bookings} รายการ

💰 <b>รายได้:</b>
💵 รวม: {total_revenue:,} บาท
📈 เฉลี่ย/การจอง: {(total_revenue/max(total_bookings,1)):,.0f} บาท

📅 <b>วันที่:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}

<b>เลือกเมนูด้านล่างเพื่อจัดการ</b>"""
        
        self.send_message(chat_id, dashboard, self.get_main_menu())
    
    def show_guests_list(self, chat_id):
        """Show all guests with actions"""
        if not self.hotel_db["guests"]:
            self.send_message(chat_id, "👥 <b>ไม่มีผู้เข้าพักในระบบ</b>", self.get_crud_menu("ผู้เข้าพัก"))
            return
        
        guests_text = "👥 <b>รายชื่อผู้เข้าพัก</b>\n\n"
        
        for guest in self.hotel_db["guests"]:
            status = "🔴 เข้าพัก" if guest.get("room") else "🟢 เช็คเอาท์แล้ว"
            guests_text += f"🆔 <b>{guest['id']}</b> - {guest['name']}\n"
            guests_text += f"   📞 {guest['phone']}\n"
            guests_text += f"   🏠 ห้อง: {guest.get('room', 'ไม่มี')}\n"
            guests_text += f"   {status}\n\n"
        
        # Add action buttons
        action_keyboard = {
            "keyboard": [
                ["👤 ดูรายละเอียด", "✏️ แก้ไขข้อมูล"],
                ["🏠 เปลี่ยนห้อง", "💰 ดูการเงิน"],
                ["➕ เพิ่มผู้เข้าพักใหม่", "🔙 กลับ"]
            ],
            "resize_keyboard": True
        }
        
        self.send_message(chat_id, guests_text, action_keyboard)
    
    def show_rooms_status(self, chat_id):
        """Show rooms with visual status"""
        rooms_text = "🏠 <b>สถานะห้องพัก</b>\n\n"
        
        # Group by floor
        floors = {}
        for room_num, room_data in self.hotel_db["rooms"].items():
            floor = room_num[0]  # First digit is floor
            if floor not in floors:
                floors[floor] = []
            floors[floor].append((room_num, room_data))
        
        for floor in sorted(floors.keys()):
            rooms_text += f"🏢 <b>ชั้น {floor}</b>\n"
            
            for room_num, room_data in sorted(floors[floor]):
                # Status emoji
                status_emoji = {
                    "available": "🟢",
                    "occupied": "🔴", 
                    "maintenance": "🟡"
                }
                
                emoji = status_emoji.get(room_data["status"], "⚪")
                guest_info = ""
                
                if room_data["status"] == "occupied" and room_data.get("guest_id"):
                    guest = next((g for g in self.hotel_db["guests"] if g["id"] == room_data["guest_id"]), None)
                    if guest:
                        guest_info = f" - {guest['name']}"
                
                rooms_text += f"{emoji} <b>{room_num}</b> ({room_data['type']}) {room_data['price']:,}฿{guest_info}\n"
            
            rooms_text += "\n"
        
        # Legend
        rooms_text += "📋 <b>สัญลักษณ์:</b>\n"
        rooms_text += "🟢 ว่าง | 🔴 เข้าพัก | 🟡 ซ่อมแซม\n"
        
        self.send_message(chat_id, rooms_text, self.get_crud_menu("ห้อง"))
    
    def export_data(self, chat_id, data_type="all"):
        """Export data to CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        
        if data_type == "guests" or data_type == "all":
            # Export guests
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(['ID', 'Name', 'Phone', 'Email', 'Room', 'Check_In', 'Check_Out', 'Status'])
            
            for guest in self.hotel_db["guests"]:
                writer.writerow([
                    guest['id'], guest['name'], guest['phone'], 
                    guest.get('email', ''), guest.get('room', ''),
                    guest.get('checkin', ''), guest.get('checkout', ''),
                    'เข้าพัก' if guest.get('room') else 'เช็คเอาท์'
                ])
            
            csv_content = output.getvalue().encode('utf-8-sig')
            filename = f"guests_{timestamp}.csv"
            self.send_document(chat_id, csv_content, filename, "👥 ข้อมูลผู้เข้าพัก")
        
        if data_type == "rooms" or data_type == "all":
            # Export rooms
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(['Room_Number', 'Type', 'Status', 'Price', 'Guest_ID', 'Guest_Name'])
            
            for room_num, room_data in self.hotel_db["rooms"].items():
                guest_name = ""
                if room_data.get("guest_id"):
                    guest = next((g for g in self.hotel_db["guests"] if g["id"] == room_data["guest_id"]), None)
                    if guest:
                        guest_name = guest["name"]
                
                writer.writerow([
                    room_num, room_data['type'], room_data['status'],
                    room_data['price'], room_data.get('guest_id', ''), guest_name
                ])
            
            csv_content = output.getvalue().encode('utf-8-sig')
            filename = f"rooms_{timestamp}.csv"
            self.send_document(chat_id, csv_content, filename, "🏠 ข้อมูลห้องพัก")
        
        if data_type == "bookings" or data_type == "all":
            # Export bookings
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(['Booking_ID', 'Guest_ID', 'Guest_Name', 'Room', 'Check_In', 'Check_Out', 'Status', 'Total'])
            
            for booking in self.hotel_db["bookings"]:
                guest = next((g for g in self.hotel_db["guests"] if g["id"] == booking["guest_id"]), None)
                guest_name = guest["name"] if guest else "Unknown"
                
                writer.writerow([
                    booking['id'], booking['guest_id'], guest_name,
                    booking['room'], booking['checkin'], booking['checkout'],
                    booking['status'], booking.get('total', 0)
                ])
            
            csv_content = output.getvalue().encode('utf-8-sig')
            filename = f"bookings_{timestamp}.csv"
            self.send_document(chat_id, csv_content, filename, "📋 ข้อมูลการจอง")
        
        if data_type == "all":
            self.send_message(chat_id, "✅ <b>Export ข้อมูลทั้งหมดเสร็จแล้ว!</b>\n\n📁 ไฟล์ CSV พร้อมใช้งาน")
    
    def generate_report(self, chat_id, report_type):
        """Generate various reports"""
        if report_type == "occupancy":
            # Occupancy report
            total_rooms = len(self.hotel_db["rooms"])
            occupied = sum(1 for r in self.hotel_db["rooms"].values() if r["status"] == "occupied")
            available = sum(1 for r in self.hotel_db["rooms"].values() if r["status"] == "available")
            maintenance = sum(1 for r in self.hotel_db["rooms"].values() if r["status"] == "maintenance")
            
            report = f"""📊 <b>รายงานอัตราเข้าพัก</b>

📅 <b>วันที่:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}

🏠 <b>สถิติห้องพัก:</b>
• ทั้งหมด: {total_rooms} ห้อง
• เข้าพัก: {occupied} ห้อง ({(occupied/total_rooms*100):.1f}%)
• ว่าง: {available} ห้อง ({(available/total_rooms*100):.1f}%)
• ซ่อมแซม: {maintenance} ห้อง ({(maintenance/total_rooms*100):.1f}%)

📈 <b>อัตราเข้าพัก:</b> {(occupied/total_rooms*100):.1f}%

💡 <b>คำแนะนำ:</b>
{self.get_occupancy_recommendation(occupied/total_rooms*100)}"""
            
            self.send_message(chat_id, report)
        
        elif report_type == "revenue":
            # Revenue report
            total_revenue = sum(booking.get("total", 0) for booking in self.hotel_db["bookings"])
            total_bookings = len(self.hotel_db["bookings"])
            avg_revenue = total_revenue / max(total_bookings, 1)
            
            # Revenue by room type
            revenue_by_type = {}
            for booking in self.hotel_db["bookings"]:
                room_num = booking["room"]
                room_type = self.hotel_db["rooms"][room_num]["type"]
                if room_type not in revenue_by_type:
                    revenue_by_type[room_type] = 0
                revenue_by_type[room_type] += booking.get("total", 0)
            
            report = f"""💰 <b>รายงานรายได้</b>

📅 <b>วันที่:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}

💵 <b>รายได้รวม:</b> {total_revenue:,} บาท
📋 <b>จำนวนการจอง:</b> {total_bookings} รายการ
📊 <b>รายได้เฉลี่ย:</b> {avg_revenue:,.0f} บาท/การจอง

🏠 <b>รายได้ตามประเภทห้อง:</b>
"""
            
            for room_type, revenue in revenue_by_type.items():
                percentage = (revenue / total_revenue * 100) if total_revenue > 0 else 0
                report += f"• {room_type}: {revenue:,} บาท ({percentage:.1f}%)\n"
            
            self.send_message(chat_id, report)
    
    def get_occupancy_recommendation(self, occupancy_rate):
        """Get recommendation based on occupancy rate"""
        if occupancy_rate >= 90:
            return "🔥 อัตราเข้าพักสูงมาก! พิจารณาเพิ่มราคาหรือโปรโมชั่นพิเศษ"
        elif occupancy_rate >= 70:
            return "✅ อัตราเข้าพักดี รักษาระดับบริการ"
        elif occupancy_rate >= 50:
            return "📈 อัตราเข้าพักปานกลาง พิจารณาโปรโมชั่น"
        else:
            return "📉 อัตราเข้าพักต่ำ ควรทำการตลาดเพิ่มเติม"
    
    def process_message(self, message):
        """Process all messages - Mini App style"""
        chat_id = message['chat']['id']
        text = message.get('text', '').strip()
        user_name = message['from'].get('first_name', 'Guest')
        
        if text == '/start':
            welcome = f"""🏨 <b>ยินดีต้อนรับ {user_name}!</b>

🎯 <b>Hotel Management Mini App</b>
<i>ระบบจัดการโรงแรมครบครันในแชท</i>

✨ <b>ฟีเจอร์ทั้งหมด:</b>
• 👥 จัดการผู้เข้าพัก (CRUD)
• 🏠 จัดการห้องพัก
• 📋 ระบบการจอง
• 👨‍💼 จัดการพนักงาน
• 💰 ระบบการเงิน
• 📊 รายงานแบบ Real-time
• 📁 Export/Import ข้อมูล

<b>เริ่มใช้งานเลย!</b> 🚀"""
            
            self.show_dashboard(chat_id)
            
        elif text == "👥 ผู้เข้าพัก":
            self.show_guests_list(chat_id)
            
        elif text == "🏠 ห้องพัก":
            self.show_rooms_status(chat_id)
            
        elif text == "📊 รายงาน":
            report_menu = {
                "keyboard": [
                    ["📈 รายงานอัตราเข้าพัก", "💰 รายงานรายได้"],
                    ["👥 รายงานผู้เข้าพัก", "🏠 รายงานห้องพัก"],
                    ["📅 รายงานรายวัน", "📊 Dashboard"],
                    ["🔙 กลับเมนูหลัก"]
                ],
                "resize_keyboard": True
            }
            self.send_message(chat_id, "📊 <b>เลือกประเภทรายงาน:</b>", report_menu)
            
        elif text == "📁 Export":
            export_menu = {
                "keyboard": [
                    ["👥 Export ผู้เข้าพัก", "🏠 Export ห้องพัก"],
                    ["📋 Export การจอง", "📁 Export ทั้งหมด"],
                    ["🔙 กลับเมนูหลัก"]
                ],
                "resize_keyboard": True
            }
            self.send_message(chat_id, "📁 <b>เลือกข้อมูลที่ต้องการ Export:</b>", export_menu)
            
        elif text == "📈 รายงานอัตราเข้าพัก":
            self.generate_report(chat_id, "occupancy")
            
        elif text == "💰 รายงานรายได้":
            self.generate_report(chat_id, "revenue")
            
        elif text == "👥 Export ผู้เข้าพัก":
            self.export_data(chat_id, "guests")
            
        elif text == "🏠 Export ห้องพัก":
            self.export_data(chat_id, "rooms")
            
        elif text == "📋 Export การจอง":
            self.export_data(chat_id, "bookings")
            
        elif text == "📁 Export ทั้งหมด":
            self.export_data(chat_id, "all")
            
        elif text == "📊 Dashboard" or text == "🔙 กลับเมนูหลัก":
            self.show_dashboard(chat_id)
            
        else:
            self.send_message(chat_id, "❓ <b>ไม่เข้าใจคำสั่ง</b>\n\n📱 กดปุ่มเมนูด้านล่างเพื่อใช้งาน")
    
    def get_updates(self):
        """Get updates"""
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
        """Start polling"""
        self.running = True
        print("🤖 Hotel Mini App started...")
        
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

if __name__ == "__main__":
    bot = HotelMiniApp()
    bot.start_polling()
