#!/usr/bin/env python3
"""
Telegram Interactive Forms & UI Components
"""
import os
import requests
import threading
import time
import json
from datetime import datetime

class TelegramFormBot:
    def __init__(self):
        self.token = "8227507211:AAEGs1_BnDaJUvcK07a91MO9YK0LcosPq9I"
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.offset = 0
        self.running = False
        
        # Form sessions - track user form progress
        self.form_sessions = {}
        
        # Hotel data
        self.hotel_data = {
            "registrations": [],
            "bookings": [],
            "feedback": []
        }
        
        self.data_file = "form_data.json"
        self.load_data()
        
    def load_data(self):
        """Load data"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.hotel_data = json.load(f)
        except:
            pass
        self.save_data()
    
    def save_data(self):
        """Save data"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.hotel_data, f, ensure_ascii=False, indent=2)
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
    
    def get_main_keyboard(self):
        """Main menu with form options"""
        return {
            "keyboard": [
                ["📝 ลงทะเบียน", "🏨 จองห้อง", "💬 แสดงความคิดเห็น"],
                ["👤 โปรไฟล์", "📋 ข้อมูลของฉัน", "📊 สถิติ"],
                ["⚙️ ตั้งค่า", "ℹ️ ช่วยเหลือ"]
            ],
            "resize_keyboard": True
        }
    
    def get_inline_keyboard(self, options):
        """Create inline keyboard"""
        keyboard = []
        row = []
        for i, option in enumerate(options):
            row.append({"text": option["text"], "callback_data": option["data"]})
            if (i + 1) % 2 == 0 or i == len(options) - 1:  # 2 buttons per row
                keyboard.append(row)
                row = []
        return {"inline_keyboard": keyboard}
    
    def create_form_ui(self, form_type, step=0):
        """Create form UI with progress"""
        forms = {
            "register": {
                "title": "📝 ลงทะเบียนสมาชิก",
                "steps": [
                    {"field": "name", "prompt": "👤 กรุณาใส่ชื่อ-นามสกุล:", "type": "text"},
                    {"field": "phone", "prompt": "📞 กรุณาใส่เบอร์โทรศัพท์:", "type": "text"},
                    {"field": "email", "prompt": "📧 กรุณาใส่อีเมล:", "type": "text"},
                    {"field": "age", "prompt": "🎂 กรุณาเลือกช่วงอายุ:", "type": "select", 
                     "options": ["18-25", "26-35", "36-45", "46-55", "55+"]},
                    {"field": "gender", "prompt": "👫 กรุณาเลือกเพศ:", "type": "select",
                     "options": ["ชาย", "หญิง", "ไม่ระบุ"]},
                    {"field": "interests", "prompt": "🎯 กรุณาเลือกความสนใจ:", "type": "multi_select",
                     "options": ["ท่องเที่ยว", "อาหาร", "กีฬา", "ช้อปปิ้ง", "ธุรกิจ"]}
                ]
            },
            "booking": {
                "title": "🏨 จองห้องพัก",
                "steps": [
                    {"field": "guest_name", "prompt": "👤 ชื่อผู้เข้าพัก:", "type": "text"},
                    {"field": "phone", "prompt": "📞 เบอร์โทรศัพท์:", "type": "text"},
                    {"field": "room_type", "prompt": "🏠 เลือกประเภทห้อง:", "type": "select",
                     "options": ["Standard (800฿)", "Deluxe (1,200฿)", "Suite (2,000฿)"]},
                    {"field": "checkin", "prompt": "📅 วันเช็คอิน (DD/MM/YYYY):", "type": "text"},
                    {"field": "checkout", "prompt": "📅 วันเช็คเอาท์ (DD/MM/YYYY):", "type": "text"},
                    {"field": "guests", "prompt": "👥 จำนวนผู้เข้าพัก:", "type": "select",
                     "options": ["1 คน", "2 คน", "3 คน", "4 คน", "5+ คน"]},
                    {"field": "special_requests", "prompt": "📝 ความต้องการพิเศษ (ถ้ามี):", "type": "text"}
                ]
            },
            "feedback": {
                "title": "💬 แสดงความคิดเห็น",
                "steps": [
                    {"field": "rating", "prompt": "⭐ ให้คะแนนบริการ:", "type": "select",
                     "options": ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]},
                    {"field": "service_type", "prompt": "🏨 ประเภทบริการ:", "type": "select",
                     "options": ["ห้องพัก", "อาหาร", "พนักงาน", "สิ่งอำนวยความสะดวก", "อื่นๆ"]},
                    {"field": "comment", "prompt": "💭 ความคิดเห็น/ข้อเสนอแนะ:", "type": "text"},
                    {"field": "recommend", "prompt": "👍 แนะนำให้เพื่อนไหม:", "type": "select",
                     "options": ["แนะนำ", "ไม่แนะนำ", "ไม่แน่ใจ"]}
                ]
            }
        }
        return forms.get(form_type)
    
    def start_form(self, chat_id, form_type):
        """Start interactive form"""
        form_config = self.create_form_ui(form_type)
        if not form_config:
            self.send_message(chat_id, "❌ ไม่พบแบบฟอร์มที่ต้องการ")
            return
        
        # Initialize form session
        self.form_sessions[chat_id] = {
            "type": form_type,
            "step": 0,
            "data": {},
            "config": form_config
        }
        
        # Send form header with progress
        total_steps = len(form_config["steps"])
        progress_bar = "▓" * 1 + "░" * (total_steps - 1)
        
        header = f"""📋 <b>{form_config['title']}</b>

📊 <b>ความคืบหน้า:</b> [{progress_bar}] 1/{total_steps}

{self.get_step_prompt(chat_id)}"""
        
        self.send_message(chat_id, header, self.get_step_keyboard(chat_id))
    
    def get_step_prompt(self, chat_id):
        """Get current step prompt"""
        session = self.form_sessions.get(chat_id)
        if not session:
            return "❌ ไม่พบเซสชันแบบฟอร์ม"
        
        current_step = session["config"]["steps"][session["step"]]
        return current_step["prompt"]
    
    def get_step_keyboard(self, chat_id):
        """Get keyboard for current step"""
        session = self.form_sessions.get(chat_id)
        if not session:
            return None
        
        current_step = session["config"]["steps"][session["step"]]
        
        if current_step["type"] == "select":
            # Single select with inline keyboard
            options = []
            for option in current_step["options"]:
                options.append({"text": option, "data": f"select_{option}"})
            return self.get_inline_keyboard(options)
            
        elif current_step["type"] == "multi_select":
            # Multi select with checkboxes
            options = []
            selected = session["data"].get(current_step["field"], [])
            for option in current_step["options"]:
                checkbox = "☑️" if option in selected else "☐"
                options.append({"text": f"{checkbox} {option}", "data": f"multi_{option}"})
            
            # Add done button
            options.append({"text": "✅ เสร็จแล้ว", "data": "multi_done"})
            return self.get_inline_keyboard(options)
            
        else:
            # Text input - show skip option if optional
            return {
                "keyboard": [
                    ["⏭️ ข้าม (ถ้าไม่บังคับ)"],
                    ["❌ ยกเลิก"]
                ],
                "resize_keyboard": True
            }
    
    def process_form_input(self, chat_id, text=None, callback_data=None):
        """Process form input"""
        session = self.form_sessions.get(chat_id)
        if not session:
            return
        
        current_step = session["config"]["steps"][session["step"]]
        field_name = current_step["field"]
        
        # Handle different input types
        if callback_data:
            if callback_data.startswith("select_"):
                # Single select
                value = callback_data.replace("select_", "")
                session["data"][field_name] = value
                self.next_form_step(chat_id)
                
            elif callback_data.startswith("multi_"):
                # Multi select
                if callback_data == "multi_done":
                    self.next_form_step(chat_id)
                else:
                    option = callback_data.replace("multi_", "")
                    if field_name not in session["data"]:
                        session["data"][field_name] = []
                    
                    if option in session["data"][field_name]:
                        session["data"][field_name].remove(option)
                    else:
                        session["data"][field_name].append(option)
                    
                    # Update keyboard
                    self.send_message(chat_id, self.get_step_prompt(chat_id), self.get_step_keyboard(chat_id))
        
        elif text:
            if text == "❌ ยกเลิก":
                self.cancel_form(chat_id)
                return
            elif text == "⏭️ ข้าม (ถ้าไม่บังคับ)":
                session["data"][field_name] = ""
                self.next_form_step(chat_id)
                return
            else:
                # Text input
                session["data"][field_name] = text
                self.next_form_step(chat_id)
    
    def next_form_step(self, chat_id):
        """Move to next form step"""
        session = self.form_sessions.get(chat_id)
        if not session:
            return
        
        session["step"] += 1
        total_steps = len(session["config"]["steps"])
        
        if session["step"] >= total_steps:
            # Form completed
            self.complete_form(chat_id)
        else:
            # Show next step
            current_step = session["step"] + 1
            progress_bar = "▓" * current_step + "░" * (total_steps - current_step)
            
            header = f"""📋 <b>{session['config']['title']}</b>

📊 <b>ความคืบหน้า:</b> [{progress_bar}] {current_step}/{total_steps}

{self.get_step_prompt(chat_id)}"""
            
            self.send_message(chat_id, header, self.get_step_keyboard(chat_id))
    
    def complete_form(self, chat_id):
        """Complete form and save data"""
        session = self.form_sessions.get(chat_id)
        if not session:
            return
        
        form_data = {
            "type": session["type"],
            "data": session["data"],
            "timestamp": datetime.now().isoformat(),
            "chat_id": chat_id
        }
        
        # Save to appropriate collection
        if session["type"] == "register":
            self.hotel_data["registrations"].append(form_data)
        elif session["type"] == "booking":
            self.hotel_data["bookings"].append(form_data)
        elif session["type"] == "feedback":
            self.hotel_data["feedback"].append(form_data)
        
        self.save_data()
        
        # Show completion message with summary
        summary = self.format_form_summary(session)
        
        completion_msg = f"""✅ <b>เสร็จสิ้น!</b>

📋 <b>{session['config']['title']}</b>

{summary}

🎉 <b>ขอบคุณสำหรับข้อมูล!</b>
📧 เราจะติดต่อกลับภายใน 24 ชั่วโมง"""
        
        # Clear session
        del self.form_sessions[chat_id]
        
        self.send_message(chat_id, completion_msg, self.get_main_keyboard())
    
    def format_form_summary(self, session):
        """Format form data summary"""
        summary = ""
        for field, value in session["data"].items():
            if isinstance(value, list):
                value = ", ".join(value)
            
            # Format field names
            field_names = {
                "name": "👤 ชื่อ",
                "guest_name": "👤 ชื่อผู้เข้าพัก",
                "phone": "📞 เบอร์โทร",
                "email": "📧 อีเมล",
                "age": "🎂 อายุ",
                "gender": "👫 เพศ",
                "interests": "🎯 ความสนใจ",
                "room_type": "🏠 ประเภทห้อง",
                "checkin": "📅 เช็คอิน",
                "checkout": "📅 เช็คเอาท์",
                "guests": "👥 จำนวนผู้เข้าพัก",
                "special_requests": "📝 ความต้องการพิเศษ",
                "rating": "⭐ คะแนน",
                "service_type": "🏨 ประเภทบริการ",
                "comment": "💭 ความคิดเห็น",
                "recommend": "👍 แนะนำ"
            }
            
            field_display = field_names.get(field, field)
            summary += f"{field_display}: {value}\\n"
        
        return summary
    
    def cancel_form(self, chat_id):
        """Cancel current form"""
        if chat_id in self.form_sessions:
            del self.form_sessions[chat_id]
        
        self.send_message(chat_id, "❌ <b>ยกเลิกการกรอกแบบฟอร์ม</b>", self.get_main_keyboard())
    
    def show_user_data(self, chat_id):
        """Show user's submitted data"""
        user_registrations = [r for r in self.hotel_data["registrations"] if r["chat_id"] == chat_id]
        user_bookings = [b for b in self.hotel_data["bookings"] if b["chat_id"] == chat_id]
        user_feedback = [f for f in self.hotel_data["feedback"] if f["chat_id"] == chat_id]
        
        response = f"""📋 <b>ข้อมูลของคุณ</b>

📝 <b>การลงทะเบียน:</b> {len(user_registrations)} รายการ
🏨 <b>การจอง:</b> {len(user_bookings)} รายการ
💬 <b>ความคิดเห็น:</b> {len(user_feedback)} รายการ

📊 <b>สถิติรวม:</b>
• ลงทะเบียนทั้งหมด: {len(self.hotel_data['registrations'])} คน
• การจองทั้งหมด: {len(self.hotel_data['bookings'])} รายการ
• ความคิดเห็นทั้งหมด: {len(self.hotel_data['feedback'])} รายการ"""
        
        self.send_message(chat_id, response)
    
    def process_message(self, message):
        """Process messages and callbacks"""
        chat_id = message['chat']['id']
        text = message.get('text', '').strip()
        user_name = message['from'].get('first_name', 'Guest')
        
        # Check if user is in form session
        if chat_id in self.form_sessions:
            self.process_form_input(chat_id, text=text)
            return
        
        # Handle menu commands
        if text == '/start':
            welcome = f"""🏨 <b>ยินดีต้อนรับ {user_name}!</b>

📋 <b>แบบฟอร์มอินเทอร์แอคทีฟ</b>

เลือกแบบฟอร์มที่ต้องการกรอก:
• 📝 ลงทะเบียนสมาชิก
• 🏨 จองห้องพัก  
• 💬 แสดงความคิดเห็น

หรือดูข้อมูลของคุณ:
• 👤 โปรไฟล์
• 📋 ข้อมูลของฉัน"""
            
            self.send_message(chat_id, welcome, self.get_main_keyboard())
            
        elif text == "📝 ลงทะเบียน":
            self.start_form(chat_id, "register")
            
        elif text == "🏨 จองห้อง":
            self.start_form(chat_id, "booking")
            
        elif text == "💬 แสดงความคิดเห็น":
            self.start_form(chat_id, "feedback")
            
        elif text == "📋 ข้อมูลของฉัน":
            self.show_user_data(chat_id)
            
        else:
            self.send_message(chat_id, "❓ <b>ไม่เข้าใจคำสั่ง</b>\\n\\n📝 พิมพ์ /start เพื่อเริ่มใช้งาน")
    
    def process_callback(self, callback_query):
        """Process inline keyboard callbacks"""
        chat_id = callback_query['message']['chat']['id']
        callback_data = callback_query['data']
        
        # Answer callback to remove loading state
        try:
            requests.post(f"{self.base_url}/answerCallbackQuery", 
                         json={"callback_query_id": callback_query['id']}, timeout=5)
        except:
            pass
        
        # Process form callback
        if chat_id in self.form_sessions:
            self.process_form_input(chat_id, callback_data=callback_data)
    
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
        print("🤖 Telegram Form Bot started...")
        
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
    bot = TelegramFormBot()
    bot.start_polling()
