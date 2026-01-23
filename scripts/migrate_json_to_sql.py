import json
import sqlite3
import os

DB_PATH = os.path.join('database', 'data', 'โรงแรม.db')
JSON_PATH = os.path.join('database', 'data', 'complete_hotel_data.json')

def migrate_data():
    if not os.path.exists(JSON_PATH):
        print(f"JSON data not found at {JSON_PATH}")
        return

    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Migrate Hotel Info to System_Config
    print("Migration: Hotel Info...")
    hotel_info = data.get('hotel_info', {})
    for key, value in hotel_info.items():
        cursor.execute('''
            INSERT OR REPLACE INTO System_Config (config_key, config_value, description)
            VALUES (?, ?, ?)
        ''', (f"hotel_{key}", str(value), f"ข้อมูลโรงแรม: {key}"))

    # 2. Migrate Rooms
    print("Migration: Rooms...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ห้องพัก (
            เลขห้อง TEXT PRIMARY KEY,
            ประเภท TEXT,
            ราคา REAL,
            สถานะ TEXT,
            วันที่อัพเดท TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    room_categories = data.get('rooms', {})
    for category_name, category_data in room_categories.items():
        price = category_data.get('price', 0)
        rooms = category_data.get('rooms', {})
        for room_no, room_info in rooms.items():
            status_thai = "ว่าง" if room_info.get('status') == 'available' else "มีผู้เข้าพัก"
            if room_info.get('status') == 'maintenance':
                status_thai = "แจ้งซ่อม"
            
            cursor.execute('''
                INSERT OR REPLACE INTO ห้องพัก (เลขห้อง, ประเภท, ราคา, สถานะ)
                VALUES (?, ?, ?, ?)
            ''', (room_no, category_name.capitalize(), price, status_thai))

    # 3. Create Staff Table if needed (Optional but good for complete context)
    print("Migration: Staff...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Data_Staff (
            staff_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            position TEXT,
            shift TEXT,
            phone TEXT
        )
    ''')
    staff_list = data.get('staff', [])
    for staff in staff_list:
        cursor.execute('''
            INSERT OR REPLACE INTO Data_Staff (staff_id, name, position, shift, phone)
            VALUES (?, ?, ?, ?, ?)
        ''', (staff.get('id'), staff.get('name'), staff.get('position'), staff.get('shift'), staff.get('phone')))

    conn.commit()
    conn.close()
    print("✅ Migration from JSON to SQL completed successfully!")

if __name__ == "__main__":
    migrate_data()
