#!/usr/bin/env python3
import sqlite3
from datetime import datetime, timedelta
from .db_access import เชื่อมต่อฐานข้อมูล, generate_id

def get_date_range(start_date, end_date):
    """สร้างรายการวันที่จาก Start Date ถึงก่อน End Date (Date-Flattening)"""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    delta = end - start
    return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(delta.days)]

def check_conflict(room_number, check_in, check_out):
    """ตรวจสอบการจองซ้อนด้วยลอจิก Date-Flattening"""
    conn = เชื่อมต่อฐานข้อมูล()
    cursor = conn.cursor()
    
    # ดึงวันที่ต้องการจองใหม่
    requested_dates = get_date_range(check_in, check_out)
    
    # ดึงรายการจองปัจจุบันของห้องนี้ที่ยังไม่ถูกยกเลิก
    cursor.execute('''
        SELECT check_in, check_out FROM Data_Bookings 
        WHERE room_number = ? AND status NOT IN ('Cancelled')
    ''', (room_number,))
    
    existing_bookings = cursor.fetchall()
    conn.close()
    
    occupied_dates = []
    for b_in, b_out in existing_bookings:
        occupied_dates.extend(get_date_range(b_in, b_out))
    
    # ตรวจสอบว่ามีวันที่ทับซ้อนกันหรือไม่
    conflicts = set(requested_dates).intersection(set(occupied_dates))
    
    return list(conflicts)

def create_booking(customer_id, room_number, check_in, check_out, total_price):
    """สร้างการจองใหม่พร้อมบันทึกบัญชีอัตโนมัติ"""
    conflicts = check_conflict(room_number, check_in, check_out)
    
    if conflicts:
        return {"success": False, "message": f"ห้องไม่ว่างในวันที่: {', '.join(conflicts)}"}
    
    conn = เชื่อมต่อฐานข้อมูล()
    cursor = conn.cursor()
    booking_id = generate_id("RES")
    
    try:
        # 1. บันทึกข้อมูลการจอง
        cursor.execute('''
            INSERT INTO Data_Bookings (booking_id, customer_id, room_number, check_in, check_out, total_price)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (booking_id, customer_id, room_number, check_in, check_out, total_price))
        
        # 2. บันทึกบัญชีอัตโนมัติ (Double-Entry)
        # Dr. 1020 เงินฝากธนาคาร | Cr. 2050 เงินมัดจำรับล่วงหน้า
        journal_id = generate_id("JNL")
        cursor.execute('INSERT INTO Data_Journal (journal_id, description, reference_id) VALUES (?, ?, ?)',
                       (journal_id, f"เงินมัดจำการจอง {booking_id}", booking_id))
        
        # รายการ Debit
        cursor.execute('INSERT INTO Data_JournalEntries (journal_id, account_code, debit) VALUES (?, ?, ?)',
                       (journal_id, '1020', total_price))
        # รายการ Credit
        cursor.execute('INSERT INTO Data_JournalEntries (journal_id, account_code, credit) VALUES (?, ?, ?)',
                       (journal_id, '2050', total_price))
        
        # 3. อัปเดตสถานะห้องพัก
        cursor.execute('UPDATE ห้องพัก SET สถานะ = "มีผู้เข้าพัก" WHERE เลขห้อง = ?', (room_number,))
        
        conn.commit()
        return {"success": True, "booking_id": booking_id}
        
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

if __name__ == "__main__":
    # ทดสอบระบบ
    print("🧪 Testing Booking Engine...")
    test_res = create_booking("CUS-TEST", "101", "2026-02-01", "2026-02-03", 2500)
    print(f"Result: {test_res}")
    
    # ทดสอบจองซ้ำ
    print("🧪 Testing Conflict Detection...")
    conflict_res = create_booking("CUS-TEST-2", "101", "2026-02-02", "2026-02-04", 2500)
    print(f"Result (Should fail): {conflict_res}")
