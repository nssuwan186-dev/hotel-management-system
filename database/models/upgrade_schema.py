#!/usr/bin/env python3
import sqlite3
import os

def upgrade():
    db_path = 'database/data/โรงแรม.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("🚀 Starting Database Schema Upgrade...")

    # 1. ตารางผังบัญชี (Chart of Accounts)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Data_ChartOfAccounts (
        account_code TEXT PRIMARY KEY,
        account_name TEXT NOT NULL,
        category TEXT NOT NULL, -- Assets, Liabilities, Equity, Revenue, Expenses
        balance REAL DEFAULT 0
    )''')

    # 2. ตารางสมุดรายวันทั่วไป (General Journal) - ระบบบัญชีคู่
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Data_Journal (
        journal_id TEXT PRIMARY KEY,
        transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        description TEXT,
        reference_id TEXT, -- Booking_ID or TXN_ID
        status TEXT DEFAULT 'Posted'
    )''')

    # 3. ตารางรายการย่อยในสมุดรายวัน (Journal Entries)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Data_JournalEntries (
        entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
        journal_id TEXT,
        account_code TEXT,
        debit REAL DEFAULT 0,
        credit REAL DEFAULT 0,
        FOREIGN KEY (journal_id) REFERENCES Data_Journal(journal_id),
        FOREIGN KEY (account_code) REFERENCES Data_ChartOfAccounts(account_code)
    )''')

    # 4. ตารางประวัติการจอง (Enhanced Bookings)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Data_Bookings (
        booking_id TEXT PRIMARY KEY,
        customer_id TEXT,
        room_number TEXT,
        check_in DATE,
        check_out DATE,
        status TEXT DEFAULT 'Confirmed', -- Confirmed, Checked-in, Checked-out, Cancelled, Conflict
        total_price REAL,
        conflict_status BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (room_number) REFERENCES ห้องพัก(เลขห้อง)
    )''')

    # ใส่ข้อมูลผังบัญชีเบื้องต้น
    initial_accounts = [
        ('1010', 'เงินสดย่อยหน้า Front', 'Assets'),
        ('1020', 'เงินฝากธนาคาร', 'Assets'),
        ('2050', 'เงินมัดจำรับล่วงหน้า', 'Liabilities'),
        ('4010', 'รายได้ค่าห้องพัก', 'Revenue'),
        ('5010', 'เงินเดือนพนักงาน', 'Expenses'),
        ('5210', 'ค่าน้ำ ค่าไฟ', 'Expenses')
    ]
    cursor.executemany('INSERT OR IGNORE INTO Data_ChartOfAccounts (account_code, account_name, category) VALUES (?, ?, ?)', initial_accounts)

    conn.commit()
    conn.close()
    print("✅ Database Schema Upgraded Successfully!")

if __name__ == "__main__":
    upgrade()
