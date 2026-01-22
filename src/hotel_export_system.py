#!/usr/bin/env python3
"""
Hotel Export & Data Management System
"""
import os
import requests
import threading
import time
import json
import csv
from datetime import datetime, timedelta
from io import StringIO

class HotelExportBot:
    def __init__(self):
        self.token = "8227507211:AAEGs1_BnDaJUvcK07a91MO9YK0LcosPq9I"
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.offset = 0
        self.running = False
        
        # Enhanced data structure
        self.hotel_data = {
            "hotel_info": {
                "name": "Grand Hotel",
                "address": "123 ถนนสุขุมวิท กรุงเทพฯ 10110",
                "phone": "02-123-4567",
                "email": "info@grandhotel.com",
                "tax_id": "0123456789012",
                "manager": "คุณสมชาย ใจดี"
            },
            "rooms": {
                "standard": {
                    "price": 800,
                    "amenities": ["แอร์", "ทีวี", "ตู้เย็น", "ห้องน้ำในตัว"],
                    "rooms": {
                        "101": {"status": "available", "guest": None, "checkin": None, "checkout": None, "last_maintenance": "2025-01-15"},
                        "102": {"status": "available", "guest": None, "checkin": None, "checkout": None, "last_maintenance": "2025-01-16"},
                        "103": {"status": "occupied", "guest": "นายสมชาย", "checkin": "2025-01-20", "checkout": "2025-01-23", "last_maintenance": "2025-01-10"},
                        "104": {"status": "available", "guest": None, "checkin": None, "checkout": None, "last_maintenance": "2025-01-17"},
                        "105": {"status": "maintenance", "guest": None, "checkin": None, "checkout": None, "last_maintenance": "2025-01-22"},
                        "201": {"status": "available", "guest": None, "checkin": None, "checkout": None, "last_maintenance": "2025-01-14"},
                        "202": {"status": "available", "guest": None, "checkin": None, "checkout": None, "last_maintenance": "2025-01-13"},
                        "203": {"status": "available", "guest": None, "checkin": None, "checkout": None, "last_maintenance": "2025-01-18"},
                        "204": {"status": "occupied", "guest": "นางสาวมาลี", "checkin": "2025-01-21", "checkout": "2025-01-24", "last_maintenance": "2025-01-12"},
                        "205": {"status": "available", "guest": None, "checkin": None, "checkout": None, "last_maintenance": "2025-01-19"}
                    }
                },
                "deluxe": {
                    "price": 1200,
                    "amenities": ["แอร์", "ทีวี LCD", "ตู้เย็น", "ห้องน้ำในตัว", "ระเบียง", "เครื่องชงกาแฟ"],
                    "rooms": {
                        "301": {"status": "available", "guest": None, "checkin": None, "checkout": None, "last_maintenance": "2025-01-11"},
                        "302": {"status": "occupied", "guest": "นายจอห์น", "checkin": "2025-01-19", "checkout": "2025-01-25", "last_maintenance": "2025-01-09"},
                        "303": {"status": "available", "guest": None, "checkin": None, "checkout": None, "last_maintenance": "2025-01-20"},
                        "304": {"status": "available", "guest": None, "checkin": None, "checkout": None, "last_maintenance": "2025-01-21"},
                        "305": {"status": "available", "guest": None, "checkin": None, "checkout": None, "last_maintenance": "2025-01-08"}
                    }
                },
                "suite": {
                    "price": 2000,
                    "amenities": ["แอร์", "ทีวี LED 55\"", "ตู้เย็น", "ห้องน้ำในตัว", "ระเบียงใหญ่", "เครื่องชงกาแฟ", "ห้องนั่งเล่น", "อ่างอาบน้ำ"],
                    "rooms": {
                        "401": {"status": "occupied", "guest": "คุณวิภา", "checkin": "2025-01-20", "checkout": "2025-01-26", "last_maintenance": "2025-01-05"},
                        "402": {"status": "available", "guest": None, "checkin": None, "checkout": None, "last_maintenance": "2025-01-07"}
                    }
                }
            },
            "bookings": [],
            "utilities": {
                "electricity_rate": 4.5,
                "water_rate": 18.0,
                "internet_fee": 100.0,
                "cleaning_fee": 200.0
            },
            "staff": [
                {"id": 1, "name": "นางสาวสุดา", "position": "แม่บ้าน", "shift": "เช้า", "phone": "081-111-1111"},
                {"id": 2, "name": "นายสมศักดิ์", "position": "รปภ.", "shift": "กลางคืน", "phone": "081-222-2222"},
                {"id": 3, "name": "นางสาวนิดา", "position": "แผนกต้อนรับ", "shift": "เช้า", "phone": "081-333-3333"}
            ]
        }
        
        self.data_file = "complete_hotel_data.json"
        self.load_data()
        
    def load_data(self):
        """Load complete data"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    # Merge with default structure
                    for key in loaded_data:
                        if key in self.hotel_data:
                            self.hotel_data[key].update(loaded_data[key])
        except:
            pass
        self.save_data()
    
    def save_data(self):
        """Save complete data"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.hotel_data, f, ensure_ascii=False, indent=2)
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
    
    def send_document(self, chat_id, file_content, filename, caption=""):
        """Send CSV file"""
        try:
            files = {
                'document': (filename, file_content, 'text/csv')
            }
            data = {
                'chat_id': chat_id,
                'caption': caption
            }
            response = requests.post(f"{self.base_url}/sendDocument", files=files, data=data, timeout=30)
            return response.json().get('ok', False)
        except Exception as e:
            print(f"Send document error: {e}")
            return False
    
    def get_main_keyboard(self):
        """Enhanced keyboard with export options"""
        return {
            "keyboard": [
                ["🏠 ห้องว่าง", "🔍 ค้นหาห้อง", "📋 รายการจอง"],
                ["👥 ผู้เข้าพัก", "👨‍💼 พนักงาน", "💡 ค่าไฟน้ำ"],
                ["📊 รายงาน", "📁 Export CSV", "⚙️ จัดการข้อมูล"],
                ["📅 ปฏิทิน", "ℹ️ ข้อมูลโรงแรม", "🆘 ช่วยเหลือ"]
            ],
            "resize_keyboard": True
        }
    
    def export_rooms_csv(self):
        """Export rooms data to CSV"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow(['Room_Number', 'Room_Type', 'Price', 'Status', 'Guest_Name', 'Check_In', 'Check_Out', 'Last_Maintenance', 'Amenities'])
        
        # Data
        for room_type, type_data in self.hotel_data["rooms"].items():
            amenities = ", ".join(type_data["amenities"])
            for room_num, room_info in type_data["rooms"].items():
                writer.writerow([
                    room_num,
                    room_type,
                    type_data["price"],
                    room_info["status"],
                    room_info.get("guest", ""),
                    room_info.get("checkin", ""),
                    room_info.get("checkout", ""),
                    room_info.get("last_maintenance", ""),
                    amenities
                ])
        
        return output.getvalue().encode('utf-8-sig')  # BOM for Excel
    
    def export_bookings_csv(self):
        """Export bookings data to CSV"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow(['Booking_ID', 'Guest_Name', 'Phone', 'Room_Number', 'Room_Type', 'Price_Per_Night', 'Days', 'Total_Amount', 'Check_In', 'Check_Out', 'Status', 'Booking_Date'])
        
        # Data
        for booking in self.hotel_data["bookings"]:
            writer.writerow([
                booking.get("id", ""),
                booking.get("name", ""),
                booking.get("phone", ""),
                booking.get("room_number", ""),
                booking.get("room_type", ""),
                booking.get("price", ""),
                booking.get("days", 1),
                booking.get("total", ""),
                booking.get("checkin", ""),
                booking.get("checkout", ""),
                booking.get("status", ""),
                booking.get("booking_date", "")
            ])
        
        return output.getvalue().encode('utf-8-sig')
    
    def export_staff_csv(self):
        """Export staff data to CSV"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow(['Staff_ID', 'Name', 'Position', 'Shift', 'Phone'])
        
        # Data
        for staff in self.hotel_data["staff"]:
            writer.writerow([
                staff["id"],
                staff["name"],
                staff["position"],
                staff["shift"],
                staff["phone"]
            ])
        
        return output.getvalue().encode('utf-8-sig')
    
    def export_financial_report_csv(self):
        """Export financial report to CSV"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow(['Date', 'Room_Number', 'Guest_Name', 'Room_Type', 'Revenue', 'Utilities', 'Net_Income'])
        
        # Calculate financial data
        total_revenue = 0
        for booking in self.hotel_data["bookings"]:
            if booking.get("status") in ["confirmed", "checked_in", "checked_out"]:
                revenue = booking.get("total", 0)
                utilities = 50  # Estimated utilities per booking
                net_income = revenue - utilities
                total_revenue += revenue
                
                writer.writerow([
                    booking.get("checkin", ""),
                    booking.get("room_number", ""),
                    booking.get("name", ""),
                    booking.get("room_type", ""),
                    revenue,
                    utilities,
                    net_income
                ])
        
        # Summary row
        writer.writerow(["", "", "", "TOTAL", total_revenue, "", ""])
        
        return output.getvalue().encode('utf-8-sig')
    
    def handle_export_csv(self, chat_id, export_type="all"):
        """Handle CSV export requests"""
        try:
            if export_type == "rooms" or export_type == "all":
                rooms_csv = self.export_rooms_csv()
                filename = f"hotel_rooms_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                self.send_document(chat_id, rooms_csv, filename, "🏠 ข้อมูลห้องพัก")
            
            if export_type == "bookings" or export_type == "all":
                bookings_csv = self.export_bookings_csv()
                filename = f"hotel_bookings_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                self.send_document(chat_id, bookings_csv, filename, "📋 ข้อมูลการจอง")
            
            if export_type == "staff" or export_type == "all":
                staff_csv = self.export_staff_csv()
                filename = f"hotel_staff_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                self.send_document(chat_id, staff_csv, filename, "👨‍💼 ข้อมูลพนักงาน")
            
            if export_type == "financial" or export_type == "all":
                financial_csv = self.export_financial_report_csv()
                filename = f"hotel_financial_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
                self.send_document(chat_id, financial_csv, filename, "💰 รายงานการเงิน")
            
            if export_type == "all":
                self.send_message(chat_id, "✅ <b>Export ทั้งหมดเสร็จแล้ว!</b>\n\n📁 ไฟล์ CSV พร้อมนำไปใช้ในระบบฐานข้อมูล")
                
        except Exception as e:
            self.send_message(chat_id, f"❌ <b>Export ล้มเหลว:</b> {str(e)}")
    
    def handle_hotel_info(self, chat_id):
        """Show hotel information"""
        info = self.hotel_data["hotel_info"]
        response = f"""🏨 <b>ข้อมูลโรงแรม</b>

🏢 <b>ชื่อ:</b> {info['name']}
📍 <b>ที่อยู่:</b> {info['address']}
📞 <b>โทร:</b> {info['phone']}
📧 <b>อีเมล:</b> {info['email']}
🆔 <b>เลขประจำตัวผู้เสียภาษี:</b> {info['tax_id']}
👨‍💼 <b>ผู้จัดการ:</b> {info['manager']}

📊 <b>สถิติ:</b>
🏠 ห้องทั้งหมด: {sum(len(type_data['rooms']) for type_data in self.hotel_data['rooms'].values())} ห้อง
👥 พนักงาน: {len(self.hotel_data['staff'])} คน
📋 การจอง: {len(self.hotel_data['bookings'])} รายการ"""
        
        self.send_message(chat_id, response)
    
    def handle_staff_list(self, chat_id):
        """Show staff list"""
        response = "👨‍💼 <b>รายชื่อพนักงาน</b>\n\n"
        
        for staff in self.hotel_data["staff"]:
            response += f"🆔 <b>{staff['id']:02d}</b> - {staff['name']}\n"
            response += f"   💼 {staff['position']} ({staff['shift']})\n"
            response += f"   📞 {staff['phone']}\n\n"
        
        self.send_message(chat_id, response)
    
    def handle_add_room(self, chat_id, text):
        """Add new room"""
        # Format: เพิ่มห้อง [เลขห้อง] [ประเภท]
        parts = text.split()
        if len(parts) < 3:
            self.send_message(chat_id, "❌ <b>รูปแบบ:</b> เพิ่มห้อง [เลขห้อง] [ประเภท]")
            return
        
        room_number = parts[1]
        room_type = parts[2]
        
        if room_type not in self.hotel_data["rooms"]:
            self.send_message(chat_id, "❌ <b>ประเภทห้อง:</b> standard, deluxe, suite")
            return
        
        # Check if room already exists
        if room_number in self.hotel_data["rooms"][room_type]["rooms"]:
            self.send_message(chat_id, f"❌ <b>ห้อง {room_number} มีอยู่แล้ว</b>")
            return
        
        # Add new room
        self.hotel_data["rooms"][room_type]["rooms"][room_number] = {
            "status": "available",
            "guest": None,
            "checkin": None,
            "checkout": None,
            "last_maintenance": datetime.now().strftime("%Y-%m-%d")
        }
        
        self.save_data()
        
        response = f"""✅ <b>เพิ่มห้องสำเร็จ!</b>

🏠 <b>ห้อง:</b> {room_number}
📋 <b>ประเภท:</b> {room_type}
💰 <b>ราคา:</b> {self.hotel_data['rooms'][room_type]['price']:,} บาท/คืน
🟢 <b>สถานะ:</b> ว่าง"""
        
        self.send_message(chat_id, response)
    
    def process_message(self, message):
        """Enhanced message processing with export features"""
        chat_id = message['chat']['id']
        text = message.get('text', '').strip()
        user_name = message['from'].get('first_name', 'Guest')
        text_lower = text.lower()
        
        if text_lower == '/start':
            welcome = f"""🏨 <b>ยินดีต้อนรับ {user_name}!</b>

🔹 <b>จอง [ชื่อ] [เบอร์] [ประเภท] [วัน]</b> - จองห้อง
🔹 <b>ห้อง [เลขห้อง]</b> - ดูข้อมูลห้อง
🔹 <b>เช็คอิน/เช็คเอาท์ [เลขห้อง]</b>
🔹 <b>Export CSV</b> - ส่งออกข้อมูล
🔹 <b>Export [ประเภท]</b> - rooms/bookings/staff/financial
🔹 <b>เพิ่มห้อง [เลขห้อง] [ประเภท]</b> - เพิ่มห้องใหม่

<b>ข้อมูลโรงแรม:</b> ข้อมูลโรงแรม
<b>พนักงาน:</b> พนักงาน"""
            
            self.send_message(chat_id, welcome, self.get_main_keyboard())
            
        elif 'export csv' in text_lower or '📁' in text:
            self.handle_export_csv(chat_id, "all")
            
        elif text_lower.startswith('export '):
            export_type = text.split()[1] if len(text.split()) > 1 else "all"
            self.handle_export_csv(chat_id, export_type)
            
        elif 'ข้อมูลโรงแรม' in text_lower or 'ℹ️' in text:
            self.handle_hotel_info(chat_id)
            
        elif 'พนักงาน' in text_lower or '👨‍💼' in text:
            self.handle_staff_list(chat_id)
            
        elif text_lower.startswith('เพิ่มห้อง'):
            self.handle_add_room(chat_id, text)
            
        elif 'รายงาน' in text_lower or '📊' in text:
            # Generate summary report
            total_rooms = sum(len(type_data['rooms']) for type_data in self.hotel_data['rooms'].values())
            occupied_rooms = sum(1 for type_data in self.hotel_data['rooms'].values() 
                               for room in type_data['rooms'].values() 
                               if room['status'] == 'occupied')
            
            response = f"""📊 <b>รายงานสรุป</b>

🏠 <b>ห้องพัก:</b>
   • ทั้งหมด: {total_rooms} ห้อง
   • เข้าพัก: {occupied_rooms} ห้อง
   • ว่าง: {total_rooms - occupied_rooms} ห้อง
   • อัตราเข้าพัก: {(occupied_rooms/total_rooms*100):.1f}%

📋 <b>การจอง:</b> {len(self.hotel_data['bookings'])} รายการ
👥 <b>พนักงาน:</b> {len(self.hotel_data['staff'])} คน

💰 <b>รายได้รวม:</b> {sum(b.get('total', 0) for b in self.hotel_data['bookings']):,} บาท

📅 <b>วันที่:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}"""
            
            self.send_message(chat_id, response)
            
        else:
            # Import previous bot functionality here
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
        print("🤖 Hotel Export Bot started...")
        
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
    bot = HotelExportBot()
    bot.start_polling()
