#!/usr/bin/env python3
"""
Enhanced Hotel Mini App with Telegram's Latest Features
Checklists + Suggested Posts + Advanced UI
"""
import os
import requests
import threading
import time
import json
import csv
from datetime import datetime, timedelta
from io import StringIO

class EnhancedHotelApp:
    def __init__(self):
        self.token = "8227507211:AAEGs1_BnDaJUvcK07a91MO9YK0LcosPq9I"
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.offset = 0
        self.running = False
        
        # Enhanced database with new features
        self.hotel_db = {
            "guests": [
                {"id": 1, "name": "นายสมชาย ใจดี", "phone": "081-234-5678", "room": "102", "checkin": "2025-01-20", "checkout": "2025-01-23"},
                {"id": 2, "name": "นางสาวมาลี สวยงาม", "phone": "082-345-6789", "room": "301", "checkin": "2025-01-21", "checkout": "2025-01-25"}
            ],
            "rooms": {
                "101": {"type": "standard", "status": "available", "guest_id": None, "price": 800},
                "102": {"type": "standard", "status": "occupied", "guest_id": 1, "price": 800},
                "103": {"type": "standard", "status": "available", "guest_id": None, "price": 800},
                "201": {"type": "deluxe", "status": "available", "guest_id": None, "price": 1200},
                "202": {"type": "deluxe", "status": "maintenance", "guest_id": None, "price": 1200},
                "301": {"type": "suite", "status": "occupied", "guest_id": 2, "price": 2000}
            },
            "checklists": [],
            "tasks": [],
            "suggestions": [],
            "staff_tasks": [],
            "maintenance_tasks": []
        }
        
        self.data_file = "enhanced_hotel_db.json"
        self.load_data()
        
    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.hotel_db = json.load(f)
        except:
            pass
        self.save_data()
    
    def save_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.hotel_db, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def send_message(self, chat_id, text, keyboard=None, parse_mode="HTML"):
        payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
        if keyboard:
            payload["reply_markup"] = keyboard
        try:
            response = requests.post(f"{self.base_url}/sendMessage", json=payload, timeout=10)
            return response.json().get('ok', False)
        except:
            return False
    
    def get_main_menu(self):
        """Enhanced main menu with new features"""
        return {
            "keyboard": [
                ["👥 ผู้เข้าพัก", "🏠 ห้องพัก", "📋 การจอง"],
                ["✅ Checklists", "💡 Suggestions", "🛠️ Tasks"],
                ["👨‍💼 พนักงาน", "💰 การเงิน", "📊 รายงาน"],
                ["📁 Export", "⚙️ ตั้งค่า", "ℹ️ ช่วยเหลือ"]
            ],
            "resize_keyboard": True
        }
    
    def get_checklist_menu(self):
        """Checklist management menu"""
        return {
            "keyboard": [
                ["➕ สร้าง Checklist", "📋 ดู Checklists"],
                ["🏠 Checklist ห้องพัก", "👨‍💼 Checklist พนักงาน"],
                ["🛠️ Checklist ซ่อมแซม", "🧹 Checklist ทำความสะอาด"],
                ["🔙 กลับเมนูหลัก"]
            ],
            "resize_keyboard": True
        }
    
    def show_dashboard(self, chat_id):
        """Enhanced dashboard with checklists and tasks"""
        # Calculate statistics
        total_rooms = len(self.hotel_db["rooms"])
        occupied_rooms = sum(1 for room in self.hotel_db["rooms"].values() if room["status"] == "occupied")
        available_rooms = sum(1 for room in self.hotel_db["rooms"].values() if room["status"] == "available")
        
        # Task statistics
        total_tasks = len(self.hotel_db.get("tasks", []))
        completed_tasks = sum(1 for task in self.hotel_db.get("tasks", []) if task.get("completed", False))
        pending_tasks = total_tasks - completed_tasks
        
        # Checklist statistics
        total_checklists = len(self.hotel_db.get("checklists", []))
        
        dashboard = f"""🏨 <b>Enhanced Hotel Dashboard</b>

📊 <b>สถิติห้องพัก:</b>
🏠 ทั้งหมด: {total_rooms} ห้อง
🔴 เข้าพัก: {occupied_rooms} ห้อง ({(occupied_rooms/total_rooms*100):.1f}%)
🟢 ว่าง: {available_rooms} ห้อง

✅ <b>Task Management:</b>
📋 Checklists: {total_checklists} รายการ
🛠️ Tasks ทั้งหมด: {total_tasks} งาน
✅ เสร็จแล้ว: {completed_tasks} งาน
⏳ รอดำเนินการ: {pending_tasks} งาน

👥 <b>ผู้เข้าพัก:</b> {len(self.hotel_db["guests"])} คน

📅 <b>วันที่:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}

<b>🎯 เลือกเมนูด้านล่าง</b>"""
        
        self.send_message(chat_id, dashboard, self.get_main_menu())
    
    def create_checklist(self, chat_id, checklist_type="general"):
        """Create different types of checklists"""
        checklist_templates = {
            "room_cleaning": {
                "title": "🧹 Checklist ทำความสะอาดห้อง",
                "tasks": [
                    "🛏️ เปลี่ยนผ้าปูที่นอน",
                    "🚿 ทำความสะอาดห้องน้ำ",
                    "🧽 เช็ดฝุ่นเฟอร์นิเจอร์",
                    "🗑️ เทขยะ",
                    "🧹 ดูดฝุ่นพรม",
                    "🪟 เช็ดกระจก",
                    "🧴 เติมอุปกรณ์ห้องน้ำ",
                    "❄️ ตรวจสอบแอร์",
                    "📺 ตรวจสอบอุปกรณ์",
                    "✅ ตรวจสอบความเรียบร้อย"
                ]
            },
            "maintenance": {
                "title": "🛠️ Checklist ซ่อมแซม",
                "tasks": [
                    "🔧 ตรวจสอบก๊อกน้ำ",
                    "💡 ตรวจสอบหลอดไฟ",
                    "❄️ ตรวจสอบแอร์",
                    "🚪 ตรวจสอบประตู-หน้าต่าง",
                    "🔌 ตรวจสอบปลั๊กไฟ",
                    "📺 ตรวจสอบทีวี",
                    "🛏️ ตรวจสอบเฟอร์นิเจอร์",
                    "🚿 ตรวจสอบฝักบัว",
                    "🔒 ตรวจสอบล็อค",
                    "📋 บันทึกผลการตรวจสอบ"
                ]
            },
            "checkin": {
                "title": "📋 Checklist เช็คอิน",
                "tasks": [
                    "🆔 ตรวจสอบบัตรประชาชน",
                    "📝 กรอกข้อมูลผู้เข้าพัก",
                    "💳 รับชำระเงิน",
                    "🗝️ มอบกุญแจห้อง",
                    "📍 แนะนำสิ่งอำนวยความสะดวก",
                    "📞 แจ้งเบอร์ติดต่อ",
                    "🅿️ แจ้งที่จอดรถ",
                    "🍽️ แนะนำร้านอาหาร",
                    "📋 ให้ข้อมูลโรงแรม",
                    "✅ ยืนยันการเช็คอิน"
                ]
            },
            "staff_daily": {
                "title": "👨‍💼 Checklist งานประจำวัน",
                "tasks": [
                    "⏰ เช็คเวลาเข้างาน",
                    "👔 ตรวจสอบเครื่องแบบ",
                    "📋 รับมอบหมายงาน",
                    "🏠 ตรวจสอบห้องพัก",
                    "👥 ดูแลผู้เข้าพัก",
                    "📞 รับโทรศัพท์",
                    "🧹 ดูแลความสะอาด",
                    "💰 จัดการการเงิน",
                    "📊 บันทึกรายงาน",
                    "🔄 ส่งมอบงานกะต่อไป"
                ]
            }
        }
        
        template = checklist_templates.get(checklist_type, checklist_templates["room_cleaning"])
        
        # Create checklist
        checklist_id = len(self.hotel_db["checklists"]) + 1
        checklist = {
            "id": checklist_id,
            "title": template["title"],
            "type": checklist_type,
            "created_by": chat_id,
            "created_date": datetime.now().isoformat(),
            "tasks": []
        }
        
        # Add tasks
        for i, task_title in enumerate(template["tasks"]):
            task = {
                "id": i + 1,
                "title": task_title,
                "completed": False,
                "completed_by": None,
                "completed_date": None
            }
            checklist["tasks"].append(task)
        
        self.hotel_db["checklists"].append(checklist)
        self.save_data()
        
        # Show checklist with interactive buttons
        self.show_checklist(chat_id, checklist_id)
    
    def show_checklist(self, chat_id, checklist_id):
        """Show interactive checklist"""
        checklist = next((c for c in self.hotel_db["checklists"] if c["id"] == checklist_id), None)
        if not checklist:
            self.send_message(chat_id, "❌ ไม่พบ Checklist")
            return
        
        # Calculate progress
        total_tasks = len(checklist["tasks"])
        completed_tasks = sum(1 for task in checklist["tasks"] if task["completed"])
        progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Progress bar
        progress_bar = "▓" * int(progress / 10) + "░" * (10 - int(progress / 10))
        
        checklist_text = f"""✅ <b>{checklist['title']}</b>

📊 <b>ความคืบหน้า:</b> [{progress_bar}] {progress:.0f}%
✅ เสร็จแล้ว: {completed_tasks}/{total_tasks} งาน

📋 <b>รายการงาน:</b>

"""
        
        # Create inline keyboard for tasks
        keyboard = {"inline_keyboard": []}
        
        for task in checklist["tasks"]:
            status_emoji = "✅" if task["completed"] else "☐"
            button_text = f"{status_emoji} {task['title']}"
            callback_data = f"toggle_task_{checklist_id}_{task['id']}"
            
            keyboard["inline_keyboard"].append([{
                "text": button_text,
                "callback_data": callback_data
            }])
        
        # Add control buttons
        keyboard["inline_keyboard"].append([
            {"text": "🔄 รีเซ็ต", "callback_data": f"reset_checklist_{checklist_id}"},
            {"text": "📊 สถิติ", "callback_data": f"stats_checklist_{checklist_id}"}
        ])
        
        self.send_message(chat_id, checklist_text, keyboard)
    
    def show_all_checklists(self, chat_id):
        """Show all checklists"""
        if not self.hotel_db["checklists"]:
            self.send_message(chat_id, "📋 <b>ยังไม่มี Checklist</b>", self.get_checklist_menu())
            return
        
        checklists_text = "📋 <b>Checklists ทั้งหมด</b>\n\n"
        
        for checklist in self.hotel_db["checklists"]:
            total_tasks = len(checklist["tasks"])
            completed_tasks = sum(1 for task in checklist["tasks"] if task["completed"])
            progress = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            status_emoji = "✅" if progress == 100 else "⏳" if progress > 0 else "📋"
            
            checklists_text += f"{status_emoji} <b>{checklist['title']}</b>\n"
            checklists_text += f"   📊 {completed_tasks}/{total_tasks} งาน ({progress:.0f}%)\n"
            checklists_text += f"   📅 {checklist['created_date'][:10]}\n\n"
        
        # Create keyboard for checklist selection
        keyboard = {"inline_keyboard": []}
        for checklist in self.hotel_db["checklists"]:
            keyboard["inline_keyboard"].append([{
                "text": f"📋 {checklist['title']}",
                "callback_data": f"view_checklist_{checklist['id']}"
            }])
        
        self.send_message(chat_id, checklists_text, keyboard)
    
    def handle_suggestions(self, chat_id):
        """Handle suggestion system"""
        suggestions_menu = {
            "keyboard": [
                ["💡 เสนอไอเดีย", "📝 เสนอปรับปรุง"],
                ["🎯 เสนอบริการใหม่", "💰 เสนอโปรโมชั่น"],
                ["📋 ดูข้อเสนอแนะ", "⭐ โหวตไอเดีย"],
                ["🔙 กลับเมนูหลัก"]
            ],
            "resize_keyboard": True
        }
        
        suggestions_text = """💡 <b>ระบบข้อเสนอแนะ</b>

🎯 <b>ประเภทข้อเสนอแนะ:</b>
• 💡 ไอเดียใหม่ๆ
• 📝 ปรับปรุงบริการ
• 🎯 บริการเพิ่มเติม
• 💰 โปรโมชั่น

✨ <b>คุณสามารถ:</b>
• เสนอไอเดียใหม่
• โหวตไอเดียที่ชอบ
• ดูข้อเสนอแนะทั้งหมด
• ติดตามสถานะ

<b>เลือกเมนูด้านล่าง:</b>"""
        
        self.send_message(chat_id, suggestions_text, suggestions_menu)
    
    def create_suggestion(self, chat_id, suggestion_type):
        """Create new suggestion"""
        suggestion_id = len(self.hotel_db["suggestions"]) + 1
        
        # For demo, create sample suggestions
        sample_suggestions = {
            "idea": {
                "title": "💡 เพิ่มบริการ Room Service 24 ชั่วโมง",
                "description": "เสนอให้มีบริการส่งอาหารถึงห้องตลอด 24 ชั่วโมง",
                "category": "บริการ"
            },
            "improvement": {
                "title": "📝 ปรับปรุงระบบ Wi-Fi",
                "description": "เพิ่มความเร็วและความเสถียรของ Wi-Fi ในทุกห้อง",
                "category": "เทคโนโลยี"
            },
            "service": {
                "title": "🎯 บริการรถรับส่งสนามบิน",
                "description": "เพิ่มบริการรถรับส่งสนามบินสำหรับผู้เข้าพัก",
                "category": "การขนส่ง"
            },
            "promotion": {
                "title": "💰 โปรโมชั่นพักยาว",
                "description": "ส่วนลด 20% สำหรับการพักตั้งแต่ 7 คืนขึ้นไป",
                "category": "การตลาด"
            }
        }
        
        suggestion_data = sample_suggestions.get(suggestion_type, sample_suggestions["idea"])
        
        suggestion = {
            "id": suggestion_id,
            "title": suggestion_data["title"],
            "description": suggestion_data["description"],
            "category": suggestion_data["category"],
            "suggested_by": chat_id,
            "date": datetime.now().isoformat(),
            "votes": 0,
            "status": "pending",
            "voters": []
        }
        
        self.hotel_db["suggestions"].append(suggestion)
        self.save_data()
        
        response = f"""✅ <b>เสนอไอเดียสำเร็จ!</b>

💡 <b>หัวข้อ:</b> {suggestion['title']}
📝 <b>รายละเอียด:</b> {suggestion['description']}
🏷️ <b>หมวดหมู่:</b> {suggestion['category']}
📅 <b>วันที่:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}

🎯 <b>ข้อเสนอแนะของคุณจะได้รับการพิจารณา</b>
⭐ <b>ผู้อื่นสามารถโหวตสนับสนุนได้</b>"""
        
        self.send_message(chat_id, response)
    
    def show_suggestions(self, chat_id):
        """Show all suggestions with voting"""
        if not self.hotel_db["suggestions"]:
            self.send_message(chat_id, "💡 <b>ยังไม่มีข้อเสนอแนะ</b>")
            return
        
        suggestions_text = "💡 <b>ข้อเสนอแนะทั้งหมด</b>\n\n"
        
        # Create keyboard for voting
        keyboard = {"inline_keyboard": []}
        
        for suggestion in self.hotel_db["suggestions"]:
            status_emoji = {
                "pending": "⏳",
                "approved": "✅", 
                "rejected": "❌",
                "implemented": "🎉"
            }.get(suggestion["status"], "⏳")
            
            suggestions_text += f"{status_emoji} <b>{suggestion['title']}</b>\n"
            suggestions_text += f"   📝 {suggestion['description']}\n"
            suggestions_text += f"   🏷️ {suggestion['category']} | ⭐ {suggestion['votes']} โหวต\n"
            suggestions_text += f"   📅 {suggestion['date'][:10]}\n\n"
            
            # Add vote button
            keyboard["inline_keyboard"].append([{
                "text": f"⭐ โหวต ({suggestion['votes']})",
                "callback_data": f"vote_suggestion_{suggestion['id']}"
            }])
        
        self.send_message(chat_id, suggestions_text, keyboard)
    
    def process_callback(self, callback_query):
        """Process inline keyboard callbacks"""
        chat_id = callback_query['message']['chat']['id']
        callback_data = callback_query['data']
        
        # Answer callback
        try:
            requests.post(f"{self.base_url}/answerCallbackQuery", 
                         json={"callback_query_id": callback_query['id']}, timeout=5)
        except:
            pass
        
        if callback_data.startswith("toggle_task_"):
            # Toggle task completion
            parts = callback_data.split("_")
            checklist_id = int(parts[2])
            task_id = int(parts[3])
            
            checklist = next((c for c in self.hotel_db["checklists"] if c["id"] == checklist_id), None)
            if checklist:
                task = next((t for t in checklist["tasks"] if t["id"] == task_id), None)
                if task:
                    task["completed"] = not task["completed"]
                    if task["completed"]:
                        task["completed_by"] = chat_id
                        task["completed_date"] = datetime.now().isoformat()
                    else:
                        task["completed_by"] = None
                        task["completed_date"] = None
                    
                    self.save_data()
                    self.show_checklist(chat_id, checklist_id)
        
        elif callback_data.startswith("view_checklist_"):
            checklist_id = int(callback_data.split("_")[2])
            self.show_checklist(chat_id, checklist_id)
        
        elif callback_data.startswith("vote_suggestion_"):
            suggestion_id = int(callback_data.split("_")[2])
            suggestion = next((s for s in self.hotel_db["suggestions"] if s["id"] == suggestion_id), None)
            if suggestion and chat_id not in suggestion["voters"]:
                suggestion["votes"] += 1
                suggestion["voters"].append(chat_id)
                self.save_data()
                self.send_message(chat_id, "⭐ <b>โหวตสำเร็จ!</b> ขอบคุณสำหรับการสนับสนุน")
            else:
                self.send_message(chat_id, "❌ <b>คุณโหวตไอเดียนี้แล้ว</b>")
    
    def process_message(self, message):
        """Enhanced message processing"""
        chat_id = message['chat']['id']
        text = message.get('text', '').strip()
        user_name = message['from'].get('first_name', 'Guest')
        
        if text == '/start':
            self.show_dashboard(chat_id)
            
        elif text == "✅ Checklists":
            self.send_message(chat_id, "✅ <b>Checklist Management</b>\n\nเลือกประเภท Checklist:", self.get_checklist_menu())
            
        elif text == "➕ สร้าง Checklist":
            create_menu = {
                "keyboard": [
                    ["🧹 ทำความสะอาดห้อง", "🛠️ ซ่อมแซม"],
                    ["📋 เช็คอิน", "👨‍💼 งานประจำวัน"],
                    ["🔙 กลับ"]
                ],
                "resize_keyboard": True
            }
            self.send_message(chat_id, "➕ <b>เลือกประเภท Checklist:</b>", create_menu)
            
        elif text == "🧹 ทำความสะอาดห้อง":
            self.create_checklist(chat_id, "room_cleaning")
            
        elif text == "🛠️ ซ่อมแซม":
            self.create_checklist(chat_id, "maintenance")
            
        elif text == "📋 เช็คอิน":
            self.create_checklist(chat_id, "checkin")
            
        elif text == "👨‍💼 งานประจำวัน":
            self.create_checklist(chat_id, "staff_daily")
            
        elif text == "📋 ดู Checklists":
            self.show_all_checklists(chat_id)
            
        elif text == "💡 Suggestions":
            self.handle_suggestions(chat_id)
            
        elif text == "💡 เสนอไอเดีย":
            self.create_suggestion(chat_id, "idea")
            
        elif text == "📝 เสนอปรับปรุง":
            self.create_suggestion(chat_id, "improvement")
            
        elif text == "🎯 เสนอบริการใหม่":
            self.create_suggestion(chat_id, "service")
            
        elif text == "💰 เสนอโปรโมชั่น":
            self.create_suggestion(chat_id, "promotion")
            
        elif text == "📋 ดูข้อเสนอแนะ":
            self.show_suggestions(chat_id)
            
        elif text == "🔙 กลับเมนูหลัก" or text == "🔙 กลับ":
            self.show_dashboard(chat_id)
            
        else:
            self.send_message(chat_id, "❓ <b>ไม่เข้าใจคำสั่ง</b>\n\n📱 กดปุ่มเมนูด้านล่างเพื่อใช้งาน")
    
    def get_updates(self):
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
        self.running = True
        print("🤖 Enhanced Hotel App with Checklists started...")
        
        while self.running:
            try:
                updates = self.get_updates()
                if updates and updates.get('ok'):
                    for update in updates.get('result', []):
                        self.offset = update['update_id'] + 1
                        if 'message' in update:
                            self.process_message(update['message'])
                        elif 'callback_query' in update:
                            self.process_callback(update['callback_query'])
            except Exception as e:
                print(f"Polling error: {e}")
                time.sleep(5)

if __name__ == "__main__":
    bot = EnhancedHotelApp()
    bot.start_polling()
