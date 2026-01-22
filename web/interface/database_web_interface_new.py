#!/usr/bin/env python3
import http.server
import socketserver
import json
import sqlite3
from urllib.parse import urlparse, parse_qs
from database.models.booking_engine import create_booking, check_conflict

import os

PORT = int(os.environ.get('PORT', 8000))
DB_PATH = 'database/data/โรงแรม.db'

class DatabaseWebInterface(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        """จัดการการส่งข้อมูลจากฟอร์ม (เช่น การจองห้อง)"""
        if self.path == '/api/create_booking':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode('utf-8'))
            
            result = create_booking(
                customer_id=params.get('customer_name'),
                room_number=params.get('room_number'),
                check_in=params.get('check_in'),
                check_out=params.get('check_out'),
                total_price=float(params.get('total_price', 0))
            )
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

    def do_GET(self):
        if self.path == '/':
            self.serve_interface()
        elif self.path == '/api/bookings':
            self.serve_bookings()
        elif self.path == '/api/accounting':
            self.serve_accounting()
        elif self.path == '/api/rooms':
            self.serve_rooms()
        else:
            self.send_error(404)

    def serve_rooms(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT เลขห้อง, ประเภท, ราคา, สถานะ FROM ห้องพัก ORDER BY เลขห้อง")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        self.send_json(rows)

    def serve_bookings(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Data_Bookings ORDER BY created_at DESC")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        self.send_json(rows)

    def serve_accounting(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT j.journal_id, j.transaction_date, j.description, 
                   e.account_code, c.account_name, e.debit, e.credit
            FROM Data_Journal j
            JOIN Data_JournalEntries e ON j.journal_id = e.journal_id
            JOIN Data_ChartOfAccounts c ON e.account_code = c.account_code
            ORDER BY j.transaction_date DESC
        ''')
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        self.send_json(rows)

    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def serve_interface(self):
        html = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VIPAT HOTEL - Full ERP System</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        .tab-content.hidden { display: none; }
        .calendar-day { min-height: 100px; border: 1px solid #e2e8f0; padding: 4px; font-size: 0.75rem; transition: all 0.2s; }
        .calendar-day:hover { background-color: #f8fafc; }
        .has-booking { background-color: #fee2e2; border-top: 4px solid #ef4444; }
        .status-badge { padding: 2px 8px; border-radius: 12px; font-size: 0.7rem; font-weight: bold; }
    </style>
</head>
<body class="bg-slate-50 font-sans text-slate-800">
    <div class="flex h-screen overflow-hidden">
        <!-- Sidebar -->
        <aside class="w-64 bg-slate-900 text-slate-300 flex flex-col shrink-0">
            <div class="p-6 border-b border-slate-700">
                <h1 class="text-xl font-bold text-white">VIPAT ERP v2.1</h1>
                <div class="flex items-center gap-2 mt-2">
                    <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span class="text-xs text-green-400">System 100% Ready</span>
                </div>
            </div>
            <nav class="flex-1 p-4 space-y-2 overflow-y-auto">
                <button onclick="showTab('dashboard')" class="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800 transition-colors" data-tab="dashboard">
                    <i data-lucide="layout-dashboard" class="w-5 h-5"></i> ภาพรวม
                </button>
                <button onclick="showTab('booking-form')" class="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800 transition-colors text-blue-400 font-bold" data-tab="booking-form">
                    <i data-lucide="plus-circle" class="w-5 h-5"></i> จองห้องพักใหม่
                </button>
                <button onclick="showTab('gantt')" class="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800 transition-colors" data-tab="gantt">
                    <i data-lucide="calendar" class="w-5 h-5"></i> ปฏิทิน Gantt
                </button>
                <button onclick="showTab('accounting')" class="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800 transition-colors" data-tab="accounting">
                    <i data-lucide="dollar-sign" class="w-5 h-5"></i> ระบบบัญชีคู่
                </button>
            </nav>
        </aside>

        <!-- Main Content -->
        <main class="flex-1 overflow-y-auto p-8">
            <!-- Dashboard -->
            <div id="dashboard" class="tab-content space-y-6">
                <h2 class="text-3xl font-bold text-slate-800">แผงควบคุมหลัก</h2>
                <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                        <p class="text-sm text-slate-500 mb-1">ยอดเงินสด (1020)</p>
                        <h3 id="stat-cash" class="text-2xl font-black text-blue-600">0฿</h3>
                    </div>
                    <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                        <p class="text-sm text-slate-500 mb-1">รายได้สะสม</p>
                        <h3 id="stat-revenue" class="text-2xl font-black text-green-600">0฿</h3>
                    </div>
                    <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                        <p class="text-sm text-slate-500 mb-1">การจองทั้งหมด</p>
                        <h3 id="stat-bookings" class="text-2xl font-black text-slate-800">0</h3>
                    </div>
                    <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                        <p class="text-sm text-slate-500 mb-1">ความเสถียรระบบ</p>
                        <h3 class="text-2xl font-black text-indigo-600">100%</h3>
                    </div>
                </div>

                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
                    <div class="bg-white p-6 rounded-2xl shadow-sm border">
                        <h4 class="font-bold text-lg mb-4">รายการจองล่าสุด</h4>
                        <div id="recent-bookings-list" class="space-y-3"></div>
                    </div>
                    <div class="bg-white p-6 rounded-2xl shadow-sm border">
                        <h4 class="font-bold text-lg mb-4">สถานะห้องพักด่วน</h4>
                        <div id="room-status-grid" class="grid grid-cols-5 gap-2"></div>
                    </div>
                </div>
            </div>

            <!-- Booking Form -->
            <div id="booking-form" class="tab-content hidden max-w-2xl mx-auto">
                <div class="bg-white p-8 rounded-3xl shadow-xl border border-blue-100">
                    <h2 class="text-2xl font-bold mb-6 flex items-center gap-2 text-blue-700">
                        <i data-lucide="plus-circle"></i> สร้างการจองใหม่ (ERP)
                    </h2>
                    <form id="new-booking-form" class="space-y-4">
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium mb-1">ชื่อลูกค้า</label>
                                <input type="text" id="cust_name" required class="w-full p-3 bg-slate-50 border rounded-xl outline-blue-500">
                            </div>
                            <div>
                                <label class="block text-sm font-medium mb-1">เลขห้อง</label>
                                <select id="room_select" required class="w-full p-3 bg-slate-50 border rounded-xl"></select>
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <label class="block text-sm font-medium mb-1">วันเช็คอิน</label>
                                <input type="date" id="check_in" required class="w-full p-3 bg-slate-50 border rounded-xl">
                            </div>
                            <div>
                                <label class="block text-sm font-medium mb-1">วันเช็คเอาท์</label>
                                <input type="date" id="check_out" required class="w-full p-3 bg-slate-50 border rounded-xl">
                            </div>
                        </div>
                        <div>
                            <label class="block text-sm font-medium mb-1">ราคารวม (เงินมัดจำ)</label>
                            <input type="number" id="total_price" required class="w-full p-3 bg-slate-50 border rounded-xl text-xl font-bold text-blue-600">
                        </div>
                        <button type="submit" class="w-full bg-blue-600 text-white py-4 rounded-xl font-bold text-lg hover:bg-blue-700 transition-all shadow-lg shadow-blue-200">
                            ยืนยันการจองและลงบัญชีอัตโนมัติ
                        </button>
                    </form>
                    <div id="booking-result" class="mt-4 hidden p-4 rounded-xl text-center font-bold"></div>
                </div>
            </div>

            <!-- Gantt -->
            <div id="gantt" class="tab-content hidden">
                <h2 class="text-2xl font-bold mb-6">ปฏิทินสถานะการเข้าพัก (Gantt View)</h2>
                <div class="bg-white p-6 rounded-2xl shadow-sm border overflow-x-auto">
                    <div id="gantt-container" class="grid grid-cols-7 gap-2"></div>
                </div>
            </div>

            <!-- Accounting -->
            <div id="accounting" class="tab-content hidden">
                <h2 class="text-2xl font-bold mb-6">บัญชีแยกประเภท (General Journal)</h2>
                <div class="bg-white rounded-2xl shadow-sm border overflow-hidden">
                    <table class="w-full text-left">
                        <thead class="bg-slate-900 text-white">
                            <tr>
                                <th class="p-4">วันที่</th>
                                <th class="p-4">รายการบันทึก</th>
                                <th class="p-4">รหัสบัญชี</th>
                                <th class="p-4 text-right">Debit</th>
                                <th class="p-4 text-right">Credit</th>
                            </tr>
                        </thead>
                        <tbody id="accounting-body"></tbody>
                    </table>
                </div>
            </div>
        </main>
    </div>

    <script>
        lucide.createIcons();

        function showTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.add('hidden'));
            document.querySelectorAll('nav button').forEach(b => b.classList.remove('bg-slate-800', 'text-white'));
            
            document.getElementById(tabId).classList.remove('hidden');
            document.querySelector(`[data-tab="${tabId}"]`).classList.add('bg-slate-800', 'text-white');
            refreshData();
        }

        async function refreshData() {
            const [bookRes, accRes, roomRes] = await Promise.all([
                fetch('/api/bookings'),
                fetch('/api/accounting'),
                fetch('/api/rooms')
            ]);
            
            const bookings = await bookRes.json();
            const journal = await accRes.json();
            const rooms = await roomRes.json();

            // Dashboard Stats
            document.getElementById('stat-bookings').textContent = bookings.length;
            
            let cash = 0, revenue = 0;
            journal.forEach(e => {
                if(e.account_code === '1020') cash += (e.debit - e.credit);
                if(e.account_code === '4010') revenue += (e.credit - e.debit);
            });
            document.getElementById('stat-cash').textContent = cash.toLocaleString() + '฿';
            document.getElementById('stat-revenue').textContent = revenue.toLocaleString() + '฿';

            // Room Select Option
            const roomSelect = document.getElementById('room_select');
            roomSelect.innerHTML = rooms.map(r => `<option value="${r.เลขห้อง}">ห้อง ${r.เลขห้อง} (${r.ประเภท})</option>`).join('');

            // Room Status Grid
            document.getElementById('room-status-grid').innerHTML = rooms.map(r => `
                <div class="p-2 border rounded-lg text-center ${r.สถานะ === 'ว่าง' ? 'bg-green-50' : 'bg-red-50'}">
                    <div class="text-xs font-bold">${r.เลขห้อง}</div>
                    <div class="w-2 h-2 mx-auto rounded-full ${r.สถานะ === 'ว่าง' ? 'bg-green-500' : 'bg-red-500'}"></div>
                </div>
            `).join('');

            // Recent Bookings
            document.getElementById('recent-bookings-list').innerHTML = bookings.slice(0, 5).map(b => `
                <div class="flex justify-between items-center p-3 bg-slate-50 rounded-xl border">
                    <div>
                        <div class="font-bold text-sm">${b.customer_id}</div>
                        <div class="text-xs text-slate-500">ห้อง ${b.room_number} | ${b.check_in} - ${b.check_out}</div>
                    </div>
                    <span class="status-badge bg-blue-100 text-blue-700">${b.status}</span>
                </div>
            `).join('');

            // Gantt Chart
            const gantt = document.getElementById('gantt-container');
            gantt.innerHTML = '';
            for(let i=0; i<28; i++) {
                const date = new Date();
                date.setDate(date.getDate() + i);
                const dateStr = date.toISOString().split('T')[0];
                const activeBookings = bookings.filter(b => dateStr >= b.check_in && dateStr < b.check_out);
                
                const div = document.createElement('div');
                div.className = `calendar-day ${activeBookings.length > 0 ? 'has-booking' : ''}`;
                div.innerHTML = `<div class="font-bold border-b mb-1">${date.getDate()} ${date.toLocaleString('th-TH',{month:'short'})}</div>`;
                activeBookings.forEach(b => {
                    div.innerHTML += `<div class="text-[10px] text-red-700 truncate">Rm ${b.room_number}</div>`;
                });
                gantt.appendChild(div);
            }

            // Accounting Table
            document.getElementById('accounting-body').innerHTML = journal.map(e => `
                <tr class="border-b hover:bg-slate-50 transition-colors">
                    <td class="p-4 text-xs font-mono">${new Date(e.transaction_date).toLocaleString('th-TH')}</td>
                    <td class="p-4">
                        <div class="font-bold text-slate-700">${e.description}</div>
                        <div class="text-xs text-slate-500 italic">${e.account_name}</div>
                    </td>
                    <td class="p-4 font-mono text-sm">${e.account_code}</td>
                    <td class="p-4 text-right text-blue-600 font-bold">${e.debit ? e.debit.toLocaleString() : '-'}</td>
                    <td class="p-4 text-right text-red-600 font-bold">${e.credit ? e.credit.toLocaleString() : '-'}</td>
                </tr>
            `).join('');
        }

        // Handle Booking Form
        document.getElementById('new-booking-form').onsubmit = async (e) => {
            e.preventDefault();
            const data = {
                customer_name: document.getElementById('cust_name').value,
                room_number: document.getElementById('room_select').value,
                check_in: document.getElementById('check_in').value,
                check_out: document.getElementById('check_out').value,
                total_price: document.getElementById('total_price').value
            };
            
            const res = await fetch('/api/create_booking', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });
            const result = await res.json();
            
            const resDiv = document.getElementById('booking-result');
            resDiv.classList.remove('hidden', 'bg-green-100', 'text-green-700', 'bg-red-100', 'text-red-700');
            if(result.success) {
                resDiv.textContent = "✅ จองสำเร็จและลงบัญชีเรียบร้อย!";
                resDiv.classList.add('bg-green-100', 'text-green-700');
                e.target.reset();
                refreshData();
            } else {
                resDiv.textContent = "❌ " + result.message;
                resDiv.classList.add('bg-red-100', 'text-red-700');
            }
        };

        // Initialize
        document.addEventListener('DOMContentLoaded', () => showTab('dashboard'));
    </script>
</body>
</html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

if __name__ == '__main__':
    # กำหนด PYTHONPATH ให้หา Module database เจอ
    import sys
    import os
    sys.path.append(os.getcwd())
    
    with socketserver.TCPServer(("", PORT), DatabaseWebInterface) as httpd:
        print(f"🚀 VIPAT ERP v2.1 running at http://localhost:{PORT}")
        httpd.serve_forever()
