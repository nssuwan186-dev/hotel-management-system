#!/usr/bin/env python3
import sqlite3
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

class DatabaseWebInterface(BaseHTTPRequestHandler):
    def do_GET(self):
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
        html = '''<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏨 VIPAT HOTEL - Management System</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest/dist/umd/lucide.js"></script>
    <style>
        .sidebar { transition: transform 0.3s ease-in-out; }
        .sidebar.collapsed { transform: translateX(-100%); }
        .calendar-day { 
            width: 28px; height: 28px; display: flex; align-items: center; justify-content: center;
            border-radius: 6px; cursor: pointer; transition: all 0.2s; font-size: 12px;
        }
        .calendar-day:hover { background-color: #e2e8f0; }
        .calendar-day.today { background-color: #3b82f6; color: white; }
        .calendar-day.has-booking { background-color: #ef4444; color: white; }
        .calendar-day.has-task { background-color: #f59e0b; color: white; }
        
        @media (max-width: 768px) {
            .sidebar { position: fixed; z-index: 50; height: 100vh; }
            .main-content { margin-left: 0 !important; }
        }
    </style>
</head>
<body class="bg-slate-50 font-sans text-slate-800">
    <!-- Mobile Menu Button -->
    <button id="mobile-menu-btn" onclick="toggleSidebar()" class="md:hidden fixed top-4 left-4 z-50 bg-slate-900 text-white p-2 rounded-lg">
        <i data-lucide="menu" class="w-5 h-5"></i>
    </button>
    
    <!-- Sidebar Overlay -->
    <div id="sidebar-overlay" onclick="toggleSidebar()" class="fixed inset-0 bg-black bg-opacity-50 z-40 hidden md:hidden"></div>
    
    <div class="flex h-screen">
        <!-- Sidebar -->
        <aside id="sidebar" class="sidebar w-64 bg-slate-900 text-slate-300 flex flex-col shrink-0">
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
                <button onclick="showTab('import')" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 hover:bg-slate-800 hover:text-white" data-tab="import">
                    <i data-lucide="upload" class="w-5 h-5"></i>
                    <span>นำเข้าข้อมูล</span>
                </button>
                <button onclick="showTab('export')" class="nav-btn w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 hover:bg-slate-800 hover:text-white" data-tab="export">
                    <i data-lucide="download" class="w-5 h-5"></i>
                    <span>ส่งออกรายงาน</span>
                </button>
            </nav>
        </aside>

        <!-- Main Content -->
        <main id="main-content" class="flex-1 overflow-y-auto ml-0 md:ml-64">
            <header class="bg-white shadow-sm px-4 md:px-8 py-4 flex justify-between items-center sticky top-0 z-10">
                <h2 id="page-title" class="font-semibold text-slate-700 ml-12 md:ml-0">Dashboard Overview</h2>
                <div class="flex items-center gap-4">
                    <div class="text-right hidden md:block">
                        <p class="text-sm font-bold text-slate-700">Admin User</p>
                        <p class="text-xs text-slate-500">ผู้จัดการทั่วไป</p>
                    </div>
                    <div class="w-8 h-8 md:w-10 md:h-10 bg-slate-200 rounded-full flex items-center justify-center">
                        <i data-lucide="users" class="w-4 h-4 md:w-5 md:h-5 text-slate-600"></i>
                    </div>
                </div>
            </header>

            <div class="p-4 md:p-8 pb-24">
                <!-- Dashboard Tab -->
                <div id="dashboard" class="tab-content">
                    <div class="space-y-4 md:space-y-6">
                        <!-- Calendar Widget -->
                        <div class="bg-white p-4 md:p-6 rounded-xl shadow-sm border border-slate-100">
                            <div class="flex justify-between items-center mb-4">
                                <h3 class="font-bold text-base md:text-lg text-slate-700">ปฏิทิน 30 วัน</h3>
                                <div class="flex gap-2 text-xs">
                                    <span class="flex items-center gap-1"><div class="w-3 h-3 bg-blue-500 rounded"></div>วันนี้</span>
                                    <span class="flex items-center gap-1"><div class="w-3 h-3 bg-red-500 rounded"></div>จอง</span>
                                </div>
                            </div>
                            <div id="calendar-widget" class="grid grid-cols-7 gap-1">
                                <!-- Calendar will be generated here -->
                            </div>
                        </div>

                        <h2 class="text-xl md:text-2xl font-bold text-slate-800">ภาพรวมกิจการ</h2>
                        
                        <!-- Statistics Grid -->
                        <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
                            <div class="bg-white p-4 md:p-6 rounded-xl shadow-sm border border-slate-100 flex items-start justify-between">
                                <div>
                                    <p class="text-slate-500 text-xs md:text-sm font-medium mb-1">อัตราการเข้าพัก</p>
                                    <h3 id="occupancy-rate" class="text-lg md:text-2xl font-bold text-slate-800">-</h3>
                                    <p id="occupancy-detail" class="text-xs mt-2 text-blue-600">-</p>
                                </div>
                                <div class="p-2 md:p-3 rounded-lg bg-blue-100">
                                    <i data-lucide="bed-double" class="w-4 h-4 md:w-6 md:h-6 text-blue-600"></i>
                                </div>
                            </div>
                            
                            <div class="bg-white p-4 md:p-6 rounded-xl shadow-sm border border-slate-100 flex items-start justify-between">
                                <div>
                                    <p class="text-slate-500 text-xs md:text-sm font-medium mb-1">จำนวนห้อง</p>
                                    <h3 id="total-rooms" class="text-lg md:text-2xl font-bold text-slate-800">-</h3>
                                    <p class="text-xs mt-2 text-green-600">ห้องทั้งหมด</p>
                                </div>
                                <div class="p-2 md:p-3 rounded-lg bg-green-100">
                                    <i data-lucide="home" class="w-4 h-4 md:w-6 md:h-6 text-green-600"></i>
                                </div>
                            </div>
                            
                            <div class="bg-white p-4 md:p-6 rounded-xl shadow-sm border border-slate-100 flex items-start justify-between">
                                <div>
                                    <p class="text-slate-500 text-xs md:text-sm font-medium mb-1">ผู้เข้าพัก</p>
                                    <h3 id="current-guests" class="text-lg md:text-2xl font-bold text-slate-800">-</h3>
                                    <p class="text-xs mt-2 text-purple-600">ปัจจุบัน</p>
                                </div>
                                <div class="p-2 md:p-3 rounded-lg bg-purple-100">
                                    <i data-lucide="users" class="w-4 h-4 md:w-6 md:h-6 text-purple-600"></i>
                                </div>
                            </div>
                            
                            <div class="bg-white p-4 md:p-6 rounded-xl shadow-sm border border-slate-100 flex items-start justify-between">
                                <div>
                                    <p class="text-slate-500 text-xs md:text-sm font-medium mb-1">ตารางข้อมูล</p>
                                    <h3 id="total-tables" class="text-lg md:text-2xl font-bold text-slate-800">-</h3>
                                    <p class="text-xs mt-2 text-red-600">ในระบบ</p>
                                </div>
                                <div class="p-2 md:p-3 rounded-lg bg-red-100">
                                    <i data-lucide="database" class="w-4 h-4 md:w-6 md:h-6 text-red-600"></i>
                                </div>
                            </div>
                        </div>

                        <!-- Room Status Grid -->
                        <div class="bg-white p-4 md:p-6 rounded-xl shadow-sm border border-slate-100">
                            <h3 class="font-bold text-base md:text-lg mb-4 text-slate-700">สถานะห้องพัก</h3>
                            <div id="rooms-grid" class="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2 md:gap-3">
                                <!-- Rooms will be loaded here -->
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Other tabs -->
                <div id="rooms" class="tab-content hidden">
                    <h2 class="text-xl md:text-2xl font-bold text-slate-800 mb-4 md:mb-6">ตารางข้อมูล</h2>
                    <div id="tables-list" class="space-y-4">
                        <!-- Tables will be loaded here -->
                    </div>
                </div>

                <div id="import" class="tab-content hidden">
                    <h2 class="text-xl md:text-2xl font-bold text-slate-800 mb-4 md:mb-6">นำเข้าข้อมูล</h2>
                    <div class="bg-white p-4 md:p-6 rounded-xl shadow-sm border">
                        <p class="text-slate-600">ฟีเจอร์นำเข้าข้อมูลกำลังพัฒนา...</p>
                    </div>
                </div>

                <div id="export" class="tab-content hidden">
                    <h2 class="text-xl md:text-2xl font-bold text-slate-800 mb-4 md:mb-6">ส่งออกรายงานข้อมูล</h2>
                    
                    <!-- Export Filters -->
                    <div class="bg-white p-4 md:p-6 rounded-xl shadow-sm border mb-6">
                        <h3 class="font-bold text-lg mb-4">ตัวกรองข้อมูล</h3>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label class="block text-sm font-medium text-slate-700 mb-2">เลือกตาราง</label>
                                <select id="export-table-select" class="w-full p-2 border rounded-lg">
                                    <option value="">เลือกตาราง...</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-slate-700 mb-2">วันที่เริ่มต้น</label>
                                <input type="date" id="export-date-start" class="w-full p-2 border rounded-lg">
                            </div>
                            <div>
                                <label class="block text-sm font-medium text-slate-700 mb-2">วันที่สิ้นสุด</label>
                                <input type="date" id="export-date-end" class="w-full p-2 border rounded-lg">
                            </div>
                        </div>
                        
                        <!-- Dynamic Filters -->
                        <div id="dynamic-filters" class="mt-4 hidden">
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div id="status-filter" class="hidden">
                                    <label class="block text-sm font-medium text-slate-700 mb-2">สถานะ</label>
                                    <select id="export-status" class="w-full p-2 border rounded-lg">
                                        <option value="">ทั้งหมด</option>
                                    </select>
                                </div>
                                <div id="building-filter" class="hidden">
                                    <label class="block text-sm font-medium text-slate-700 mb-2">ตึก</label>
                                    <select id="export-building" class="w-full p-2 border rounded-lg">
                                        <option value="">ทั้งหมด</option>
                                    </select>
                                </div>
                                <div id="room-type-filter" class="hidden">
                                    <label class="block text-sm font-medium text-slate-700 mb-2">ประเภทห้อง</label>
                                    <select id="export-room-type" class="w-full p-2 border rounded-lg">
                                        <option value="">ทั้งหมด</option>
                                    </select>
                                </div>
                                <div id="price-filter" class="hidden">
                                    <label class="block text-sm font-medium text-slate-700 mb-2">ช่วงราคา</label>
                                    <div class="flex gap-2">
                                        <input type="number" id="export-price-min" placeholder="ต่ำสุด" class="w-full p-2 border rounded-lg">
                                        <input type="number" id="export-price-max" placeholder="สูงสุด" class="w-full p-2 border rounded-lg">
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-4 flex gap-2">
                            <button onclick="previewFilteredData()" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                                <i data-lucide="eye" class="w-4 h-4 inline mr-2"></i>
                                ดูตัวอย่าง
                            </button>
                            <button onclick="exportFilteredData('json')" class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700">
                                <i data-lucide="download" class="w-4 h-4 inline mr-2"></i>
                                ส่งออก JSON
                            </button>
                            <button onclick="exportFilteredData('csv')" class="bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700">
                                <i data-lucide="file-spreadsheet" class="w-4 h-4 inline mr-2"></i>
                                ส่งออก CSV
                            </button>
                        </div>
                    </div>
                    
                    <!-- Preview Area -->
                    <div id="export-preview" class="bg-white p-4 md:p-6 rounded-xl shadow-sm border hidden">
                        <h3 class="font-bold text-lg mb-4">ตัวอย่างข้อมูลที่จะส่งออก</h3>
                        <div id="preview-content" class="overflow-x-auto">
                            <!-- Preview will be shown here -->
                        </div>
                        <div class="mt-4 text-sm text-slate-600">
                            <span id="preview-count">0</span> รายการ
                        </div>
                    </div>
                    
                    <!-- Quick Export Options -->
                    <div class="mt-6">
                        <h3 class="font-bold text-lg mb-4">ส่งออกด่วน</h3>
                        <div id="export-options" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            <!-- Export options will be loaded here -->
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <script>
        lucide.createIcons();
        let currentData = {};
        let sidebarCollapsed = false;
        
        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.getElementById('sidebar-overlay');
            
            sidebarCollapsed = !sidebarCollapsed;
            
            if (sidebarCollapsed) {
                sidebar.classList.add('collapsed');
                overlay.classList.add('hidden');
            } else {
                sidebar.classList.remove('collapsed');
                if (window.innerWidth < 768) {
                    overlay.classList.remove('hidden');
                }
            }
        }
        
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
                'import': 'Data Import',
                'export': 'Export Reports'
            };
            document.getElementById('page-title').textContent = titles[tabName] || 'Dashboard';
            
            // Auto collapse sidebar on mobile after selection
            if (window.innerWidth < 768 && !sidebarCollapsed) {
                setTimeout(() => toggleSidebar(), 500);
            }
        }
        
        function generateCalendar() {
            const today = new Date();
            const calendar = document.getElementById('calendar-widget');
            
            for (let i = 0; i < 30; i++) {
                const date = new Date(today);
                date.setDate(today.getDate() + i);
                
                const dayDiv = document.createElement('div');
                dayDiv.className = 'calendar-day text-xs font-medium';
                dayDiv.textContent = date.getDate();
                
                if (i === 0) dayDiv.classList.add('today');
                if (Math.random() > 0.7) dayDiv.classList.add('has-booking');
                if (Math.random() > 0.8) dayDiv.classList.add('has-task');
                
                dayDiv.title = date.toLocaleDateString('th-TH');
                calendar.appendChild(dayDiv);
            }
        }
        
        async function loadTables() {
            try {
                const response = await fetch('/api/tables');
                const tables = await response.json();
                currentData.tables = tables;
                
                document.getElementById('total-tables').textContent = tables.length;
                
                const tablesList = document.getElementById('tables-list');
                tablesList.innerHTML = tables.map(table => `
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
                
                const exportOptions = document.getElementById('export-options');
                exportOptions.innerHTML = tables.map(table => `
                    <div class="bg-white p-4 rounded-lg border shadow-sm">
                        <h3 class="font-bold text-slate-800 mb-3">${table}</h3>
                        <div class="space-y-2">
                            <button onclick="exportTable('${table}', 'json')" class="w-full bg-blue-600 text-white py-2 px-3 rounded text-sm hover:bg-blue-700">
                                JSON
                            </button>
                            <button onclick="exportTable('${table}', 'csv')" class="w-full bg-green-600 text-white py-2 px-3 rounded text-sm hover:bg-green-700">
                                CSV
                            </button>
                        </div>
                    </div>
                `).join('');
                
                // Update export table select
                const exportTableSelect = document.getElementById('export-table-select');
                if (exportTableSelect) {
                    exportTableSelect.innerHTML = '<option value="">เลือกตาราง...</option>' +
                        tables.map(table => `<option value="${table}">${table}</option>`).join('');
                }
                
            } catch (error) {
                console.error('Error loading tables:', error);
            }
        }
        
        // Export filter functions
        async function setupExportFilters() {
            const exportTableSelect = document.getElementById('export-table-select');
            if (exportTableSelect) {
                exportTableSelect.addEventListener('change', async function() {
                    const tableName = this.value;
                    if (tableName) {
                        await loadFilterOptions(tableName);
                        document.getElementById('dynamic-filters').classList.remove('hidden');
                    } else {
                        document.getElementById('dynamic-filters').classList.add('hidden');
                    }
                });
            }
        }
        
        async function loadFilterOptions(tableName) {
            try {
                const response = await fetch(`/api/data?table=${encodeURIComponent(tableName)}`);
                const data = await response.json();
                
                // Hide all filters first
                document.querySelectorAll('#dynamic-filters > div > div').forEach(filter => {
                    filter.classList.add('hidden');
                });
                
                if (data.length === 0) return;
                
                const sampleRow = data[0];
                
                // Show relevant filters based on table structure
                if ('สถานะ' in sampleRow) {
                    const statusFilter = document.getElementById('status-filter');
                    const statusSelect = document.getElementById('export-status');
                    const statuses = [...new Set(data.map(row => row.สถานะ).filter(Boolean))];
                    
                    statusSelect.innerHTML = '<option value="">ทั้งหมด</option>' +
                        statuses.map(status => `<option value="${status}">${status}</option>`).join('');
                    statusFilter.classList.remove('hidden');
                }
                
                if ('ตึก' in sampleRow) {
                    const buildingFilter = document.getElementById('building-filter');
                    const buildingSelect = document.getElementById('export-building');
                    const buildings = [...new Set(data.map(row => row.ตึก).filter(Boolean))];
                    
                    buildingSelect.innerHTML = '<option value="">ทั้งหมด</option>' +
                        buildings.map(building => `<option value="${building}">ตึก ${building}</option>`).join('');
                    buildingFilter.classList.remove('hidden');
                }
                
                if ('ประเภท' in sampleRow) {
                    const roomTypeFilter = document.getElementById('room-type-filter');
                    const roomTypeSelect = document.getElementById('export-room-type');
                    const roomTypes = [...new Set(data.map(row => row.ประเภท).filter(Boolean))];
                    
                    roomTypeSelect.innerHTML = '<option value="">ทั้งหมด</option>' +
                        roomTypes.map(type => `<option value="${type}">${type}</option>`).join('');
                    roomTypeFilter.classList.remove('hidden');
                }
                
                if ('ราคา' in sampleRow) {
                    const priceFilter = document.getElementById('price-filter');
                    const prices = data.map(row => parseInt(row.ราคา)).filter(price => !isNaN(price));
                    const minPrice = Math.min(...prices);
                    const maxPrice = Math.max(...prices);
                    
                    document.getElementById('export-price-min').placeholder = `ต่ำสุด (${minPrice})`;
                    document.getElementById('export-price-max').placeholder = `สูงสุด (${maxPrice})`;
                    priceFilter.classList.remove('hidden');
                }
                
            } catch (error) {
                console.error('Error loading filter options:', error);
            }
        }
        
        async function previewFilteredData() {
            const tableName = document.getElementById('export-table-select').value;
            if (!tableName) {
                alert('กรุณาเลือกตารางก่อน');
                return;
            }
            
            try {
                const response = await fetch(`/api/data?table=${encodeURIComponent(tableName)}`);
                let data = await response.json();
                
                // Apply filters
                data = applyFilters(data);
                
                const previewDiv = document.getElementById('export-preview');
                const previewContent = document.getElementById('preview-content');
                const previewCount = document.getElementById('preview-count');
                
                if (data.length === 0) {
                    previewContent.innerHTML = '<p class="text-slate-500">ไม่มีข้อมูลที่ตรงกับเงื่อนไข</p>';
                } else {
                    const headers = Object.keys(data[0]);
                    const displayData = data.slice(0, 10); // Show first 10 rows
                    
                    previewContent.innerHTML = `
                        <table class="w-full text-sm">
                            <thead class="bg-slate-50">
                                <tr>
                                    ${headers.map(h => `<th class="p-2 text-left border">${h}</th>`).join('')}
                                </tr>
                            </thead>
                            <tbody>
                                ${displayData.map(row => `
                                    <tr class="hover:bg-slate-50">
                                        ${headers.map(h => `<td class="p-2 border">${row[h] || '-'}</td>`).join('')}
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                        ${data.length > 10 ? `<p class="mt-2 text-sm text-slate-600">แสดง 10 รายการแรก จากทั้งหมด ${data.length} รายการ</p>` : ''}
                    `;
                }
                
                previewCount.textContent = data.length;
                previewDiv.classList.remove('hidden');
                
            } catch (error) {
                console.error('Error previewing data:', error);
                alert('เกิดข้อผิดพลาดในการดูตัวอย่างข้อมูล');
            }
        }
        
        function applyFilters(data) {
            let filteredData = [...data];
            
            // Status filter
            const status = document.getElementById('export-status')?.value;
            if (status) {
                filteredData = filteredData.filter(row => row.สถานะ === status);
            }
            
            // Building filter
            const building = document.getElementById('export-building')?.value;
            if (building) {
                filteredData = filteredData.filter(row => row.ตึก === building);
            }
            
            // Room type filter
            const roomType = document.getElementById('export-room-type')?.value;
            if (roomType) {
                filteredData = filteredData.filter(row => row.ประเภท === roomType);
            }
            
            // Price filter
            const priceMin = document.getElementById('export-price-min')?.value;
            const priceMax = document.getElementById('export-price-max')?.value;
            if (priceMin || priceMax) {
                filteredData = filteredData.filter(row => {
                    const price = parseInt(row.ราคา);
                    if (isNaN(price)) return true;
                    if (priceMin && price < parseInt(priceMin)) return false;
                    if (priceMax && price > parseInt(priceMax)) return false;
                    return true;
                });
            }
            
            return filteredData;
        }
        
        async function exportFilteredData(format) {
            const tableName = document.getElementById('export-table-select').value;
            if (!tableName) {
                alert('กรุณาเลือกตารางก่อน');
                return;
            }
            
            try {
                const response = await fetch(`/api/data?table=${encodeURIComponent(tableName)}`);
                let data = await response.json();
                
                // Apply filters
                data = applyFilters(data);
                
                if (data.length === 0) {
                    alert('ไม่มีข้อมูลที่ตรงกับเงื่อนไขที่เลือก');
                    return;
                }
                
                // Create and download file
                let content, mimeType, filename;
                
                if (format === 'csv') {
                    const headers = Object.keys(data[0]);
                    const csvContent = [
                        headers.join(','),
                        ...data.map(row => headers.map(h => `"${row[h] || ''}"`).join(','))
                    ].join('\\n');
                    
                    content = csvContent;
                    mimeType = 'text/csv;charset=utf-8;';
                    filename = `${tableName}_filtered.csv`;
                } else {
                    content = JSON.stringify(data, null, 2);
                    mimeType = 'application/json;charset=utf-8;';
                    filename = `${tableName}_filtered.json`;
                }
                
                const blob = new Blob([content], { type: mimeType });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                alert(`ส่งออกข้อมูล ${data.length} รายการเป็น ${format.toUpperCase()} สำเร็จ!`);
                
            } catch (error) {
                console.error('Export error:', error);
                alert('เกิดข้อผิดพลาดในการส่งออกข้อมูล');
            }
        }
                
            } catch (error) {
                console.error('Error loading tables:', error);
            }
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
                    document.getElementById('occupancy-detail').textContent = `${occupiedRooms}/${totalRooms} ห้อง`;
                    
                    const roomsGrid = document.getElementById('rooms-grid');
                    roomsGrid.innerHTML = data.map(room => {
                        const statusClass = room.สถานะ === 'ว่าง' ? 'bg-green-50 border-green-200' : 
                                          room.สถานะ === 'มีผู้เข้าพัก' ? 'bg-red-50 border-red-200' : 'bg-gray-100 border-gray-200';
                        const statusText = room.สถานะ === 'ว่าง' ? 'ว่าง' : 
                                         room.สถานะ === 'มีผู้เข้าพัก' ? 'ไม่ว่าง' : 'ซ่อม';
                        const statusBadgeClass = room.สถานะ === 'ว่าง' ? 'bg-green-100 text-green-700' : 
                                               room.สถานะ === 'มีผู้เข้าพัก' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700';
                        
                        return `
                            <div class="p-3 md:p-4 rounded-lg border flex flex-col items-center justify-center text-center transition-all cursor-pointer hover:scale-105 shadow-sm hover:shadow-md ${statusClass}">
                                <span class="font-bold text-slate-700 text-sm">${room.เลขห้อง}</span>
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
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            showTab('dashboard');
            generateCalendar();
            refreshData();
            setupExportFilters();
            
            // Auto collapse sidebar on mobile
            if (window.innerWidth < 768) {
                sidebarCollapsed = true;
                document.getElementById('sidebar').classList.add('collapsed');
            }
        });
        
        // Handle window resize
        window.addEventListener('resize', function() {
            if (window.innerWidth >= 768) {
                document.getElementById('sidebar').classList.remove('collapsed');
                document.getElementById('sidebar-overlay').classList.add('hidden');
                sidebarCollapsed = false;
            } else if (!sidebarCollapsed) {
                document.getElementById('sidebar-overlay').classList.remove('hidden');
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
        try:
            conn = sqlite3.connect('/root/projects/hotel-management/database/data/โรงแรม.db')
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
        try:
            conn = sqlite3.connect('/root/projects/hotel-management/database/data/โรงแรม.db')
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
        try:
            conn = sqlite3.connect('/root/projects/hotel-management/database/data/โรงแรม.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM `{table_name}`")
            rows = cursor.fetchall()
            data = [dict(row) for row in rows]
            conn.close()
            
            if format_type == 'csv':
                import csv, io
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
    server = HTTPServer(('0.0.0.0', 8081), DatabaseWebInterface)
    print("🌐 Responsive Web Interface เริ่มทำงานที่ http://localhost:8081")
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
