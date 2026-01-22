#!/usr/bin/env python3
"""
VIPAT Hotel ERP - Database Schema Upgrade to v2.0
อัปเกรดฐานข้อมูลให้รองรับระบบ ERP เต็มรูปแบบ
"""
import sqlite3
import os
from datetime import datetime
import shutil

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'โรงแรม.db')

def backup_database():
    """สำรองฐานข้อมูลก่อนอัปเกรด"""
    if os.path.exists(DB_PATH):
        backup_path = f"{DB_PATH}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(DB_PATH, backup_path)
        print(f"✅ สำรองข้อมูลไปที่: {backup_path}")
        return backup_path
    return None

def upgrade_schema():
    """อัปเกรด Schema ให้รองรับ ERP v2.0"""
    print("🚀 Starting Schema Upgrade to ERP v2.0 at TARGET location...")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # ==================== ID COUNTER TABLES ====================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ID_Counters (
            prefix TEXT PRIMARY KEY,
            last_value INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Daily_Counters (
            prefix TEXT NOT NULL,
            date TEXT NOT NULL,
            last_value INTEGER DEFAULT 0,
            PRIMARY KEY (prefix, date)
        )
    ''')
    
    # ==================== ENHANCED CHART OF ACCOUNTS ====================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Data_ChartOfAccounts (
            account_code TEXT PRIMARY KEY,
            account_name TEXT NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('Assets', 'Liabilities', 'Equity', 'Revenue', 'Expenses')),
            subcategory TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check for missing columns in case table exists
    cursor.execute("PRAGMA table_info(Data_ChartOfAccounts)")
    cols = [r[1] for r in cursor.fetchall()]
    if 'subcategory' not in cols:
        cursor.execute("ALTER TABLE Data_ChartOfAccounts ADD COLUMN subcategory TEXT")
    if 'is_active' not in cols:
        cursor.execute("ALTER TABLE Data_ChartOfAccounts ADD COLUMN is_active BOOLEAN DEFAULT 1")

    standard_accounts = [
        ('1010', 'เงินสดย่อยหน้า Front', 'Assets', 'Current Assets'),
        ('1020', 'เงินฝากธนาคาร', 'Assets', 'Current Assets'),
        ('1040', 'ลูกหนี้การค้า', 'Assets', 'Current Assets'),
        ('1050', 'สินค้าคงคลัง', 'Assets', 'Current Assets'),
        ('1510', 'อาคารและสิ่งปลูกสร้าง', 'Assets', 'Fixed Assets'),
        ('1520', 'เครื่องใช้สำนักงาน', 'Assets', 'Fixed Assets'),
        ('2010', 'เจ้าหนี้การค้า', 'Liabilities', 'Current Liabilities'),
        ('2030', 'ภาษีมูลค่าเพิ่มค้างจ่าย', 'Liabilities', 'Current Liabilities'),
        ('2050', 'เงินมัดจำรับล่วงหน้า', 'Liabilities', 'Current Liabilities'),
        ('2060', 'เงินเดือนค้างจ่าย', 'Liabilities', 'Current Liabilities'),
        ('3010', 'ทุนจดทะเบียน', 'Equity', 'Capital'),
        ('3110', 'กำไรสะสม', 'Equity', 'Retained Earnings'),
        ('3210', 'กำไร(ขาดทุน)สุทธิปีปัจจุบัน', 'Equity', 'Current Year'),
        ('4010', 'รายได้ค่าห้องพัก', 'Revenue', 'Room Revenue'),
        ('4110', 'รายได้อาหารและเครื่องดื่ม', 'Revenue', 'F&B Revenue'),
        ('4210', 'รายได้บริการซักรีด', 'Revenue', 'Laundry Revenue'),
        ('4910', 'รายได้อื่นๆ', 'Revenue', 'Other Revenue'),
        ('5010', 'เงินเดือนพนักงาน', 'Expenses', 'Personnel'),
        ('5110', 'ของใช้ในห้องพัก', 'Expenses', 'Operating Supplies'),
        ('5210', 'ค่าน้ำ ค่าไฟ', 'Expenses', 'Utilities'),
        ('5310', 'ค่าซ่อมบำรุง', 'Expenses', 'Maintenance'),
        ('5410', 'ค่าเสื่อมราคา', 'Expenses', 'Depreciation'),
    ]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO Data_ChartOfAccounts 
        (account_code, account_name, category, subcategory)
        VALUES (?, ?, ?, ?)
    ''', standard_accounts)
    
    # ==================== ENHANCED JOURNAL TABLES ====================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Data_Journal (
            journal_id TEXT PRIMARY KEY,
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            description TEXT NOT NULL,
            reference_id TEXT,
            status TEXT DEFAULT 'Posted' CHECK(status IN ('Draft', 'Posted', 'Voided')),
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Data_JournalEntries (
            entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
            journal_id TEXT NOT NULL,
            account_code TEXT NOT NULL,
            debit REAL DEFAULT 0 CHECK(debit >= 0),
            credit REAL DEFAULT 0 CHECK(credit >= 0),
            memo TEXT,
            FOREIGN KEY (journal_id) REFERENCES Data_Journal(journal_id) ON DELETE CASCADE,
            FOREIGN KEY (account_code) REFERENCES Data_ChartOfAccounts(account_code),
            CHECK (NOT (debit > 0 AND credit > 0))
        )
    ''')
    
    # ==================== ENHANCED BOOKINGS TABLE ====================
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Data_Bookings'")
    if cursor.fetchone():
        try: cursor.execute('ALTER TABLE Data_Bookings ADD COLUMN conflict_status BOOLEAN DEFAULT 0')
        except: pass
        try: cursor.execute('ALTER TABLE Data_Bookings ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        except: pass
    else:
        cursor.execute('''
            CREATE TABLE Data_Bookings (
                booking_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                room_number TEXT NOT NULL,
                check_in DATE NOT NULL,
                check_out DATE NOT NULL,
                status TEXT DEFAULT 'Confirmed' CHECK(status IN ('Confirmed', 'Checked-in', 'Checked-out', 'Cancelled', 'No-show')),
                total_price REAL NOT NULL CHECK(total_price >= 0),
                conflict_status BOOLEAN DEFAULT 0,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    # ==================== AUDIT LOG & CONFIG ====================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Audit_Log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT NOT NULL,
            record_id TEXT NOT NULL,
            action TEXT NOT NULL CHECK(action IN ('INSERT', 'UPDATE', 'DELETE')),
            old_value TEXT,
            new_value TEXT,
            changed_by TEXT,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS System_Config (
            config_key TEXT PRIMARY KEY,
            config_value TEXT,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    configs = [
        ('erp_version', '2.0', 'เวอร์ชันของระบบ ERP'),
        ('vat_rate', '0.07', 'อัตราภาษีมูลค่าเพิ่ม'),
        ('revenue_recognition_method', 'checkout', 'วิธีการรับรู้รายได้ (checkout/daily)'),
        ('currency', 'THB', 'สกุลเงิน'),
        ('fiscal_year_start', '01-01', 'วันเริ่มต้นปีบัญชี (MM-DD)'),
    ]
    cursor.executemany('INSERT OR REPLACE INTO System_Config (config_key, config_value, description) VALUES (?, ?, ?)', configs)
    
    conn.commit()
    conn.close()
    print("✅ Schema Upgrade Integrated at Target!")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "auto":
        upgrade_schema()
    else:
        upgrade_schema()
