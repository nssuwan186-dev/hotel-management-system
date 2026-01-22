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

            <div class="p-8 pb-24">
                <!-- Dashboard Tab with Calendar -->
                <div id="dashboard" class="tab-content">
                    <div class="space-y-6 animate-fade-in">
                        <!-- Calendar Widget at Top -->
                        <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                            <div class="flex justify-between items-center mb-4">
                                <h3 class="font-bold text-lg text-slate-700">ปฏิทิน 30 วัน</h3>
                                <div class="flex gap-2 text-xs">
                                    <span class="flex items-center gap-1"><div class="w-3 h-3 bg-blue-500 rounded"></div>วันนี้</span>
                                    <span class="flex items-center gap-1"><div class="w-3 h-3 bg-red-500 rounded"></div>มีการจอง</span>
                                    <span class="flex items-center gap-1"><div class="w-3 h-3 bg-amber-500 rounded"></div>มีงาน</span>
                                </div>
                            </div>
                            <div id="calendar-widget" class="grid grid-cols-7 gap-1">
                                <!-- Calendar will be generated here -->
                            </div>
                        </div>

                        <h2 class="text-2xl font-bold text-slate-800">ภาพรวมกิจการ (Dashboard)</h2>
                        
                        <!-- Enhanced Statistics Grid -->
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex items-start justify-between">
                                <div>
                                    <p class="text-slate-500 text-sm font-medium mb-1">อัตราการเข้าพัก</p>
                                    <h3 id="occupancy-rate" class="text-2xl font-bold text-slate-800">-</h3>
                                    <p id="occupancy-detail" class="text-xs mt-2 text-blue-600">-</p>
                                </div>
                                <div class="p-3 rounded-lg bg-blue-100">
                                    <i data-lucide="bed-double" class="w-6 h-6 text-blue-600"></i>
                                </div>
                            </div>
                            
                            <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex items-start justify-between">
                                <div>
                                    <p class="text-slate-500 text-sm font-medium mb-1">จำนวนห้องทั้งหมด</p>
                                    <h3 id="total-rooms" class="text-2xl font-bold text-slate-800">-</h3>
                                    <p class="text-xs mt-2 text-green-600">ห้องพักในระบบ</p>
                                </div>
                                <div class="p-3 rounded-lg bg-green-100">
                                    <i data-lucide="home" class="w-6 h-6 text-green-600"></i>
                                </div>
                            </div>
                            
                            <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex items-start justify-between">
                                <div>
                                    <p class="text-slate-500 text-sm font-medium mb-1">ผู้เข้าพักปัจจุบัน</p>
                                    <h3 id="current-guests" class="text-2xl font-bold text-slate-800">-</h3>
                                    <p class="text-xs mt-2 text-purple-600">คนที่เข้าพักอยู่</p>
                                </div>
                                <div class="p-3 rounded-lg bg-purple-100">
                                    <i data-lucide="users" class="w-6 h-6 text-purple-600"></i>
                                </div>
                            </div>
                            
                            <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex items-start justify-between">
                                <div>
                                    <p class="text-slate-500 text-sm font-medium mb-1">ตารางข้อมูล</p>
                                    <h3 id="total-tables" class="text-2xl font-bold text-slate-800">-</h3>
                                    <p class="text-xs mt-2 text-red-600">ตารางในฐานข้อมูล</p>
                                </div>
                                <div class="p-3 rounded-lg bg-red-100">
                                    <i data-lucide="database" class="w-6 h-6 text-red-600"></i>
                                </div>
                            </div>
                        </div>

                        <!-- Room Status Grid -->
                        <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                            <h3 class="font-bold text-lg mb-4 text-slate-700">สถานะห้องพักวันนี้</h3>
                            <div id="rooms-grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                                <!-- Rooms will be loaded here -->
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Enhanced Tables Tab with Filters -->
                <div id="rooms" class="tab-content hidden">
                    <div class="space-y-6">
                        <div class="flex justify-between items-center">
                            <h2 class="text-2xl font-bold text-slate-800">ตารางข้อมูลทั้งหมด</h2>
                            <div class="flex gap-2">
                                <input type="text" id="table-filter" placeholder="กรองตาราง..." class="px-3 py-2 border rounded-lg text-sm">
                                <button onclick="refreshData()" class="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700 transition-colors">
                                    <i data-lucide="refresh-cw" class="w-4 h-4"></i>
                                    รีเฟรช
                                </button>
                            </div>
                        </div>
                        <div id="tables-list" class="space-y-4">
                            <!-- Tables will be loaded here -->
                        </div>
                    </div>
                </div>

                <!-- Import Tab -->
                <div id="import" class="tab-content hidden">
                    <div class="space-y-6">
                        <h2 class="text-2xl font-bold text-slate-800">นำเข้าข้อมูล</h2>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="bg-white p-6 rounded-xl shadow-sm border">
                                <h3 class="font-bold text-lg mb-4">นำเข้าจากไฟล์ CSV</h3>
                                <input type="file" id="csv-file" accept=".csv" class="mb-4 block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100">
                                <select id="target-table" class="w-full p-2 border rounded-lg mb-4">
                                    <option value="">เลือกตารางปลายทาง</option>
                                </select>
                                <button onclick="importCSV()" class="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700">
                                    <i data-lucide="upload" class="w-4 h-4 inline mr-2"></i>
                                    นำเข้าข้อมูล
                                </button>
                            </div>
                            
                            <div class="bg-white p-6 rounded-xl shadow-sm border">
                                <h3 class="font-bold text-lg mb-4">นำเข้าจาก JSON</h3>
                                <textarea id="json-input" placeholder="วาง JSON ข้อมูลที่นี่..." class="w-full h-32 p-3 border rounded-lg mb-4"></textarea>
                                <select id="json-target-table" class="w-full p-2 border rounded-lg mb-4">
                                    <option value="">เลือกตารางปลายทาง</option>
                                </select>
                                <button onclick="importJSON()" class="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700">
                                    <i data-lucide="database" class="w-4 h-4 inline mr-2"></i>
                                    นำเข้า JSON
                                </button>
                            </div>
                        </div>
                        
                        <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                            <h4 class="font-bold text-yellow-800 mb-2">คำแนะนำ:</h4>
                            <ul class="text-sm text-yellow-700 space-y-1">
                                <li>• ไฟล์ CSV ต้องมี header ที่ตรงกับชื่อคอลัมน์ในตาราง</li>
                                <li>• JSON ต้องเป็น array ของ objects</li>
                                <li>• ข้อมูลที่นำเข้าจะถูกเพิ่มเข้าไปในตาราง ไม่ใช่แทนที่</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <!-- Export Tab -->
                <div id="export" class="tab-content hidden">
                    <div class="space-y-6">
                        <h2 class="text-2xl font-bold text-slate-800">ส่งออกรายงานข้อมูล</h2>
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" id="export-options">
                            <!-- Export options will be loaded here -->
                        </div>
                        
                        <div class="bg-white p-6 rounded-xl shadow-sm border">
                            <h3 class="font-bold text-lg mb-4">รายงานพิเศษ</h3>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <button onclick="exportSpecialReport('occupancy')" class="p-4 border rounded-lg hover:bg-slate-50 text-left">
                                    <h4 class="font-bold text-slate-800">รายงานอัตราการเข้าพัก</h4>
                                    <p class="text-sm text-slate-600">สถิติการเข้าพักรายวัน/เดือน</p>
                                </button>
                                <button onclick="exportSpecialReport('revenue')" class="p-4 border rounded-lg hover:bg-slate-50 text-left">
                                    <h4 class="font-bold text-slate-800">รายงานรายได้</h4>
                                    <p class="text-sm text-slate-600">สรุปรายได้และค่าใช้จ่าย</p>
                                </button>
                                <button onclick="exportSpecialReport('maintenance')" class="p-4 border rounded-lg hover:bg-slate-50 text-left">
                                    <h4 class="font-bold text-slate-800">รายงานการซ่อมบำรุง</h4>
                                    <p class="text-sm text-slate-600">ประวัติการซ่อมแซมห้องพัก</p>
                                </button>
                                <button onclick="exportSpecialReport('guest-history')" class="p-4 border rounded-lg hover:bg-slate-50 text-left">
                                    <h4 class="font-bold text-slate-800">ประวัติผู้เข้าพัก</h4>
                                    <p class="text-sm text-slate-600">รายชื่อและประวัติการเข้าพัก</p>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Other existing tabs -->
                <div id="accounting" class="tab-content hidden">
                    <h2 class="text-2xl font-bold text-slate-800 mb-6">บัญชีรายรับ-รายจ่าย</h2>
                    <div class="bg-white p-6 rounded-xl shadow-sm border">
                        <p class="text-slate-600">ฟีเจอร์นี้กำลังพัฒนา...</p>
                    </div>
                </div>

                <div id="staff" class="tab-content hidden">
                    <h2 class="text-2xl font-bold text-slate-800 mb-6">บุคคลและเงินเดือน</h2>
                    <div class="bg-white p-6 rounded-xl shadow-sm border">
                        <p class="text-slate-600">ฟีเจอร์นี้กำลังพัฒนา...</p>
                    </div>
                </div>

                <div id="planning" class="tab-content hidden">
                    <h2 class="text-2xl font-bold text-slate-800 mb-6">วางแผนและงานประจำเดือน</h2>
                    <div class="bg-white p-6 rounded-xl shadow-sm border">
                        <p class="text-slate-600">ฟีเจอร์นี้กำลังพัฒนา...</p>
                    </div>
                </div>
            </div>
        </main>
    </div>
    <script>
        // Initialize Lucide icons
        lucide.createIcons();
        
        let currentData = {};
        
        // Tab switching
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.add('hidden');
            });
            
            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.classList.remove('bg-blue-600', 'text-white', 'shadow-md');
            });
            
            document.getElementById(tabName).classList.remove('hidden');
            document.querySelector(`[data-tab="${tabName}"]`).classList.add('bg-blue-600', 'text-white', 'shadow-md');
            
            const titles = {
                'dashboard': 'Dashboard Overview',
                'rooms': 'Database Tables',
                'accounting': 'Financial Records',
                'staff': 'Human Resources',
                'planning': 'Planning & Automation',
                'import': 'Data Import',
                'export': 'Export Reports'
            };
            document.getElementById('page-title').textContent = titles[tabName] || 'Dashboard';
        }
        
        // Calendar Widget
        function generateCalendar() {
            const today = new Date();
            const calendar = document.getElementById('calendar-widget');
            
            // Generate 30 days starting from today
            for (let i = 0; i < 30; i++) {
                const date = new Date(today);
                date.setDate(today.getDate() + i);
                
                const dayDiv = document.createElement('div');
                dayDiv.className = 'calendar-day text-xs font-medium';
                dayDiv.textContent = date.getDate();
                
                // Add classes based on conditions
                if (i === 0) dayDiv.classList.add('today');
                if (date.getDay() === 0 || date.getDay() === 6) dayDiv.classList.add('weekend');
                
                // Simulate some bookings and tasks (you can replace with real data)
                if (Math.random() > 0.7) dayDiv.classList.add('has-booking');
                if (Math.random() > 0.8) dayDiv.classList.add('has-task');
                
                dayDiv.title = `${date.toLocaleDateString('th-TH')}`;
                calendar.appendChild(dayDiv);
            }
        }
        
        // Load data functions
        async function loadTables() {
            try {
                const response = await fetch('/api/tables');
                const tables = await response.json();
                currentData.tables = tables;
                
                document.getElementById('total-tables').textContent = tables.length;
                
                // Update tables list with filter
                updateTablesList(tables);
                
                // Update export options
                updateExportOptions(tables);
                
                // Update import target options
                updateImportOptions(tables);
                
            } catch (error) {
                console.error('Error loading tables:', error);
            }
        }
        
        function updateTablesList(tables) {
            const filter = document.getElementById('table-filter')?.value.toLowerCase() || '';
            const filteredTables = tables.filter(table => table.toLowerCase().includes(filter));
            
            const tablesList = document.getElementById('tables-list');
            tablesList.innerHTML = filteredTables.map(table => `
                <div class="bg-white p-4 rounded-lg border shadow-sm">
                    <div class="flex justify-between items-center">
                        <h3 class="font-bold text-slate-800">${table}</h3>
                        <button onclick="loadTableData('${table}')" class="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700">
                            ดูข้อมูล
                        </button>
                    </div>
                    <div id="table-${table}" class="mt-4 hidden"></div>
                </div>
            `).join('');
        }
        
        function updateExportOptions(tables) {
            const exportOptions = document.getElementById('export-options');
            exportOptions.innerHTML = tables.map(table => `
                <div class="bg-white p-4 rounded-lg border shadow-sm">
                    <h3 class="font-bold text-slate-800 mb-3">${table}</h3>
                    <div class="space-y-2">
                        <button onclick="exportTable('${table}', 'json')" class="w-full bg-blue-600 text-white py-2 px-3 rounded text-sm hover:bg-blue-700 flex items-center justify-center gap-2">
                            <i data-lucide="file-json" class="w-4 h-4"></i>
                            JSON
                        </button>
                        <button onclick="exportTable('${table}', 'csv')" class="w-full bg-green-600 text-white py-2 px-3 rounded text-sm hover:bg-green-700 flex items-center justify-center gap-2">
                            <i data-lucide="file-spreadsheet" class="w-4 h-4"></i>
                            CSV
                        </button>
                    </div>
                </div>
            `).join('');
            lucide.createIcons();
        }
        
        function updateImportOptions(tables) {
            const selects = ['target-table', 'json-target-table'];
            selects.forEach(selectId => {
                const select = document.getElementById(selectId);
                if (select) {
                    select.innerHTML = '<option value="">เลือกตารางปลายทาง</option>' +
                        tables.map(table => `<option value="${table}">${table}</option>`).join('');
                }
            });
        }
        
        async function loadTableData(tableName) {
            try {
                const response = await fetch(`/api/data?table=${encodeURIComponent(tableName)}`);
                const data = await response.json();
                
                const container = document.getElementById(`table-${tableName}`);
                
                if (data.length === 0) {
                    container.innerHTML = '<p class="text-slate-500 text-sm">ไม่มีข้อมูล</p>';
                } else {
                    const headers = Object.keys(data[0]);
                    container.innerHTML = `
                        <div class="overflow-x-auto">
                            <table class="w-full text-sm">
                                <thead class="bg-slate-50">
                                    <tr>
                                        ${headers.map(h => `<th class="p-2 text-left border">${h}</th>`).join('')}
                                    </tr>
                                </thead>
                                <tbody>
                                    ${data.map(row => `
                                        <tr class="hover:bg-slate-50">
                                            ${headers.map(h => `<td class="p-2 border">${row[h] || '-'}</td>`).join('')}
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    `;
                }
                
                container.classList.toggle('hidden');
                
                // Update dashboard stats
                if (tableName === 'ผู้เข้าพัก') {
                    const activeGuests = data.filter(g => g.สถานะ === 'เข้าพัก').length;
                    document.getElementById('current-guests').textContent = activeGuests;
                }
                
                if (tableName === 'ห้องพัก') {
                    const totalRooms = data.length;
                    const occupiedRooms = data.filter(r => r.สถานะ === 'มีผู้เข้าพัก').length;
                    const occupancyRate = totalRooms > 0 ? ((occupiedRooms / totalRooms) * 100).toFixed(1) : 0;
                    
                    document.getElementById('total-rooms').textContent = totalRooms;
                    document.getElementById('occupancy-rate').textContent = `${occupancyRate}%`;
                    document.getElementById('occupancy-detail').textContent = `${occupiedRooms} จาก ${totalRooms} ห้อง`;
                    
                    // Update rooms grid
                    const roomsGrid = document.getElementById('rooms-grid');
                    roomsGrid.innerHTML = data.map(room => {
                        const statusClass = room.สถานะ === 'ว่าง' ? 'bg-green-50 border-green-200' : 
                                          room.สถานะ === 'มีผู้เข้าพัก' ? 'bg-red-50 border-red-200' : 'bg-gray-100 border-gray-200';
                        const statusText = room.สถานะ === 'ว่าง' ? 'ว่าง' : 
                                         room.สถานะ === 'มีผู้เข้าพัก' ? 'ไม่ว่าง' : 'ซ่อมแซม';
                        const statusBadgeClass = room.สถานะ === 'ว่าง' ? 'bg-green-100 text-green-700' : 
                                               room.สถานะ === 'มีผู้เข้าพัก' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700';
                        
                        return `
                            <div class="p-4 rounded-lg border flex flex-col items-center justify-center text-center transition-all cursor-pointer hover:scale-105 shadow-sm hover:shadow-md ${statusClass}">
                                <span class="font-bold text-slate-700">${room.เลขห้อง}</span>
                                <span class="text-xs text-slate-500 mb-1">${room.ประเภท}</span>
                                <span class="px-2 py-1 rounded-full text-xs font-medium ${statusBadgeClass}">${statusText}</span>
                            </div>
                        `;
                    }).join('');
                }
                
            } catch (error) {
                console.error('Error loading table data:', error);
            }
        }
        
        // Export functions
        async function exportTable(tableName, format) {
            try {
                const response = await fetch(`/api/export?table=${encodeURIComponent(tableName)}&format=${format}`);
                const blob = await response.blob();
                
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${tableName}.${format}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                alert(`ส่งออก ${tableName} เป็น ${format.toUpperCase()} สำเร็จ!`);
            } catch (error) {
                console.error('Export error:', error);
                alert('เกิดข้อผิดพลาดในการส่งออกข้อมูล');
            }
        }
        
        function exportSpecialReport(reportType) {
            alert(`กำลังพัฒนารายงาน ${reportType}...`);
        }
        
        // Import functions
        function importCSV() {
            const fileInput = document.getElementById('csv-file');
            const targetTable = document.getElementById('target-table').value;
            
            if (!fileInput.files[0] || !targetTable) {
                alert('กรุณาเลือกไฟล์และตารางปลายทาง');
                return;
            }
            
            alert('ฟีเจอร์นำเข้า CSV กำลังพัฒนา...');
        }
        
        function importJSON() {
            const jsonInput = document.getElementById('json-input').value;
            const targetTable = document.getElementById('json-target-table').value;
            
            if (!jsonInput.trim() || !targetTable) {
                alert('กรุณาใส่ข้อมูล JSON และเลือกตารางปลายทาง');
                return;
            }
            
            try {
                JSON.parse(jsonInput);
                alert('ฟีเจอร์นำเข้า JSON กำลังพัฒนา...');
            } catch (e) {
                alert('รูปแบบ JSON ไม่ถูกต้อง');
            }
        }
        
        async function refreshData() {
            await loadTables();
            if (currentData.tables) {
                if (currentData.tables.includes('ผู้เข้าพัก')) {
                    await loadTableData('ผู้เข้าพัก');
                }
                if (currentData.tables.includes('ห้องพัก')) {
                    await loadTableData('ห้องพัก');
                }
            }
        }
        
        // Event listeners
        document.addEventListener('DOMContentLoaded', function() {
            showTab('dashboard');
            generateCalendar();
            refreshData();
            
            // Add filter event listener
            const tableFilter = document.getElementById('table-filter');
            if (tableFilter) {
                tableFilter.addEventListener('input', () => {
                    if (currentData.tables) {
                        updateTablesList(currentData.tables);
                    }
                });
            }
        });
    </script>
</body>
</html>'''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def serve_tables(self):
        """Serve list of tables"""
        try:
            conn = sqlite3.connect('database/data/โรงแรม.db')
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
            conn = sqlite3.connect('database/data/โรงแรม.db')
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
            conn = sqlite3.connect('database/data/โรงแรม.db')
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
                <!-- Dashboard Tab with Calendar -->
                <div id="dashboard" class="tab-content">
                    <div class="space-y-6 animate-fade-in">
                        <!-- Calendar Widget at Top -->
                        <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                            <div class="flex justify-between items-center mb-4">
                                <h3 class="font-bold text-lg text-slate-700">ปฏิทิน 30 วัน</h3>
                                <div class="flex gap-2 text-xs">
                                    <span class="flex items-center gap-1"><div class="w-3 h-3 bg-blue-500 rounded"></div>วันนี้</span>
                                    <span class="flex items-center gap-1"><div class="w-3 h-3 bg-red-500 rounded"></div>มีการจอง</span>
                                    <span class="flex items-center gap-1"><div class="w-3 h-3 bg-amber-500 rounded"></div>มีงาน</span>
                                </div>
                            </div>
                            <div id="calendar-widget" class="grid grid-cols-7 gap-1">
                                <!-- Calendar will be generated here -->
                            </div>
                        </div>

                        <h2 class="text-2xl font-bold text-slate-800">ภาพรวมกิจการ (Dashboard)</h2>
                        
                        <!-- Enhanced Statistics Grid -->
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex items-start justify-between">
                                <div>
                                    <p class="text-slate-500 text-sm font-medium mb-1">อัตราการเข้าพัก</p>
                                    <h3 id="occupancy-rate" class="text-2xl font-bold text-slate-800">-</h3>
                                    <p id="occupancy-detail" class="text-xs mt-2 text-blue-600">-</p>
                                </div>
                                <div class="p-3 rounded-lg bg-blue-100">
                                    <i data-lucide="bed-double" class="w-6 h-6 text-blue-600"></i>
                                </div>
                            </div>
                            
                            <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex items-start justify-between">
                                <div>
                                    <p class="text-slate-500 text-sm font-medium mb-1">จำนวนห้องทั้งหมด</p>
                                    <h3 id="total-rooms" class="text-2xl font-bold text-slate-800">-</h3>
                                    <p class="text-xs mt-2 text-green-600">ห้องพักในระบบ</p>
                                </div>
                                <div class="p-3 rounded-lg bg-green-100">
                                    <i data-lucide="home" class="w-6 h-6 text-green-600"></i>
                                </div>
                            </div>
                            
                            <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex items-start justify-between">
                                <div>
                                    <p class="text-slate-500 text-sm font-medium mb-1">ผู้เข้าพักปัจจุบัน</p>
                                    <h3 id="current-guests" class="text-2xl font-bold text-slate-800">-</h3>
                                    <p class="text-xs mt-2 text-purple-600">คนที่เข้าพักอยู่</p>
                                </div>
                                <div class="p-3 rounded-lg bg-purple-100">
                                    <i data-lucide="users" class="w-6 h-6 text-purple-600"></i>
                                </div>
                            </div>
                            
                            <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-100 flex items-start justify-between">
                                <div>
                                    <p class="text-slate-500 text-sm font-medium mb-1">ตารางข้อมูล</p>
                                    <h3 id="total-tables" class="text-2xl font-bold text-slate-800">-</h3>
                                    <p class="text-xs mt-2 text-red-600">ตารางในฐานข้อมูล</p>
                                </div>
                                <div class="p-3 rounded-lg bg-red-100">
                                    <i data-lucide="database" class="w-6 h-6 text-red-600"></i>
                                </div>
                            </div>
                        </div>

                        <!-- Room Status Grid -->
                        <div class="bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                            <h3 class="font-bold text-lg mb-4 text-slate-700">สถานะห้องพักวันนี้</h3>
                            <div id="rooms-grid" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                                <!-- Rooms will be loaded here -->
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Enhanced Tables Tab with Filters -->
                <div id="rooms" class="tab-content hidden">
                    <div class="space-y-6">
                        <div class="flex justify-between items-center">
                            <h2 class="text-2xl font-bold text-slate-800">ตารางข้อมูลทั้งหมด</h2>
                            <div class="flex gap-2">
                                <input type="text" id="table-filter" placeholder="กรองตาราง..." class="px-3 py-2 border rounded-lg text-sm">
                                <button onclick="refreshData()" class="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700 transition-colors">
                                    <i data-lucide="refresh-cw" class="w-4 h-4"></i>
                                    รีเฟรช
                                </button>
                            </div>
                        </div>
                        <div id="tables-list" class="space-y-4">
                            <!-- Tables will be loaded here -->
                        </div>
                    </div>
                </div>

                <!-- Import Tab -->
                <div id="import" class="tab-content hidden">
                    <div class="space-y-6">
                        <h2 class="text-2xl font-bold text-slate-800">นำเข้าข้อมูล</h2>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="bg-white p-6 rounded-xl shadow-sm border">
                                <h3 class="font-bold text-lg mb-4">นำเข้าจากไฟล์ CSV</h3>
                                <input type="file" id="csv-file" accept=".csv" class="mb-4 block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100">
                                <select id="target-table" class="w-full p-2 border rounded-lg mb-4">
                                    <option value="">เลือกตารางปลายทาง</option>
                                </select>
                                <button onclick="importCSV()" class="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700">
                                    <i data-lucide="upload" class="w-4 h-4 inline mr-2"></i>
                                    นำเข้าข้อมูล
                                </button>
                            </div>
                            
                            <div class="bg-white p-6 rounded-xl shadow-sm border">
                                <h3 class="font-bold text-lg mb-4">นำเข้าจาก JSON</h3>
                                <textarea id="json-input" placeholder="วาง JSON ข้อมูลที่นี่..." class="w-full h-32 p-3 border rounded-lg mb-4"></textarea>
                                <select id="json-target-table" class="w-full p-2 border rounded-lg mb-4">
                                    <option value="">เลือกตารางปลายทาง</option>
                                </select>
                                <button onclick="importJSON()" class="w-full bg-indigo-600 text-white py-2 rounded-lg hover:bg-indigo-700">
                                    <i data-lucide="database" class="w-4 h-4 inline mr-2"></i>
                                    นำเข้า JSON
                                </button>
                            </div>
                        </div>
                        
                        <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                            <h4 class="font-bold text-yellow-800 mb-2">คำแนะนำ:</h4>
                            <ul class="text-sm text-yellow-700 space-y-1">
                                <li>• ไฟล์ CSV ต้องมี header ที่ตรงกับชื่อคอลัมน์ในตาราง</li>
                                <li>• JSON ต้องเป็น array ของ objects</li>
                                <li>• ข้อมูลที่นำเข้าจะถูกเพิ่มเข้าไปในตาราง ไม่ใช่แทนที่</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <!-- Export Tab -->
                <div id="export" class="tab-content hidden">
                    <div class="space-y-6">
                        <h2 class="text-2xl font-bold text-slate-800">ส่งออกรายงานข้อมูล</h2>
                        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" id="export-options">
                            <!-- Export options will be loaded here -->
                        </div>
                        
                        <div class="bg-white p-6 rounded-xl shadow-sm border">
                            <h3 class="font-bold text-lg mb-4">รายงานพิเศษ</h3>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <button onclick="exportSpecialReport('occupancy')" class="p-4 border rounded-lg hover:bg-slate-50 text-left">
                                    <h4 class="font-bold text-slate-800">รายงานอัตราการเข้าพัก</h4>
                                    <p class="text-sm text-slate-600">สถิติการเข้าพักรายวัน/เดือน</p>
                                </button>
                                <button onclick="exportSpecialReport('revenue')" class="p-4 border rounded-lg hover:bg-slate-50 text-left">
                                    <h4 class="font-bold text-slate-800">รายงานรายได้</h4>
                                    <p class="text-sm text-slate-600">สรุปรายได้และค่าใช้จ่าย</p>
                                </button>
                                <button onclick="exportSpecialReport('maintenance')" class="p-4 border rounded-lg hover:bg-slate-50 text-left">
                                    <h4 class="font-bold text-slate-800">รายงานการซ่อมบำรุง</h4>
                                    <p class="text-sm text-slate-600">ประวัติการซ่อมแซมห้องพัก</p>
                                </button>
                                <button onclick="exportSpecialReport('guest-history')" class="p-4 border rounded-lg hover:bg-slate-50 text-left">
                                    <h4 class="font-bold text-slate-800">ประวัติผู้เข้าพัก</h4>
                                    <p class="text-sm text-slate-600">รายชื่อและประวัติการเข้าพัก</p>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Other existing tabs -->
                <div id="accounting" class="tab-content hidden">
                    <h2 class="text-2xl font-bold text-slate-800 mb-6">บัญชีรายรับ-รายจ่าย</h2>
                    <div class="bg-white p-6 rounded-xl shadow-sm border">
                        <p class="text-slate-600">ฟีเจอร์นี้กำลังพัฒนา...</p>
                    </div>
                </div>

                <div id="staff" class="tab-content hidden">
                    <h2 class="text-2xl font-bold text-slate-800 mb-6">บุคคลและเงินเดือน</h2>
                    <div class="bg-white p-6 rounded-xl shadow-sm border">
                        <p class="text-slate-600">ฟีเจอร์นี้กำลังพัฒนา...</p>
                    </div>
                </div>

                <div id="planning" class="tab-content hidden">
                    <h2 class="text-2xl font-bold text-slate-800 mb-6">วางแผนและงานประจำเดือน</h2>
                    <div class="bg-white p-6 rounded-xl shadow-sm border">
                        <p class="text-slate-600">ฟีเจอร์นี้กำลังพัฒนา...</p>
                    </div>
                </div>
            </div>
        </main>
    </div>
    <script>
        // Initialize Lucide icons
        lucide.createIcons();
        
        let currentData = {};
        
        // Tab switching
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.add('hidden');
            });
            
            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.classList.remove('bg-blue-600', 'text-white', 'shadow-md');
            });
            
            document.getElementById(tabName).classList.remove('hidden');
            document.querySelector(`[data-tab="${tabName}"]`).classList.add('bg-blue-600', 'text-white', 'shadow-md');
            
            const titles = {
                'dashboard': 'Dashboard Overview',
                'rooms': 'Database Tables',
                'accounting': 'Financial Records',
                'staff': 'Human Resources',
                'planning': 'Planning & Automation',
                'import': 'Data Import',
                'export': 'Export Reports'
            };
            document.getElementById('page-title').textContent = titles[tabName] || 'Dashboard';
        }
        
        // Calendar Widget
        function generateCalendar() {
            const today = new Date();
            const calendar = document.getElementById('calendar-widget');
            
            // Generate 30 days starting from today
            for (let i = 0; i < 30; i++) {
                const date = new Date(today);
                date.setDate(today.getDate() + i);
                
                const dayDiv = document.createElement('div');
                dayDiv.className = 'calendar-day text-xs font-medium';
                dayDiv.textContent = date.getDate();
                
                // Add classes based on conditions
                if (i === 0) dayDiv.classList.add('today');
                if (date.getDay() === 0 || date.getDay() === 6) dayDiv.classList.add('weekend');
                
                // Simulate some bookings and tasks (you can replace with real data)
                if (Math.random() > 0.7) dayDiv.classList.add('has-booking');
                if (Math.random() > 0.8) dayDiv.classList.add('has-task');
                
                dayDiv.title = `${date.toLocaleDateString('th-TH')}`;
                calendar.appendChild(dayDiv);
            }
        }
        
        // Load data functions
        async function loadTables() {
            try {
                const response = await fetch('/api/tables');
                const tables = await response.json();
                currentData.tables = tables;
                
                document.getElementById('total-tables').textContent = tables.length;
                
                // Update tables list with filter
                updateTablesList(tables);
                
                // Update export options
                updateExportOptions(tables);
                
                // Update import target options
                updateImportOptions(tables);
                
            } catch (error) {
                console.error('Error loading tables:', error);
            }
        }
        
        function updateTablesList(tables) {
            const filter = document.getElementById('table-filter')?.value.toLowerCase() || '';
            const filteredTables = tables.filter(table => table.toLowerCase().includes(filter));
            
            const tablesList = document.getElementById('tables-list');
            tablesList.innerHTML = filteredTables.map(table => `
                <div class="bg-white p-4 rounded-lg border shadow-sm">
                    <div class="flex justify-between items-center">
                        <h3 class="font-bold text-slate-800">${table}</h3>
                        <button onclick="loadTableData('${table}')" class="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700">
                            ดูข้อมูล
                        </button>
                    </div>
                    <div id="table-${table}" class="mt-4 hidden"></div>
                </div>
            `).join('');
        }
        
        function updateExportOptions(tables) {
            const exportOptions = document.getElementById('export-options');
            exportOptions.innerHTML = tables.map(table => `
                <div class="bg-white p-4 rounded-lg border shadow-sm">
                    <h3 class="font-bold text-slate-800 mb-3">${table}</h3>
                    <div class="space-y-2">
                        <button onclick="exportTable('${table}', 'json')" class="w-full bg-blue-600 text-white py-2 px-3 rounded text-sm hover:bg-blue-700 flex items-center justify-center gap-2">
                            <i data-lucide="file-json" class="w-4 h-4"></i>
                            JSON
                        </button>
                        <button onclick="exportTable('${table}', 'csv')" class="w-full bg-green-600 text-white py-2 px-3 rounded text-sm hover:bg-green-700 flex items-center justify-center gap-2">
                            <i data-lucide="file-spreadsheet" class="w-4 h-4"></i>
                            CSV
                        </button>
                    </div>
                </div>
            `).join('');
            lucide.createIcons();
        }
        
        function updateImportOptions(tables) {
            const selects = ['target-table', 'json-target-table'];
            selects.forEach(selectId => {
                const select = document.getElementById(selectId);
                if (select) {
                    select.innerHTML = '<option value="">เลือกตารางปลายทาง</option>' +
                        tables.map(table => `<option value="${table}">${table}</option>`).join('');
                }
            });
        }
        
        async function loadTableData(tableName) {
            try {
                const response = await fetch(`/api/data?table=${encodeURIComponent(tableName)}`);
                const data = await response.json();
                
                const container = document.getElementById(`table-${tableName}`);
                
                if (data.length === 0) {
                    container.innerHTML = '<p class="text-slate-500 text-sm">ไม่มีข้อมูล</p>';
                } else {
                    const headers = Object.keys(data[0]);
                    container.innerHTML = `
                        <div class="overflow-x-auto">
                            <table class="w-full text-sm">
                                <thead class="bg-slate-50">
                                    <tr>
                                        ${headers.map(h => `<th class="p-2 text-left border">${h}</th>`).join('')}
                                    </tr>
                                </thead>
                                <tbody>
                                    ${data.map(row => `
                                        <tr class="hover:bg-slate-50">
                                            ${headers.map(h => `<td class="p-2 border">${row[h] || '-'}</td>`).join('')}
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    `;
                }
                
                container.classList.toggle('hidden');
                
                // Update dashboard stats
                if (tableName === 'ผู้เข้าพัก') {
                    const activeGuests = data.filter(g => g.สถานะ === 'เข้าพัก').length;
                    document.getElementById('current-guests').textContent = activeGuests;
                }
                
                if (tableName === 'ห้องพัก') {
                    const totalRooms = data.length;
                    const occupiedRooms = data.filter(r => r.สถานะ === 'มีผู้เข้าพัก').length;
                    const occupancyRate = totalRooms > 0 ? ((occupiedRooms / totalRooms) * 100).toFixed(1) : 0;
                    
                    document.getElementById('total-rooms').textContent = totalRooms;
                    document.getElementById('occupancy-rate').textContent = `${occupancyRate}%`;
                    document.getElementById('occupancy-detail').textContent = `${occupiedRooms} จาก ${totalRooms} ห้อง`;
                    
                    // Update rooms grid
                    const roomsGrid = document.getElementById('rooms-grid');
                    roomsGrid.innerHTML = data.map(room => {
                        const statusClass = room.สถานะ === 'ว่าง' ? 'bg-green-50 border-green-200' : 
                                          room.สถานะ === 'มีผู้เข้าพัก' ? 'bg-red-50 border-red-200' : 'bg-gray-100 border-gray-200';
                        const statusText = room.สถานะ === 'ว่าง' ? 'ว่าง' : 
                                         room.สถานะ === 'มีผู้เข้าพัก' ? 'ไม่ว่าง' : 'ซ่อมแซม';
                        const statusBadgeClass = room.สถานะ === 'ว่าง' ? 'bg-green-100 text-green-700' : 
                                               room.สถานะ === 'มีผู้เข้าพัก' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700';
                        
                        return `
                            <div class="p-4 rounded-lg border flex flex-col items-center justify-center text-center transition-all cursor-pointer hover:scale-105 shadow-sm hover:shadow-md ${statusClass}">
                                <span class="font-bold text-slate-700">${room.เลขห้อง}</span>
                                <span class="text-xs text-slate-500 mb-1">${room.ประเภท}</span>
                                <span class="px-2 py-1 rounded-full text-xs font-medium ${statusBadgeClass}">${statusText}</span>
                            </div>
                        `;
                    }).join('');
                }
                
            } catch (error) {
                console.error('Error loading table data:', error);
            }
        }
        
        // Export functions
        async function exportTable(tableName, format) {
            try {
                const response = await fetch(`/api/export?table=${encodeURIComponent(tableName)}&format=${format}`);
                const blob = await response.blob();
                
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${tableName}.${format}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                alert(`ส่งออก ${tableName} เป็น ${format.toUpperCase()} สำเร็จ!`);
            } catch (error) {
                console.error('Export error:', error);
                alert('เกิดข้อผิดพลาดในการส่งออกข้อมูล');
            }
        }
        
        function exportSpecialReport(reportType) {
            alert(`กำลังพัฒนารายงาน ${reportType}...`);
        }
        
        // Import functions
        function importCSV() {
            const fileInput = document.getElementById('csv-file');
            const targetTable = document.getElementById('target-table').value;
            
            if (!fileInput.files[0] || !targetTable) {
                alert('กรุณาเลือกไฟล์และตารางปลายทาง');
                return;
            }
            
            alert('ฟีเจอร์นำเข้า CSV กำลังพัฒนา...');
        }
        
        function importJSON() {
            const jsonInput = document.getElementById('json-input').value;
            const targetTable = document.getElementById('json-target-table').value;
            
            if (!jsonInput.trim() || !targetTable) {
                alert('กรุณาใส่ข้อมูล JSON และเลือกตารางปลายทาง');
                return;
            }
            
            try {
                JSON.parse(jsonInput);
                alert('ฟีเจอร์นำเข้า JSON กำลังพัฒนา...');
            } catch (e) {
                alert('รูปแบบ JSON ไม่ถูกต้อง');
            }
        }
        
        async function refreshData() {
            await loadTables();
            if (currentData.tables) {
                if (currentData.tables.includes('ผู้เข้าพัก')) {
                    await loadTableData('ผู้เข้าพัก');
                }
                if (currentData.tables.includes('ห้องพัก')) {
                    await loadTableData('ห้องพัก');
                }
            }
        }
        
        // Event listeners
        document.addEventListener('DOMContentLoaded', function() {
            showTab('dashboard');
            generateCalendar();
            refreshData();
            
            // Add filter event listener
            const tableFilter = document.getElementById('table-filter');
            if (tableFilter) {
                tableFilter.addEventListener('input', () => {
                    if (currentData.tables) {
                        updateTablesList(currentData.tables);
                    }
                });
            }
        });
    </script>
</body>
</html>'''
