#!/usr/bin/env python3
"""
Web Interface สำหรับดูฐานข้อมูล SQLite - Enhanced Version
"""
import sqlite3
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import csv
import io
from datetime import datetime, timedelta

class DatabaseWebInterface(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query = parse_qs(parsed_path.query)
        
        if path == '/':
            self.serve_main_page()
        elif path == '/api/tables':
            self.serve_tables()
        elif path == '/api/data':
            table = query.get('table', [''])[0]
            self.serve_table_data(table)
        elif path == '/api/export':
            table = query.get('table', [''])[0]
            format_type = query.get('format', ['json'])[0]
            self.serve_export_data(table, format_type)
        else:
            self.send_error(404)
    
    def serve_main_page(self):
        """Serve main HTML page with enhanced features"""
        html = '''<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏨 VIPAT HOTEL - Management System</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
    <style>
        .animate-fade-in { animation: fadeIn 0.5s ease-in; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        .calendar-day { 
            width: 32px; height: 32px; 
            display: flex; align-items: center; justify-content: center;
            border-radius: 6px; cursor: pointer; transition: all 0.2s;
        }
        .calendar-day:hover { background-color: #e2e8f0; }
        .calendar-day.today { background-color: #3b82f6; color: white; }
        .calendar-day.has-booking { background-color: #ef4444; color: white; }
        .calendar-day.has-task { background-color: #f59e0b; color: white; }
        .calendar-day.weekend { color: #ef4444; }
    </style>
</head>
<body class="bg-slate-50 font-sans text-slate-800">
    <div class="flex h-screen">
        <!-- Sidebar -->
        <aside class="w-64 bg-slate-900 text-slate-300 flex flex-col shrink-0">
            <div class="p-6 border-b border-slate-700">
                <h1 class="text-xl font-bold text-white tracking-wide">VIPAT HOTEL</h1>
                <p class="text-xs text-slate-400 mt-1">Management System</p>
            </div>
            
            <nav class="flex-1 p-4 space-y-2">
                <button onclick="showTab('dashboard')" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 hover:bg-slate-800 hover:text-white" data-tab="dashboard">
                    <i data-lucide="layout-dashboard" class="w-5 h-5"></i>
                    <span>ภาพรวม</span>
                </button>
                <button onclick="showTab('rooms')" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 hover:bg-slate-800 hover:text-white" data-tab="rooms">
                    <i data-lucide="bed-double" class="w-5 h-5"></i>
                    <span>ห้องพัก/การจอง</span>
                </button>
                <button onclick="showTab('accounting')" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 hover:bg-slate-800 hover:text-white" data-tab="accounting">
                    <i data-lucide="dollar-sign" class="w-5 h-5"></i>
                    <span>บัญชีรายรับ-จ่าย</span>
                </button>
                <button onclick="showTab('staff')" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 hover:bg-slate-800 hover:text-white" data-tab="staff">
                    <i data-lucide="users" class="w-5 h-5"></i>
                    <span>พนักงาน (HR)</span>
                </button>
                <button onclick="showTab('planning')" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 hover:bg-slate-800 hover:text-white" data-tab="planning">
                    <i data-lucide="calendar" class="w-5 h-5"></i>
                    <span>วางแผนงาน</span>
                </button>
                <button onclick="showTab('import')" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 hover:bg-slate-800 hover:text-white" data-tab="import">
                    <i data-lucide="upload" class="w-5 h-5"></i>
                    <span>นำเข้าข้อมูล</span>
                </button>
                <button onclick="showTab('export')" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 hover:bg-slate-800 hover:text-white" data-tab="export">
                    <i data-lucide="download" class="w-5 h-5"></i>
                    <span>ส่งออกรายงาน</span>
                </button>
            </nav>

            <div class="p-4 border-t border-slate-700">
                <button class="w-full flex items-center gap-3 px-4 py-2 text-red-400 hover:text-red-300 transition-colors">
                    <i data-lucide="log-out" class="w-4 h-4"></i>
                    <span>ออกจากระบบ</span>
                </button>
            </div>
        </aside>

        <!-- Main Content -->
        <main class="flex-1 overflow-y-auto">
            <header class="bg-white shadow-sm px-8 py-4 flex justify-between items-center sticky top-0 z-10">
                <h2 id="page-title" class="font-semibold text-slate-700">Dashboard Overview</h2>
                <div class="flex items-center gap-4">
                    <div class="text-right hidden md:block">
                        <p class="text-sm font-bold text-slate-700">Admin User</p>
                        <p class="text-xs text-slate-500">ผู้จัดการทั่วไป</p>
                    </div>
                    <div class="w-10 h-10 bg-slate-200 rounded-full flex items-center justify-center">
                        <i data-lucide="users" class="w-5 h-5 text-slate-600"></i>
                    </div>
                </div>
            </header>

            <div class="p-8 pb-24">'''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_tables(self):
        """Serve list of tables"""
        try:
            conn = sqlite3.connect('/root/projects/hotel-management/data/โรงแรม.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(tables, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))
    
    def serve_table_data(self, table_name):
        """Serve data from specific table"""
        try:
            conn = sqlite3.connect('/root/projects/hotel-management/data/โรงแรม.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM `{table_name}`")
            rows = cursor.fetchall()
            data = [dict(row) for row in rows]
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False, default=str).encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))
    
    def serve_export_data(self, table_name, format_type):
        """Export data in various formats"""
        try:
            conn = sqlite3.connect('/root/projects/hotel-management/data/โรงแรม.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM `{table_name}`")
            rows = cursor.fetchall()
            data = [dict(row) for row in rows]
            conn.close()
            
            if format_type == 'csv':
                output = io.StringIO()
                if data:
                    writer = csv.DictWriter(output, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
                
                self.send_response(200)
                self.send_header('Content-type', 'text/csv; charset=utf-8')
                self.send_header('Content-Disposition', f'attachment; filename="{table_name}.csv"')
                self.end_headers()
                self.wfile.write(output.getvalue().encode('utf-8'))
            else:
                self.send_response(200)
                self.send_header('Content-type', 'application/json; charset=utf-8')
                self.send_header('Content-Disposition', f'attachment; filename="{table_name}.json"')
                self.end_headers()
                self.wfile.write(json.dumps(data, ensure_ascii=False, default=str, indent=2).encode('utf-8'))
                
        except Exception as e:
            self.send_error(500, str(e))

def start_web_interface():
    """Start the web interface server"""
    server = HTTPServer(('0.0.0.0', 8081), DatabaseWebInterface)
    print("🌐 Enhanced Web Interface เริ่มทำงานที่ http://localhost:8081")
    server.serve_forever()

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_web_interface)
    server_thread.daemon = True
    server_thread.start()
    
    print("🚀 กด Ctrl+C เพื่อหยุดเซิร์ฟเวอร์")
    try:
        server_thread.join()
    except KeyboardInterrupt:
        print("\n👋 หยุดเซิร์ฟเวอร์แล้ว")
