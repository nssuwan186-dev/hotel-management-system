#!/usr/bin/env python3
"""
Advanced Telegram Bot Features & Tricks
Hotel Management + AI + Multimedia + Games
"""
import os
import requests
import threading
import time
import json
import csv
import random
import base64
from datetime import datetime, timedelta
from io import StringIO, BytesIO
import qrcode
from PIL import Image, ImageDraw, ImageFont

class AdvancedTelegramBot:
    def __init__(self):
        self.token = "8227507211:AAEGs1_BnDaJUvcK07a91MO9YK0LcosPq9I"
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.offset = 0
        self.running = False
        
        # Hotel data (from previous system)
        self.hotel_data = {
            "hotel_info": {
                "name": "Grand Hotel AI",
                "address": "123 ถนนสุขุมวิท กรุงเทพฯ 10110",
                "phone": "02-123-4567",
                "email": "info@grandhotel.com",
                "website": "https://grandhotel.com"
            },
            "rooms": {
                "standard": {
                    "price": 800,
                    "rooms": {
                        "101": {"status": "available", "guest": None, "checkin": None, "checkout": None},
                        "102": {"status": "occupied", "guest": "นายสมชาย", "checkin": "2025-01-20", "checkout": "2025-01-23"},
                        "103": {"status": "available", "guest": None, "checkin": None, "checkout": None}
                    }
                },
                "deluxe": {
                    "price": 1200,
                    "rooms": {
                        "301": {"status": "available", "guest": None, "checkin": None, "checkout": None},
                        "302": {"status": "occupied", "guest": "นายจอห์น", "checkin": "2025-01-19", "checkout": "2025-01-25"}
                    }
                }
            },
            "bookings": [],
            "games": {
                "quiz_scores": {},
                "lottery_numbers": []
            }
        }
        
        self.data_file = "advanced_hotel_data.json"
        self.load_data()
        
    def load_data(self):
        """Load data"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    for key in loaded_data:
                        if key in self.hotel_data:
                            self.hotel_data[key].update(loaded_data[key])
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
        """Send message"""
        payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
        if keyboard:
            payload["reply_markup"] = keyboard
        try:
            response = requests.post(f"{self.base_url}/sendMessage", json=payload, timeout=10)
            return response.json().get('ok', False)
        except:
            return False
    
    def send_photo(self, chat_id, photo_data, caption=""):
        """Send photo"""
        try:
            files = {'photo': ('image.png', photo_data, 'image/png')}
            data = {'chat_id': chat_id, 'caption': caption, 'parse_mode': 'HTML'}
            response = requests.post(f"{self.base_url}/sendPhoto", files=files, data=data, timeout=30)
            return response.json().get('ok', False)
        except:
            return False
    
    def send_location(self, chat_id, latitude, longitude, title=""):
        """Send location"""
        try:
            payload = {
                "chat_id": chat_id,
                "latitude": latitude,
                "longitude": longitude
            }
            response = requests.post(f"{self.base_url}/sendLocation", json=payload, timeout=10)
            return response.json().get('ok', False)
        except:
            return False
    
    def send_poll(self, chat_id, question, options):
        """Send poll"""
        try:
            payload = {
                "chat_id": chat_id,
                "question": question,
                "options": options,
                "is_anonymous": False
            }
            response = requests.post(f"{self.base_url}/sendPoll", json=payload, timeout=10)
            return response.json().get('ok', False)
        except:
            return False
    
    def get_advanced_keyboard(self):
        """Advanced keyboard with all features"""
        return {
            "keyboard": [
                ["🏠 ห้องพัก", "📊 รายงาน", "📁 Export"],
                ["🎮 เกมส์", "🎲 สุ่ม", "📊 โพล"],
                ["📍 แผนที่", "📱 QR Code", "🖼️ รูปภาพ"],
                ["🤖 AI Chat", "🔔 แจ้งเตือน", "⚙️ ตั้งค่า"],
                ["ℹ️ ช่วยเหลือ"]
            ],
            "resize_keyboard": True
        }
    
    def generate_qr_code(self, data):
        """Generate QR code"""
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to bytes
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            return img_buffer.getvalue()
        except:
            return None
    
    def generate_hotel_card(self, room_number, guest_name, checkin, checkout):
        """Generate hotel card image"""
        try:
            # Create image
            img = Image.new('RGB', (400, 250), color='white')
            draw = ImageDraw.Draw(img)
            
            # Try to use a font (fallback to default if not available)
            try:
                font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
                font_text = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            except:
                font_title = ImageFont.load_default()
                font_text = ImageFont.load_default()
            
            # Draw hotel card
            draw.rectangle([10, 10, 390, 240], outline='blue', width=3)
            draw.text((20, 20), "🏨 GRAND HOTEL AI", fill='blue', font=font_title)
            draw.text((20, 50), f"ห้อง: {room_number}", fill='black', font=font_text)
            draw.text((20, 75), f"ผู้เข้าพัก: {guest_name}", fill='black', font=font_text)
            draw.text((20, 100), f"เช็คอิน: {checkin}", fill='black', font=font_text)
            draw.text((20, 125), f"เช็คเอาท์: {checkout}", fill='black', font=font_text)
            draw.text((20, 200), "📱 Powered by Telegram Bot", fill='gray', font=font_text)
            
            # Convert to bytes
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            return img_buffer.getvalue()
        except Exception as e:
            print(f"Image generation error: {e}")
            return None
    
    def handle_start(self, chat_id, user_name):
        """Advanced start with all features"""
        welcome = f"""🏨 <b>ยินดีต้อนรับ {user_name}!</b>

🎯 <b>ฟีเจอร์ทั้งหมด:</b>

🏠 <b>โรงแรม:</b>
• จอง [ชื่อ] [เบอร์] [ประเภท] [วัน]
• ห้อง [เลขห้อง] - ข้อมูลห้อง
• Export CSV - ส่งออกข้อมูล

🎮 <b>เกมส์ & สนุก:</b>
• เกมส์ - เล่นเกมส์
• สุ่ม - สุ่มตัวเลข/ชื่อ
• โพล - สร้างโพล

📱 <b>เทคโนโลยี:</b>
• QR [ข้อความ] - สร้าง QR Code
• แผนที่ - ตำแหน่งโรงแรม
• รูปภาพ - สร้างรูปการ์ด

🤖 <b>AI & อื่นๆ:</b>
• AI [คำถาม] - แชทกับ AI
• แจ้งเตือน - ตั้งการแจ้งเตือน
• ช่วยเหลือ - คำสั่งทั้งหมด"""
        
        self.send_message(chat_id, welcome, self.get_advanced_keyboard())
    
    def handle_games(self, chat_id):
        """Handle games menu"""
        games_keyboard = {
            "keyboard": [
                ["🧠 ควิซ", "🎰 ลอตเตอรี่", "🎯 ทายเลข"],
                ["🎲 ทอยลูกเต๋า", "🃏 ไพ่", "🎪 วงล้อ"],
                ["🏆 คะแนน", "🔙 กลับ"]
            ],
            "resize_keyboard": True
        }
        
        self.send_message(chat_id, "🎮 <b>เลือกเกมส์:</b>", games_keyboard)
    
    def handle_quiz(self, chat_id, user_id):
        """Handle quiz game"""
        questions = [
            {"q": "เมืองหลวงของไทยคือ?", "options": ["กรุงเทพฯ", "เชียงใหม่", "ภูเก็ต", "พัทยา"], "correct": 0},
            {"q": "1 + 1 = ?", "options": ["1", "2", "3", "4"], "correct": 1},
            {"q": "สีของธงไทยมีกี่สี?", "options": ["2", "3", "4", "5"], "correct": 1}
        ]
        
        question = random.choice(questions)
        
        # Send poll
        self.send_poll(chat_id, question["q"], question["options"])
        
        # Store correct answer (in real app, you'd handle poll answers)
        response = f"""🧠 <b>ควิซ!</b>

❓ <b>คำถาม:</b> {question['q']}

💡 <b>เฉลย:</b> {question['options'][question['correct']]}

🏆 <b>คะแนนของคุณ:</b> {self.hotel_data['games']['quiz_scores'].get(str(user_id), 0)} คะแนน"""
        
        self.send_message(chat_id, response)
    
    def handle_lottery(self, chat_id):
        """Handle lottery game"""
        numbers = [random.randint(1, 99) for _ in range(6)]
        numbers.sort()
        
        self.hotel_data['games']['lottery_numbers'].append({
            "numbers": numbers,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        })
        self.save_data()
        
        response = f"""🎰 <b>ลอตเตอรี่โรงแรม!</b>

🎲 <b>หมายเลขที่ออก:</b>
{' - '.join([f'{n:02d}' for n in numbers])}

📅 <b>วันที่:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}

🎁 <b>รางวัล:</b>
• ถูก 6 ตัว: ฟรี Suite 1 คืน
• ถูก 5 ตัว: ฟรี Deluxe 1 คืน  
• ถูก 4 ตัว: ส่วนลด 50%
• ถูก 3 ตัว: ส่วนลด 20%"""
        
        self.send_message(chat_id, response)
    
    def handle_random(self, chat_id, text):
        """Handle random generation"""
        parts = text.split()
        
        if len(parts) == 1:
            # Random number 1-100
            number = random.randint(1, 100)
            self.send_message(chat_id, f"🎲 <b>สุ่มตัวเลข:</b> {number}")
            
        elif parts[1].isdigit():
            # Random number 1-N
            max_num = int(parts[1])
            number = random.randint(1, max_num)
            self.send_message(chat_id, f"🎲 <b>สุ่มตัวเลข 1-{max_num}:</b> {number}")
            
        else:
            # Random from list
            items = " ".join(parts[1:]).split(",")
            if len(items) > 1:
                chosen = random.choice([item.strip() for item in items])
                self.send_message(chat_id, f"🎯 <b>สุ่มเลือก:</b> {chosen}")
            else:
                self.send_message(chat_id, "❌ <b>รูปแบบ:</b> สุ่ม [ตัวเลข] หรือ สุ่ม [รายการ,คั่น,ด้วย,จุลภาค]")
    
    def handle_qr_code(self, chat_id, text):
        """Handle QR code generation"""
        if len(text.split()) < 2:
            self.send_message(chat_id, "❌ <b>รูปแบบ:</b> QR [ข้อความ]")
            return
        
        qr_text = " ".join(text.split()[1:])
        qr_image = self.generate_qr_code(qr_text)
        
        if qr_image:
            self.send_photo(chat_id, qr_image, f"📱 <b>QR Code:</b> {qr_text}")
        else:
            self.send_message(chat_id, "❌ <b>ไม่สามารถสร้าง QR Code ได้</b>")
    
    def handle_hotel_map(self, chat_id):
        """Send hotel location"""
        # Bangkok coordinates (example)
        latitude = 13.7563
        longitude = 100.5018
        
        self.send_location(chat_id, latitude, longitude)
        self.send_message(chat_id, """📍 <b>ตำแหน่งโรงแรม</b>

🏨 <b>Grand Hotel AI</b>
📍 123 ถนนสุขุมวิท กรุงเทพฯ 10110
📞 02-123-4567
🌐 https://grandhotel.com

🚗 <b>การเดินทาง:</b>
• BTS อโศก - เดิน 5 นาที
• MRT สุขุมวิท - เดิน 3 นาที
• ท่าอากาศยานสุวรรณภูมิ - 45 นาที""")
    
    def handle_hotel_card(self, chat_id, room_number):
        """Generate and send hotel card"""
        # Find room info
        room_info = None
        for room_type, type_data in self.hotel_data["rooms"].items():
            if room_number in type_data["rooms"]:
                room_info = type_data["rooms"][room_number]
                break
        
        if not room_info or room_info["status"] != "occupied":
            self.send_message(chat_id, f"❌ <b>ห้อง {room_number} ไม่มีผู้เข้าพัก</b>")
            return
        
        card_image = self.generate_hotel_card(
            room_number,
            room_info["guest"],
            room_info["checkin"],
            room_info["checkout"]
        )
        
        if card_image:
            self.send_photo(chat_id, card_image, f"🏨 <b>การ์ดห้องพัก {room_number}</b>")
        else:
            self.send_message(chat_id, "❌ <b>ไม่สามารถสร้างการ์ดได้</b>")
    
    def handle_ai_chat(self, chat_id, text):
        """Simple AI chat simulation"""
        question = " ".join(text.split()[1:])
        
        # Simple responses (in real app, integrate with actual AI)
        responses = {
            "สวัสดี": "สวัสดีครับ! ยินดีให้บริการ 😊",
            "ขอบคุณ": "ยินดีครับ! มีอะไรให้ช่วยอีกไหม?",
            "ราคา": f"ราคาห้องพักเริ่มต้น {self.hotel_data['rooms']['standard']['price']} บาท/คืน",
            "ที่อยู่": self.hotel_data['hotel_info']['address'],
            "โทร": self.hotel_data['hotel_info']['phone']
        }
        
        # Find matching response
        response = "🤖 ขออภัย ผมยังไม่เข้าใจคำถามนี้ กรุณาลองใหม่อีกครั้ง"
        for key, value in responses.items():
            if key in question:
                response = f"🤖 {value}"
                break
        
        self.send_message(chat_id, response)
    
    def handle_notification_setup(self, chat_id):
        """Setup notifications"""
        notification_keyboard = {
            "keyboard": [
                ["🔔 เปิดแจ้งเตือน", "🔕 ปิดแจ้งเตือน"],
                ["⏰ ตั้งเวลา", "📅 ตั้งวันที่"],
                ["🔙 กลับ"]
            ],
            "resize_keyboard": True
        }
        
        response = """🔔 <b>ตั้งค่าการแจ้งเตือน</b>

📋 <b>ประเภทการแจ้งเตือน:</b>
• การจองใหม่
• การเช็คอิน/เช็คเอาท์
• ห้องว่าง
• โปรโมชั่น
• ข่าวสาร

⚙️ <b>เลือกการตั้งค่า:</b>"""
        
        self.send_message(chat_id, response, notification_keyboard)
    
    def process_message(self, message):
        """Enhanced message processing"""
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        text = message.get('text', '').strip()
        user_name = message['from'].get('first_name', 'Guest')
        text_lower = text.lower()
        
        if text_lower == '/start':
            self.handle_start(chat_id, user_name)
            
        elif 'เกมส์' in text_lower or '🎮' in text:
            self.handle_games(chat_id)
            
        elif 'ควิซ' in text_lower or '🧠' in text:
            self.handle_quiz(chat_id, user_id)
            
        elif 'ลอตเตอรี่' in text_lower or '🎰' in text:
            self.handle_lottery(chat_id)
            
        elif text_lower.startswith('สุ่ม') or '🎲' in text:
            self.handle_random(chat_id, text)
            
        elif text_lower.startswith('qr '):
            self.handle_qr_code(chat_id, text)
            
        elif 'แผนที่' in text_lower or '📍' in text:
            self.handle_hotel_map(chat_id)
            
        elif text_lower.startswith('การ์ด '):
            room_number = text.split()[1] if len(text.split()) > 1 else ""
            self.handle_hotel_card(chat_id, room_number)
            
        elif text_lower.startswith('ai '):
            self.handle_ai_chat(chat_id, text)
            
        elif 'แจ้งเตือน' in text_lower or '🔔' in text:
            self.handle_notification_setup(chat_id)
            
        elif 'ช่วยเหลือ' in text_lower or 'help' in text_lower:
            help_text = """ℹ️ <b>คำสั่งทั้งหมด</b>

🏠 <b>โรงแรม:</b>
• จอง [ชื่อ] [เบอร์] [ประเภท] [วัน]
• ห้อง [เลขห้อง]
• Export CSV

🎮 <b>เกมส์:</b>
• เกมส์ - เมนูเกมส์
• ควิซ - เล่นควิซ
• ลอตเตอรี่ - หวยโรงแรม
• สุ่ม [ตัวเลข/รายการ]

📱 <b>เทคโนโลยี:</b>
• QR [ข้อความ] - สร้าง QR Code
• แผนที่ - ตำแหน่งโรงแรม
• การ์ด [เลขห้อง] - การ์ดห้องพัก

🤖 <b>AI & อื่นๆ:</b>
• AI [คำถาม] - แชทกับ AI
• แจ้งเตือน - ตั้งการแจ้งเตือน"""
            
            self.send_message(chat_id, help_text)
            
        else:
            self.send_message(chat_id, "❓ <b>ไม่เข้าใจคำสั่ง</b>\\n\\n📝 พิมพ์ /start เพื่อดูฟีเจอร์ทั้งหมด")
    
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
        print("🤖 Advanced Telegram Bot started...")
        
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
    bot = AdvancedTelegramBot()
    bot.start_polling()
