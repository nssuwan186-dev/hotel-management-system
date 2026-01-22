#!/usr/bin/env python3
import http.server
import socketserver
import json
import sqlite3
from urllib.parse import urlparse, parse_qs

PORT = 8000
DB_PATH = 'database/data/โรงแรม.db'

class DatabaseWebInterface(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.serve_interface()
        elif self.path == '/api/tables':
            self.serve_tables()
        elif self.path.startswith('/api/data'):
            query = urlparse(self.path).query
            params = parse_qs(query)
            table_name = params.get('table', [None])[0]
            if table_name:
                self.serve_table_data(table_name)
        elif self.path == '/api/bookings':
            self.serve_bookings()
        elif self.path == '/api/accounting':
            self.serve_accounting()
        else:
            self.send_error(404)

    def serve_bookings(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Data_Bookings")
            rows = [dict(row) for row in cursor.fetchall()]
            conn.close()
            self.send_json(rows)
        except Exception as e:
            self.send_error(500, str(e))

    def serve_accounting(self):
        try:
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
        except Exception as e:
            self.send_error(500, str(e))

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
    <title>VIPAT HOTEL - ERP System</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        .tab-content.hidden { display: none; }
        .calendar-day { min-height: 80px; border: 1px solid #e2e8f0; padding: 4px; font-size: 0.75rem; }
        .has-booking { background-color: #fee2e2; border-left: 4px solid #ef4444; }
    </style>
</head>
<body class="bg-slate-50 font-sans text-slate-800">
    <div class="flex h-screen">
        <aside class="w-64 bg-slate-900 text-slate-300 flex flex-col shrink-0">
            <div class="p-6 border-b border-slate-700">
                <h1 class="text-xl font-bold text-white">VIPAT ERP</h1>
                <p class="text-xs text-slate-400 mt-1">Property & Accounting</p>
            </div>
            <nav class="flex-1 p-4 space-y-2">
                <button onclick="showTab('dashboard')" class="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800" data-tab="dashboard">
                    <i data-lucide="layout-dashboard" class="w-5 h-5"></i> Dashboard
                </button>
                <button onclick="showTab('bookings')" class="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800" data-tab="bookings">
                    <i data-lucide="calendar" class="w-5 h-5"></i> Gantt Chart
                </button>
                <button onclick="showTab('accounting')" class="w-full flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-slate-800" data-tab="accounting">
                    <i data-lucide="dollar-sign" class="w-5 h-5"></i> Accounting
                </button>
            </nav>
        </aside>

        <main class="flex-1 overflow-y-auto p-8">
            <div id="dashboard" class="tab-content">
                <h2 class="text-2xl font-bold mb-6">ภาพรวมระบบ (ERP Overview)</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div class="bg-white p-6 rounded-xl shadow-sm border">
                        <p class="text-sm text-slate-500">อัตราการเข้าพัก</p>
                        <h3 id="stat-occupancy" class="text-3xl font-bold">0%</h3>
                    </div>
                    <div class="bg-white p-6 rounded-xl shadow-sm border">
                        <p class="text-sm text-slate-500">จำนวนการจอง (เดือนนี้)</p>
                        <h3 id="stat-bookings" class="text-3xl font-bold">0</h3>
                    </div>
                    <div class="bg-white p-6 rounded-xl shadow-sm border">
                        <p class="text-sm text-slate-500">ยอดเงินสดในระบบ</p>
                        <h3 id="stat-cash" class="text-3xl font-bold text-green-600">0฿</h3>
                    </div>
                </div>
            </div>

            <div id="bookings" class="tab-content hidden">
                <h2 class="text-2xl font-bold mb-6">ตารางการเข้าพัก (Gantt Chart)</h2>
                <div class="bg-white p-6 rounded-xl shadow-sm border overflow-x-auto">
                    <div id="gantt-container" class="grid grid-cols-7 gap-1"></div>
                </div>
            </div>

            <div id="accounting" class="tab-content hidden">
                <h2 class="text-2xl font-bold mb-6">สมุดรายวันทั่วไป (General Journal)</h2>
                <div class="bg-white rounded-xl shadow-sm border overflow-hidden">
                    <table class="w-full text-left">
                        <thead class="bg-slate-50 border-b">
                            <tr>
                                <th class="p-4">วันที่</th>
                                <th class="p-4">รายการ</th>
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
            document.getElementById(tabId).classList.remove('hidden');
        }

        async function loadDashboard() {
            const res = await fetch('/api/bookings');
            const bookings = await res.json();
            document.getElementById('stat-bookings').textContent = bookings.length;
            
            const accRes = await fetch('/api/accounting');
            const journal = await accRes.json();
            let totalCash = 0;
            journal.forEach(e => {
                if(e.account_code === '1020') totalCash += (e.debit - e.credit);
            });
            document.getElementById('stat-cash').textContent = totalCash.toLocaleString() + '฿';

            // Render Gantt (Simplified for 30 days)
            const gantt = document.getElementById('gantt-container');
            gantt.innerHTML = '';
            for(let i=0; i<30; i++) {
                const date = new Date();
                date.setDate(date.getDate() + i);
                const dateStr = date.toISOString().split('T')[0];
                const hasBooking = bookings.some(b => dateStr >= b.check_in && dateStr < b.check_out);
                
                const div = document.createElement('div');
                div.className = `calendar-day ${hasBooking ? 'has-booking' : ''}`;
                div.innerHTML = `<div>${date.getDate()} ${date.toLocaleString('th-TH', {month:'short'})}</div>`;
                if(hasBooking) div.innerHTML += `<div class="text-red-600 font-bold mt-2">จองแล้ว</div>`;
                gantt.appendChild(div);
            }

            // Render Accounting
            const accBody = document.getElementById('accounting-body');
            accBody.innerHTML = journal.map(e => `
                <tr class="border-b hover:bg-slate-50">
                    <td class="p-4 text-sm">${new Date(e.transaction_date).toLocaleDateString('th-TH')}</td>
                    <td class="p-4">
                        <div class="font-bold">${e.description}</div>
                        <div class="text-xs text-slate-500">${e.account_name}</div>
                    </td>
                    <td class="p-4 text-mono">${e.account_code}</td>
                    <td class="p-4 text-right text-blue-600 font-bold">${e.debit ? e.debit.toLocaleString() : '-'}</td>
                    <td class="p-4 text-right text-red-600 font-bold">${e.credit ? e.credit.toLocaleString() : '-'}</td>
                </tr>
            `).join('');
        }

        loadDashboard();
    </script>
</body>
</html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def serve_tables(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        self.send_json(tables)

    def serve_table_data(self, table_name):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM `{table_name}`")
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        self.send_json(rows)

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), DatabaseWebInterface) as httpd:
        print(f"🚀 ERP Interface running at http://localhost:{PORT}")
        httpd.serve_forever()