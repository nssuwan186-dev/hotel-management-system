#!/usr/bin/env python3
"""
Enhanced Hotel Bot - Real Room Management
"""
import os
import requests
import threading
import time
import json
from datetime import datetime, timedelta

class EnhancedHotelBot:
    def __init__(self):
        self.token = "8227507211:AAEGs1_BnDaJUvcK07a91MO9YK0LcosPq9I"
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.offset = 0
        self.running = False
        
        # Enhanced room data with real room numbers
        self.rooms = {
            "standard": {
                "price": 800,
                "rooms": {
                    "101": {"status": "available", "guest": None, "checkin": None, "checkout": None},
                    "102": {"status": "available", "guest": None, "checkin": None, "checkout": None},
                    "103": {"status": "occupied", "guest": "นายสมชาย", "checkin": "2025-01-20", "checkout": "2025-01-23"},
                    "104": {"status": "available", "guest": None, "checkin": None, "checkout": None},
                    "105": {"status": "maintenance", "guest": None, "checkin": None, "checkout": None},
                    "201": {"status": "available", "guest": None, "checkin": None, "checkout": None},
                    "202": {"status": "available", "guest": None, "checkin": None, "checkout": None},
                    "203": {"status": "available", "guest": None, "checkin": None, "checkout": None},
                    "204": {"status": "occupied", "guest": "นางสาวมาลี", "checkin": "2025-01-21", "checkout": "2025-01-24"},
                    "205": {"status": "available", "guest": None, "checkin": None, "checkout": None}
                }
            },
            "deluxe": {
                "price": 1200,
                "rooms": {
                    "301": {"status": "available", "guest": None, "checkin": None, "checkout": None},
                    "302": {"status": "occupied", "guest": "นายจอห์น", "checkin": "2025-01-19", "checkout": "2025-01-25"},
                    "303": {"status": "available", "guest": None, "checkin": None, "checkout": None},
                    "304": {"status": "available", "guest": None, "checkin": None, "checkout": None},
                    "305": {"status": "available", "guest": None, "checkin": None, "checkout": None}
                }
            },
            "suite": {
                "price": 2000,
                "rooms": {
                    "401": {"status": "occupied", "guest": "คุณวิภา", "checkin": "2025-01-20", "checkout": "2025-01-26"},
                    "402": {"status": "available", "guest": None, "checkin": None, "checkout": None}
                }
            }
        }
        
        self.bookings = []
        self.utilities = {"rate": 4.5}
        self.data_file = "enhanced_hotel_data.json"
        self.load_data()
        
    def load_data(self):
        """Load enhanced data"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'rooms' in data:
                        self.rooms = data['rooms']
                    if 'bookings' in data:
                        self.bookings = data['bookings']
        except:
            pass
        self.save_data()
    
    def save_data(self):
        """Save enhanced data"""
        try:
            data = {
                "rooms": self.rooms,
                "bookings": self.bookings,
                "utilities": self.utilities,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Save error: {e}")
    
    def send_message(self, chat_id, text, keyboard=None):
        """Send message"""
        payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        if keyboard:
            payload["reply_markup"] = keyboard
        try:
            response = requests.post(f"{self.base_url}/sendMessage", json=payload, timeout=10)
            return response.json().get('ok', False)
        except:
            return False
    
    def get_main_keyboard(self):
        """Enhanced keyboard"""
        return {
            "keyboard": [
                ["🏠 ห้องว่าง", "🔍 ค้นหาห้อง", "📋 รายการจอง"],
                ["👥 ผู้เข้าพัก", "🔧 จัดการห้อง", "💡 ค่าไฟน้ำ"],
                ["📊 สถิติ", "📅 ปฏิทิน", "ℹ️ ช่วยเหลือ"]
            ],
            "resize_keyboard": True
        }
    
    def handle_start(self, chat_id, user_name):
        """Enhanced start"""
        welcome = f"""🏨 <b>ยินดีต้อนรับ {user_name}!</b>

🔹 <b>จอง [ชื่อ] [เบอร์] [ประเภท] [วัน]</b> - จองห้อง
🔹 <b>เช็คอิน [เลขห้อง]</b> - เช็คอินผู้เข้าพัก
🔹 <b>เช็คเอาท์ [เลขห้อง]</b> - เช็คเอาท์
🔹 <b>ห้อง [เลขห้อง]</b> - ดูข้อมูลห้อง
🔹 <b>ค่าไฟน้ำ [หน่วย] [เลขห้อง]</b> - คำนวณค่าไฟ

<b>ประเภทห้อง:</b>
• standard (800฿) - ห้อง 101-105, 201-205
• deluxe (1,200฿) - ห้อง 301-305  
• suite (2,000฿) - ห้อง 401-402

<b>สถานะห้อง:</b>
🟢 available - ว่าง
🔴 occupied - มีผู้เข้าพัก
🟡 maintenance - ซ่อมแซม"""
        
        self.send_message(chat_id, welcome, self.get_main_keyboard())
    
    def handle_booking(self, chat_id, text):
        """Enhanced booking with real rooms"""
        parts = text.split()
        if len(parts) < 4:
            self.send_message(chat_id, "❌ <b>รูปแบบ:</b> จอง [ชื่อ] [เบอร์] [ประเภท] [จำนวนวัน]")
            return
            
        _, name, phone, room_type = parts[:4]
        days = int(parts[4]) if len(parts) > 4 else 1
        
        if room_type not in self.rooms:
            self.send_message(chat_id, "❌ <b>ประเภทห้อง:</b> standard, deluxe, suite")
            return
        
        # Find available room
        available_rooms = []
        for room_num, room_info in self.rooms[room_type]["rooms"].items():
            if room_info["status"] == "available":
                available_rooms.append(room_num)
        
        if not available_rooms:
            self.send_message(chat_id, f"❌ <b>ห้อง {room_type} เต็มทั้งหมด</b>")
            return
        
        # Assign first available room
        assigned_room = available_rooms[0]
        checkin_date = datetime.now().strftime("%Y-%m-%d")
        checkout_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        
        # Update room status
        self.rooms[room_type]["rooms"][assigned_room] = {
            "status": "occupied",
            "guest": name,
            "checkin": checkin_date,
            "checkout": checkout_date
        }
        
        # Create booking record
        booking = {
            "id": len(self.bookings) + 1,
            "name": name,
            "phone": phone,
            "room_number": assigned_room,
            "room_type": room_type,
            "price": self.rooms[room_type]["price"],
            "days": days,
            "total": self.rooms[room_type]["price"] * days,
            "checkin": checkin_date,
            "checkout": checkout_date,
            "status": "confirmed"
        }
        
        self.bookings.append(booking)
        self.save_data()
        
        response = f"""✅ <b>จองสำเร็จ!</b>

🆔 <b>รหัส:</b> #{booking['id']:03d}
👤 <b>ชื่อ:</b> {name}
📞 <b>เบอร์:</b> {phone}
🏠 <b>ห้อง:</b> {assigned_room} ({room_type})
💰 <b>ราคา:</b> {booking['price']:,} บาท/คืน
📅 <b>เข้าพัก:</b> {checkin_date}
📅 <b>ออก:</b> {checkout_date}
🗓️ <b>จำนวน:</b> {days} คืน
💵 <b>รวม:</b> {booking['total']:,} บาท"""
        
        self.send_message(chat_id, response)
    
    def handle_room_info(self, chat_id, room_number):
        """Show specific room info"""
        room_found = False
        for room_type, type_data in self.rooms.items():
            if room_number in type_data["rooms"]:
                room_info = type_data["rooms"][room_number]
                room_found = True
                
                status_emoji = {
                    "available": "🟢",
                    "occupied": "🔴", 
                    "maintenance": "🟡"
                }
                
                response = f"""🏠 <b>ห้อง {room_number}</b>

📋 <b>ประเภท:</b> {room_type}
💰 <b>ราคา:</b> {type_data['price']:,} บาท/คืน
{status_emoji.get(room_info['status'], '⚪')} <b>สถานะ:</b> {room_info['status']}"""
                
                if room_info["status"] == "occupied":
                    response += f"""
👤 <b>ผู้เข้าพัก:</b> {room_info['guest']}
📅 <b>เช็คอิน:</b> {room_info['checkin']}
📅 <b>เช็คเอาท์:</b> {room_info['checkout']}"""
                
                self.send_message(chat_id, response)
                break
        
        if not room_found:
            self.send_message(chat_id, f"❌ <b>ไม่พบห้อง {room_number}</b>")
    
    def handle_checkin(self, chat_id, room_number):
        """Handle check-in"""
        # Find booking for this room
        for booking in self.bookings:
            if booking["room_number"] == room_number and booking["status"] == "confirmed":
                booking["status"] = "checked_in"
                self.save_data()
                
                response = f"""✅ <b>เช็คอินสำเร็จ!</b>

🏠 <b>ห้อง:</b> {room_number}
👤 <b>ผู้เข้าพัก:</b> {booking['name']}
📅 <b>วันที่:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
                
                self.send_message(chat_id, response)
                return
        
        self.send_message(chat_id, f"❌ <b>ไม่พบการจองสำหรับห้อง {room_number}</b>")
    
    def handle_checkout(self, chat_id, room_number):
        """Handle check-out"""
        room_found = False
        for room_type, type_data in self.rooms.items():
            if room_number in type_data["rooms"]:
                room_info = type_data["rooms"][room_number]
                if room_info["status"] == "occupied":
                    # Clear room
                    self.rooms[room_type]["rooms"][room_number] = {
                        "status": "available",
                        "guest": None,
                        "checkin": None,
                        "checkout": None
                    }
                    
                    # Update booking status
                    for booking in self.bookings:
                        if booking["room_number"] == room_number and booking["status"] in ["confirmed", "checked_in"]:
                            booking["status"] = "checked_out"
                            break
                    
                    self.save_data()
                    
                    response = f"""✅ <b>เช็คเอาท์สำเร็จ!</b>

🏠 <b>ห้อง:</b> {room_number}
👤 <b>ผู้เข้าพัก:</b> {room_info['guest']}
📅 <b>วันที่:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}
🧹 <b>สถานะ:</b> ห้องว่างพร้อมใช้"""
                    
                    self.send_message(chat_id, response)
                    room_found = True
                    break
        
        if not room_found:
            self.send_message(chat_id, f"❌ <b>ห้อง {room_number} ไม่มีผู้เข้าพัก</b>")
    
    def handle_rooms_status(self, chat_id):
        """Enhanced room status"""
        response = "🏠 <b>สถานะห้องพักทั้งหมด</b>\n\n"
        
        for room_type, type_data in self.rooms.items():
            available = sum(1 for r in type_data["rooms"].values() if r["status"] == "available")
            occupied = sum(1 for r in type_data["rooms"].values() if r["status"] == "occupied")
            maintenance = sum(1 for r in type_data["rooms"].values() if r["status"] == "maintenance")
            total = len(type_data["rooms"])
            
            response += f"📋 <b>{room_type.upper()}</b> ({type_data['price']:,}฿)\n"
            response += f"🟢 ว่าง: {available} | 🔴 เข้าพัก: {occupied} | 🟡 ซ่อม: {maintenance}\n"
            response += f"📊 รวม: {total} ห้อง\n\n"
            
            # Show room details
            for room_num, room_info in type_data["rooms"].items():
                status_emoji = {"available": "🟢", "occupied": "🔴", "maintenance": "🟡"}
                emoji = status_emoji.get(room_info["status"], "⚪")
                
                if room_info["status"] == "occupied":
                    response += f"{emoji} {room_num}: {room_info['guest']}\n"
                else:
                    response += f"{emoji} {room_num}: {room_info['status']}\n"
            
            response += "\n"
        
        self.send_message(chat_id, response)
    
    def handle_guests_list(self, chat_id):
        """Show current guests"""
        response = "👥 <b>ผู้เข้าพักปัจจุบัน</b>\n\n"
        
        current_guests = []
        for room_type, type_data in self.rooms.items():
            for room_num, room_info in type_data["rooms"].items():
                if room_info["status"] == "occupied":
                    current_guests.append({
                        "room": room_num,
                        "guest": room_info["guest"],
                        "checkin": room_info["checkin"],
                        "checkout": room_info["checkout"],
                        "type": room_type
                    })
        
        if current_guests:
            for guest in current_guests:
                response += f"🏠 <b>ห้อง {guest['room']}</b> ({guest['type']})\n"
                response += f"👤 {guest['guest']}\n"
                response += f"📅 {guest['checkin']} → {guest['checkout']}\n\n"
        else:
            response += "📭 <b>ไม่มีผู้เข้าพักในขณะนี้</b>"
        
        self.send_message(chat_id, response)
    
    def process_message(self, message):
        """Enhanced message processing"""
        chat_id = message['chat']['id']
        text = message.get('text', '').strip()
        user_name = message['from'].get('first_name', 'Guest')
        text_lower = text.lower()
        
        if text_lower == '/start':
            self.handle_start(chat_id, user_name)
        elif text_lower.startswith('จอง'):
            self.handle_booking(chat_id, text)
        elif text_lower.startswith('ห้อง '):
            room_number = text.split()[1] if len(text.split()) > 1 else ""
            self.handle_room_info(chat_id, room_number)
        elif text_lower.startswith('เช็คอิน'):
            room_number = text.split()[1] if len(text.split()) > 1 else ""
            self.handle_checkin(chat_id, room_number)
        elif text_lower.startswith('เช็คเอาท์'):
            room_number = text.split()[1] if len(text.split()) > 1 else ""
            self.handle_checkout(chat_id, room_number)
        elif 'ห้องว่าง' in text_lower or '🏠' in text:
            self.handle_rooms_status(chat_id)
        elif 'ผู้เข้าพัก' in text_lower or '👥' in text:
            self.handle_guests_list(chat_id)
        elif text_lower.startswith('ค่าไฟน้ำ'):
            parts = text.split()
            if len(parts) >= 2:
                try:
                    units = float(parts[1])
                    room_num = parts[2] if len(parts) > 2 else "ทั่วไป"
                    cost = units * self.utilities["rate"]
                    
                    response = f"""💡 <b>ค่าไฟน้ำ</b>

🏠 <b>ห้อง:</b> {room_num}
🔢 <b>หน่วย:</b> {units:,.1f}
💰 <b>ค่าไฟ:</b> {cost:,.2f} บาท
📊 <b>อัตรา:</b> {self.utilities['rate']} บาท/หน่วย"""
                    
                    self.send_message(chat_id, response)
                except ValueError:
                    self.send_message(chat_id, "❌ <b>รูปแบบ:</b> ค่าไฟน้ำ [หน่วย] [เลขห้อง]")
            else:
                self.send_message(chat_id, "❌ <b>รูปแบบ:</b> ค่าไฟน้ำ [หน่วย] [เลขห้อง]")
        else:
            self.send_message(chat_id, "❓ <b>ไม่เข้าใจคำสั่ง</b>\n\n📝 พิมพ์ /start เพื่อดูคำสั่งทั้งหมด")
    
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
        print("🤖 Enhanced Hotel Bot started...")
        
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
    bot = EnhancedHotelBot()
    bot.start_polling()
