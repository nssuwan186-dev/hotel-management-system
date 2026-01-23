import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'data', 'โรงแรม.db')

def seed_rooms():
    if not os.path.exists(DB_PATH):
        print("Database not found. Run upgrade_to_erp_v2.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table if missing
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ห้องพัก (
            เลขห้อง TEXT PRIMARY KEY,
            ประเภท TEXT,
            ราคา REAL,
            สถานะ TEXT DEFAULT 'ว่าง',
            วันที่อัพเดท TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Robustly add missing columns
    cursor.execute("PRAGMA table_info(ห้องพัก)")
    cols = [r[1] for r in cursor.fetchall()]
    if 'ประเภท' not in cols:
        cursor.execute("ALTER TABLE ห้องพัก ADD COLUMN ประเภท TEXT")
    if 'ราคา' not in cols:
        cursor.execute("ALTER TABLE ห้องพัก ADD COLUMN ราคา REAL")

    # Add sample rooms
    rooms = [
        ('101', 'Standard', 1200, 'ว่าง'),
        ('102', 'Standard', 1200, 'ว่าง'),
        ('201', 'Deluxe', 1800, 'ว่าง'),
        ('202', 'Deluxe', 1800, 'ว่าง'),
        ('301', 'Suite', 3500, 'ว่าง'),
    ]

    cursor.executemany("INSERT OR IGNORE INTO ห้องพัก (เลขห้อง, ประเภท, ราคา, สถานะ) VALUES (?, ?, ?, ?)", rooms)
    
    conn.commit()
    conn.close()
    print(f"✅ Seeding rooms completed in {DB_PATH}")

if __name__ == "__main__":
    seed_rooms()
