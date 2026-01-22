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
