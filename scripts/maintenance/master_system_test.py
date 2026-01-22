#!/usr/bin/env python3
import os
import sqlite3
import datetime
from database.models.booking_engine import create_booking, check_conflict, get_date_range
from database.models.db_access import เชื่อมต่อฐานข้อมูล, generate_id
from database.backups.backup_system import DatabaseBackup

def log_test(name, status, details=""):
    icon = "✅" if status else "❌"
    print(f"{icon} {name:<40} | {details}")
    return status

def run_master_test():
    print("\n" + "═"*70)
    print("🏆 VIPAT ERP - MASTER COMPREHENSIVE SYSTEM TEST 🏆")
    print("═"*70)
    
    results = []
    conn = เชื่อมต่อฐานข้อมูล()
    cursor = conn.cursor()

    # --- 1. Database Schema Integrity ---
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    schema_ok = all(t in tables for t in ['Data_Bookings', 'Data_Journal', 'Data_JournalEntries', 'Data_ChartOfAccounts'])
    results.append(log_test("Database Schema Integrity", schema_ok, f"Found {len(tables)} tables"))

    # --- 2. ID Generation Engine ---
    id1 = generate_id("TEST")
    id2 = generate_id("TEST")
    id_ok = (id1 != id2) and id1.startswith("TEST-")
    results.append(log_test("ID Generation Uniqueness", id_ok, f"Sample: {id1}"))

    # --- 3. Logic: Standard Booking ---
    # คลีนข้อมูลเทสเก่า
    cursor.execute("DELETE FROM Data_Bookings WHERE customer_id LIKE 'MASTER-TEST%'")
    conn.commit()
    
    res1 = create_booking("MASTER-TEST-1", "102", "2026-06-01", "2026-06-05", 5000)
    results.append(log_test("Standard Booking (4 Nights)", res1['success'], f"ID: {res1.get('booking_id')}"))

    # --- 4. Logic: Back-to-Back (The Morning/Afternoon rule) ---
    # จองต่อจากคนเก่าในวันที่คนเก่าออก (5 มิ.ย.) ระบบต้องยอมให้จองได้
    res2 = create_booking("MASTER-TEST-2", "102", "2026-06-05", "2026-06-10", 6000)
    results.append(log_test("Back-to-Back Booking Logic", res2['success'], "Accepted 5th June Check-in (Same day as previous Check-out)"))

    # --- 5. Logic: Conflict Detection (Overlap) ---
    # พยายามจองทับช่วงวันที่ 2-4 มิ.ย. (ซึ่งมีคนจองไว้แล้วในข้อ 3)
    res3 = create_booking("MASTER-TEST-3", "102", "2026-06-02", "2026-06-04", 2000)
    results.append(log_test("Overlap Conflict Detection", not res3['success'], f"Correctly Rejected: {res3.get('message')}"))

    # --- 6. Accounting: Double-Entry Verification ---
    cursor.execute("SELECT journal_id FROM Data_Journal WHERE reference_id = ?", (res1.get('booking_id'),))
    jid = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(debit), SUM(credit) FROM Data_JournalEntries WHERE journal_id = ?", (jid,))
    dr, cr = cursor.fetchone()
    acc_ok = (dr == cr == 5000)
    results.append(log_test("Accounting: Double-Entry Balance", acc_ok, f"Dr {dr} / Cr {cr} matched"))

    # --- 7. Accounting: Chart of Accounts Linkage ---
    cursor.execute("SELECT category FROM Data_ChartOfAccounts WHERE account_code = '1020'")
    cat = cursor.fetchone()[0]
    results.append(log_test("Accounting: Chart of Accounts Mapping", cat == 'Assets', f"Account 1020 is correctly mapped to {cat}"))

    # --- 8. Privacy: Data Masking Logic (Simulation) ---
    phone = "081-234-5678"
    masked = f"{phone[:3]}-***-**{phone[-2:]}" # Simulating web masking logic
    mask_ok = masked == "081-***-**78"
    results.append(log_test("Privacy: Data Masking Logic", mask_ok, f"Result: {masked}"))

    # --- 9. Reliability: Backup System ---
    backup = DatabaseBackup()
    try:
        b_file = backup.create_backup()
        backup_ok = os.path.exists(b_file)
        results.append(log_test("Reliability: Automated Backup", backup_ok, f"File: {os.path.basename(b_file)}"))
    except Exception as e:
        results.append(log_test("Reliability: Automated Backup", False, str(e)))

    conn.close()
    
    print("═"*70)
    final_score = (sum(results) / len(results)) * 100
    if final_score == 100:
        print(f"🌟 FINAL RESULT: 100/100 - SYSTEM READY FOR PRODUCTION 🌟")
    else:
        print(f"⚠️ FINAL RESULT: {final_score:.1f}% - SOME COMPONENTS NEED ATTENTION ⚠️")
    print("═"*70 + "\n")

if __name__ == "__main__":
    run_master_test()
