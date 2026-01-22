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
