#!/usr/bin/env python3
"""
VIPAT Hotel ERP - Enhanced Core Engine v2.0
"""
import sqlite3
import datetime
import os
from typing import Dict, List, Optional, Tuple
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'โรงแรม.db')

@contextmanager
def get_db_connection():
    """Context Manager สำหรับ Database Connection พร้อม Transaction Support"""
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

class IDGenerator:
    @staticmethod
    def generate_sequential_id(prefix: str, conn: sqlite3.Connection) -> str:
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO ID_Counters (prefix, last_value) VALUES (?, 0)", (prefix,))
        cursor.execute("UPDATE ID_Counters SET last_value = last_value + 1 WHERE prefix = ?", (prefix,))
        cursor.execute("SELECT last_value FROM ID_Counters WHERE prefix = ?", (prefix,))
        new_value = cursor.fetchone()[0]
        return f"{prefix}-{new_value:05d}"
    
    @staticmethod
    def generate_date_based_id(prefix: str, conn: sqlite3.Connection) -> str:
        cursor = conn.cursor()
        today = datetime.datetime.now().strftime("%Y%m%d")
        cursor.execute("INSERT OR IGNORE INTO Daily_Counters (prefix, date, last_value) VALUES (?, ?, 0)", (prefix, today))
        cursor.execute("UPDATE Daily_Counters SET last_value = last_value + 1 WHERE prefix = ? AND date = ?", (prefix, today))
        cursor.execute("SELECT last_value FROM Daily_Counters WHERE prefix = ? AND date = ?", (prefix, today))
        new_value = cursor.fetchone()[0]
        return f"{prefix}-{today}-{new_value:03d}"

class DateFlatteningEngine:
    @staticmethod
    def get_date_range(start_date: str, end_date: str) -> List[str]:
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        delta = (end - start).days
        if delta <= 0:
            raise ValueError(f"วันเช็คเอาท์ ({end_date}) ต้องมากกว่าวันเช็คอิน ({start_date})")
        return [(start + datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(delta)]
    
    @staticmethod
    def create_occupancy_keys(room_number: str, dates: List[str]) -> List[str]:
        return [f"{date.replace('-', '')}_{room_number}" for date in dates]

    @staticmethod
    def check_conflict_advanced(conn: sqlite3.Connection, room_number: str, check_in: str, check_out: str, exclude_booking_id: Optional[str] = None) -> Tuple[bool, List[str]]:
        cursor = conn.cursor()
        requested_dates = DateFlatteningEngine.get_date_range(check_in, check_out)
        requested_keys = DateFlatteningEngine.create_occupancy_keys(room_number, requested_dates)
        
        query = "SELECT check_in, check_out FROM Data_Bookings WHERE room_number = ? AND status NOT IN ('Cancelled', 'Checked-out')"
        params = [room_number]
        if exclude_booking_id:
            query += " AND booking_id != ?"
            params.append(exclude_booking_id)
        
        cursor.execute(query, params)
        existing_bookings = cursor.fetchall()
        occupied_keys = set()
        for b in existing_bookings:
            dates = DateFlatteningEngine.get_date_range(b['check_in'], b['check_out'])
            occupied_keys.update(DateFlatteningEngine.create_occupancy_keys(room_number, dates))
        
        conflict_keys = set(requested_keys).intersection(occupied_keys)
        if conflict_keys:
            conflict_dates = sorted([f"{k[:4]}-{k[4:6]}-{k[6:8]}" for k in conflict_keys])
            return True, conflict_dates
        return False, []

class AccountingEngine:
    TEMPLATES = {
        "deposit_received": {
            "description": "รับเงินมัดจำการจอง",
            "entries": [
                {"account": "1020", "type": "debit"},
                {"account": "2050", "type": "credit"}
            ]
        },
        "revenue_recognition": {
            "description": "รับรู้รายได้ค่าห้องพัก",
            "entries": [
                {"account": "2050", "type": "debit"},
                {"account": "4010", "type": "credit", "amount_formula": "main / 1.07"},
                {"account": "2030", "type": "credit", "amount_formula": "main - (main / 1.07)"}
            ]
        },
        "utility_income": {
            "description": "รายได้ค่าสาธารณูปโภค (ไฟ/น้ำ)",
            "entries": [
                {"account": "1020", "type": "debit"},
                {"account": "4020", "type": "credit"}
            ]
        }
    }
    
    @staticmethod
    def create_journal_entry(conn: sqlite3.Connection, template_name: str, amount: float, reference_id: str, additional_description: str = "") -> str:
        template = AccountingEngine.TEMPLATES.get(template_name)
        if not template: raise ValueError(f"Template '{template_name}' not found")
        
        journal_id = IDGenerator.generate_date_based_id("JNL", conn)
        description = f"{template['description']} {additional_description}".strip()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Data_Journal (journal_id, description, reference_id) VALUES (?, ?, ?)", (journal_id, description, reference_id))
        
        total_debit, total_credit = 0.0, 0.0
        for entry in template['entries']:
            entry_amount = eval(entry['amount_formula'], {'main': amount}) if 'amount_formula' in entry else amount
            if entry['type'] == 'debit':
                cursor.execute("INSERT INTO Data_JournalEntries (journal_id, account_code, debit, credit) VALUES (?, ?, ?, 0)", (journal_id, entry['account'], entry_amount))
                total_debit += entry_amount
            else:
                cursor.execute("INSERT INTO Data_JournalEntries (journal_id, account_code, debit, credit) VALUES (?, ?, 0, ?)", (journal_id, entry['account'], entry_amount))
                total_credit += entry_amount
        
        if round(total_debit, 2) != round(total_credit, 2):
            raise ValueError(f"Balance Error: Dr={total_debit}, Cr={total_credit}")
        return journal_id

class EnhancedBookingEngine:
    @staticmethod
    def create_booking(customer_name: str, room_number: str, check_in: str, check_out: str, total_price: float) -> Dict:
        try:
            with get_db_connection() as conn:
                has_conflict, dates = DateFlatteningEngine.check_conflict_advanced(conn, room_number, check_in, check_out)
                if has_conflict: return {"success": False, "message": f"Conflict: {dates}"}
                
                booking_id = IDGenerator.generate_sequential_id("RES", conn)
                conn.execute("INSERT INTO Data_Bookings (booking_id, customer_id, room_number, check_in, check_out, total_price, status) VALUES (?, ?, ?, ?, ?, ?, 'Confirmed')",
                             (booking_id, customer_name, room_number, check_in, check_out, total_price))
                
                journal_id = AccountingEngine.create_journal_entry(conn, "deposit_received", total_price, booking_id, f"ห้อง {room_number}")
                return {"success": True, "booking_id": booking_id, "journal_id": journal_id, "message": "Success"}
        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def checkout_and_recognize_revenue(booking_id: str) -> Dict:
        """
        Check-out และรับรู้รายได้ตามหลักบัญชี
        """
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM Data_Bookings WHERE booking_id = ?", (booking_id,))
                booking = cursor.fetchone()
                if not booking: return {"success": False, "message": "Booking not found"}
                if booking['status'] == 'Checked-out': return {"success": False, "message": "Already checked-out"}

                journal_id = AccountingEngine.create_journal_entry(
                    conn=conn,
                    template_name="revenue_recognition",
                    amount=booking['total_price'],
                    reference_id=booking_id,
                    additional_description=f"ห้อง {booking['room_number']}"
                )

                cursor.execute("UPDATE Data_Bookings SET status = 'Checked-out' WHERE booking_id = ?", (booking_id,))
                cursor.execute("UPDATE ห้องพัก SET สถานะ = 'ว่าง', วันที่อัพเดท = CURRENT_TIMESTAMP WHERE เลขห้อง = ?", (booking['room_number'],))
                
                return {"success": True, "journal_id": journal_id, "message": "Checkout and Revenue Recognition Success"}
        except Exception as e:
            return {"success": False, "message": str(e)}

class FinancialReporting:
    """
    ระบบรายงานทางการเงินแบบ Real-time
    """
    
    @staticmethod
    def get_trial_balance(conn: sqlite3.Connection) -> List[Dict]:
        """
        ดึงงบทดลอง (Trial Balance) เพื่อตรวจสอบความสมดุล
        """
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                c.account_code,
                c.account_name,
                c.category,
                COALESCE(SUM(e.debit), 0) as total_debit,
                COALESCE(SUM(e.credit), 0) as total_credit,
                COALESCE(SUM(e.debit - e.credit), 0) as balance
            FROM Data_ChartOfAccounts c
            LEFT JOIN Data_JournalEntries e ON c.account_code = e.account_code
            GROUP BY c.account_code, c.account_name, c.category
            ORDER BY c.account_code
        ''')
        
        return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_income_statement(conn: sqlite3.Connection) -> Dict:
        """
        งบกำไรขาดทุน (Income Statement)
        """
        cursor = conn.cursor()
        
        # รายได้ (Revenue - Category 4)
        cursor.execute('''
            SELECT COALESCE(SUM(e.credit - e.debit), 0) as revenue
            FROM Data_JournalEntries e
            JOIN Data_ChartOfAccounts c ON e.account_code = c.account_code
            WHERE c.category = 'Revenue'
        ''')
        row = cursor.fetchone()
        revenue = row['revenue'] if row else 0
        
        # ค่าใช้จ่าย (Expenses - Category 5)
        cursor.execute('''
            SELECT COALESCE(SUM(e.debit - e.credit), 0) as expenses
            FROM Data_JournalEntries e
            JOIN Data_ChartOfAccounts c ON e.account_code = c.account_code
            WHERE c.category = 'Expenses'
        ''')
        row = cursor.fetchone()
        expenses = row['expenses'] if row else 0
        
        net_profit = revenue - expenses
        
        return {
            "revenue": revenue,
            "expenses": expenses,
            "net_profit": net_profit,
            "profit_margin": (net_profit / revenue * 100) if revenue > 0 else 0
        }

class HospitalityOperations:
    @staticmethod
    def calculate_utilities(room_number: str, electricity_old: float, electricity_new: float, water_old: float, water_new: float, electricity_rate: float = 8.0, water_rate: float = 20.0) -> Dict:
        """
        คำนวณค่าไฟน้ำและบันทึกบัญชีรายได้
        """
        try:
            elec_unit = electricity_new - electricity_old
            water_unit = water_new - water_old
            
            if elec_unit < 0 or water_unit < 0:
                return {"success": False, "message": "ค่าใหม่ต้องไม่น้อยกว่าค่าเก่า"}
            
            elec_price = elec_unit * electricity_rate
            water_price = water_unit * water_rate
            total = elec_price + water_price
            
            with get_db_connection() as conn:
                journal_id = AccountingEngine.create_journal_entry(
                    conn=conn,
                    template_name="utility_income",
                    amount=total,
                    reference_id=f"UTIL-{room_number}",
                    additional_description=f"ค่าไฟ {elec_unit}u, ค่าน้ำ {water_unit}u ห้อง {room_number}"
                )
                
            return {
                "success": True,
                "data": {
                    "room": room_number,
                    "units": {"elec": elec_unit, "water": water_unit},
                    "prices": {"elec": elec_price, "water": water_price},
                    "total": total,
                    "journal_id": journal_id
                }
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

if __name__ == "__main__":
    print("VIPAT ERP Core Engine v2.0 Integrated")
