#!/usr/bin/env python3
"""
VIPAT ERP v2.0 - Master System Integration Test (Target Integrated)
"""
import sqlite3
import os
import sys

# Add project root to path to allow absolute imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

# Import from the integrated location
from database.models.db_access_v2 import (
    get_db_connection, 
    IDGenerator, 
    EnhancedBookingEngine, 
    FinancialReporting
)

def run_integrated_test():
    print("=" * 80)
    print("🏆 VIPAT ERP v2.0 - INTEGRATED MASTER TEST")
    print("=" * 80)
    
    try:
        with get_db_connection() as conn:
            # 1. Check tables
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [r[0] for r in cursor.fetchall()]
            print(f"✅ Found {len(tables)} tables in target database.")
            
            # 2. Test ID
            res_id = IDGenerator.generate_sequential_id("RES", conn)
            print(f"✅ ID Generation: {res_id}")
            
            # 3. Test Booking
            # Ensure "ห้องพัก" exists
            conn.execute("CREATE TABLE IF NOT EXISTS ห้องพัก (เลขห้อง TEXT PRIMARY KEY, สถานะ TEXT, วันที่อัพเดท TIMESTAMP)")
            conn.execute("INSERT OR IGNORE INTO ห้องพัก (เลขห้อง, สถานะ) VALUES ('999', 'ว่าง')")
            
            result = EnhancedBookingEngine.create_booking("Integrated Test User", "999", "2026-12-01", "2026-12-05", 5000)
            if result['success']:
                print(f"✅ Integrated Booking Success: {result['booking_id']}")
                # 4. Test Checkout
                from database.models.db_access_v2 import EnhancedBookingEngine as EBE
                co_result = EBE.checkout_and_recognize_revenue(result['booking_id'])
                if co_result['success']:
                    print(f"✅ Integrated Revenue Recognition Success: {co_result['journal_id']}")
            else:
                print(f"❌ Booking Failed: {result['message']}")
                
            # 5. Financial Balance
            tb = FinancialReporting.get_trial_balance(conn)
            total_dr = sum(row['total_debit'] for row in tb)
            total_cr = sum(row['total_credit'] for row in tb)
            if round(total_dr, 2) == round(total_cr, 2):
                print(f"✅ Financial Balance Matched: {total_dr:,.2f} THB")
            else:
                print(f"❌ Financial Imbalance: Dr={total_dr}, Cr={total_cr}")

    except Exception as e:
        print(f"❌ Error during integrated test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_integrated_test()
