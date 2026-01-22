#!/usr/bin/env python3
import os
import sqlite3
import json
from database.models.booking_engine import create_booking, check_conflict, get_date_range
from database.models.db_access import เชื่อมต่อฐานข้อมูล

def test_database_structure():
    print("🔍 1. Testing Database Structure...")
    tables_needed = ['Data_Bookings', 'Data_ChartOfAccounts', 'Data_Journal', 'Data_JournalEntries', 'ห้องพัก']
    conn = เชื่อมต่อฐานข้อมูล()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [t[0] for t in cursor.fetchall()]
    conn.close()
    
    for table in tables_needed:
        if table in existing_tables:
            print(f"   ✅ Table '{table}' exists.")
        else:
            print(f"   ❌ Table '{table}' MISSING!")
            return False
    return True

def test_booking_and_accounting():
    print("\n🔍 2. Testing Booking & Accounting Logic...")
    room = "101"
    check_in = "2026-05-01"
    check_out = "2026-05-05"
    price = 4000.0
    
    # 2.1 Clean up previous test data if exists
    conn = เชื่อมต่อฐานข้อมูล()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Data_JournalEntries WHERE journal_id IN (SELECT journal_id FROM Data_Journal WHERE description LIKE '%Integration Test%')")
    cursor.execute("DELETE FROM Data_Journal WHERE description LIKE '%Integration Test%'")
    cursor.execute("DELETE FROM Data_Bookings WHERE customer_id = 'CUS-INT-TEST'")
    conn.commit()
    
    # 2.2 Create Booking
    print(f"   📅 Booking Room {room} for {check_in} to {check_out}...")
    result = create_booking("CUS-INT-TEST", room, check_in, check_out, price)
    
    if result['success']:
        print(f"   ✅ Booking Created: {result['booking_id']}")
    else:
        print(f"   ❌ Booking Failed: {result['message']}")
        return False
        
    # 2.3 Check Accounting Balance
    print("   💰 Checking Accounting Balance (Double-Entry)...")
    cursor.execute("SELECT SUM(debit), SUM(credit) FROM Data_JournalEntries WHERE journal_id IN (SELECT journal_id FROM Data_Journal WHERE reference_id = ?)", (result['booking_id'],))
    dr, cr = cursor.fetchone()
    if dr == cr == price:
        print(f"   ✅ Balance Match: Dr {dr} == Cr {cr}")
    else:
        print(f"   ❌ Balance Mismatch: Dr {dr} vs Cr {cr}")
        return False
        
    # 2.4 Test Conflict Detection
    print("   🚫 Testing Conflict Detection (Booking overlapping dates)...")
    conflict_result = create_booking("CUS-INT-TEST-2", room, "2026-05-03", "2026-05-06", 1000.0)
    if not conflict_result['success'] and "ห้องไม่ว่าง" in conflict_result['message']:
        print(f"   ✅ Conflict detected correctly: {conflict_result['message']}")
    else:
        print(f"   ❌ Conflict Detection FAILED!")
        return False
    
    conn.close()
    return True

def test_web_api_mock():
    print("\n🔍 3. Testing Web Data Integration...")
    conn = เชื่อมต่อฐานข้อมูล()
    cursor = conn.cursor()
    
    # Test Financial Summary Logic (Same as Web/Bot)
    cursor.execute("SELECT SUM(debit - credit) FROM Data_JournalEntries WHERE account_code = '1020'")
    cash = cursor.fetchone()[0] or 0
    print(f"   ✅ Web Data: Total Cash in System = {cash:,.2f} ฿")
    
    conn.close()
    return True

if __name__ == "__main__":
    print("🧪 STARTING FULL SYSTEM INTEGRATION TEST 🧪")
    print("="*45)
    
    results = [
        test_database_structure(),
        test_booking_and_accounting(),
        test_web_api_mock()
    ]
    
    print("\n" + "="*45)
    if all(results):
        print("🏆 FINAL RESULT: SYSTEM 100% OPERATIONAL 🏆")
    else:
        print("❌ FINAL RESULT: SYSTEM HAS ERRORS ❌")
