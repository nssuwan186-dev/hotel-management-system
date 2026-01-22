#!/usr/bin/env python3
"""
Web Interface สำหรับดูฐานข้อมูล SQLite
"""
import sqlite3
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

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
        elif path == '/api/query':
            sql = query.get('sql', [''])[0]
            self.serve_query_result(sql)
        else:
            self.send_error(404)
    
    def serve_main_page(self):
        """Serve main HTML page"""
        html = '''<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏨 ฐานข้อมูลโรงแรม SQLite</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
        .tabs { display: flex; margin-bottom: 20px; border-bottom: 2px solid #ecf0f1; }
        .tab { padding: 10px 20px; cursor: pointer; border: none; background: none; font-size: 16px; }
        .tab.active { background: #3498db; color: white; border-radius: 5px 5px 0 0; }
        .content { display: none; }
        .content.active { display: block; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #34495e; color: white; }
        tr:hover { background-color: #f5f5f5; }
        .query-box { width: 100%; height: 100px; margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .btn { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .btn:hover { background: #2980b9; }
        .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏨 ฐานข้อมูลโรงแรม SQLite</h1>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('overview')">📊 ภาพรวม</button>
            <button class="tab" onclick="showTab('tables')">🗂️ ตาราง</button>
            <button class="tab" onclick="showTab('query')">🔍 Query</button>
            <button class="tab" onclick="showTab('relationships')">🔗 ความสัมพันธ์</button>
        </div>
        
        <div id="overview" class="content active">
            <h2>📊 ภาพรวมฐานข้อมูล</h2>
            <div id="overview-content">กำลังโหลด...</div>
        </div>
        
        <div id="tables" class="content">
            <h2>🗂️ ตารางทั้งหมด</h2>
            <select id="table-select" onchange="loadTableData()">
                <option value="">เลือกตาราง...</option>
            </select>
            <div id="table-content"></div>
        </div>
        
        <div id="query" class="content">
            <h2>🔍 SQL Query</h2>
            <textarea id="sql-query" class="query-box" placeholder="พิมพ์ SQL query ที่นี่...">SELECT * FROM ผู้เข้าพัก;</textarea>
            <br>
            <button class="btn" onclick="executeQuery()">🚀 Execute</button>
            <div id="query-result"></div>
        </div>
        
        <div id="relationships" class="content">
            <h2>🔗 ความสัมพันธ์ระหว่างตาราง</h2>
            <div class="info">
                <h3>Foreign Key Relationships:</h3>
                <ul>
                    <li><strong>ห้องพัก.รหัสผู้เข้าพัก</strong> → ผู้เข้าพัก.รหัส</li>
                    <li><strong>งานตรวจสอบ.รหัสรายการ</strong> → รายการตรวจสอบ.รหัส</li>
                    <li><strong>การโหวต.รหัสข้อเสนอแนะ</strong> → ข้อเสนอแนะ.รหัส</li>
                </ul>
                
                <h3>ตัวอย่าง JOIN Queries:</h3>
                <pre>-- ห้องพักพร้อมข้อมูลผู้เข้าพัก
SELECT h.เลขห้อง, h.ประเภท, h.สถานะ, p.ชื่อ, p.โทรศัพท์
FROM ห้องพัก h
LEFT JOIN ผู้เข้าพัก p ON h.รหัสผู้เข้าพัก = p.รหัส;

-- สถิติห้องตามประเภท
SELECT ประเภท, COUNT(*) as จำนวน, AVG(ราคา) as ราคาเฉลี่ย
FROM ห้องพัก GROUP BY ประเภท;</pre>
            </div>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            // Hide all content
            document.querySelectorAll('.content').forEach(c => c.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            
            // Show selected content
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            if (tabName === 'overview') loadOverview();
            if (tabName === 'tables') loadTables();
        }
        
        function loadOverview() {
            fetch('/api/query?sql=SELECT name FROM sqlite_master WHERE type="table"')
                .then(r => r.json())
                .then(data => {
                    let html = '<div class="info"><h3>📋 ตารางในฐานข้อมูล:</h3><ul>';
                    data.forEach(row => {
                        html += `<li>${row[0]}</li>`;
                    });
                    html += '</ul></div>';
                    
                    // Add statistics
                    Promise.all([
                        fetch('/api/query?sql=SELECT COUNT(*) FROM ผู้เข้าพัก'),
                        fetch('/api/query?sql=SELECT COUNT(*) FROM ห้องพัก'),
                        fetch('/api/query?sql=SELECT COUNT(*) FROM ห้องพัก WHERE สถานะ="มีผู้เข้าพัก"')
                    ]).then(responses => Promise.all(responses.map(r => r.json())))
                      .then(results => {
                          html += `<div class="success">
                              <h3>📊 สถิติ:</h3>
                              <p>👥 ผู้เข้าพัก: ${results[0][0][0]} คน</p>
                              <p>🏠 ห้องทั้งหมด: ${results[1][0][0]} ห้อง</p>
                              <p>🔴 ห้องที่มีผู้เข้าพัก: ${results[2][0][0]} ห้อง</p>
                          </div>`;
                          document.getElementById('overview-content').innerHTML = html;
                      });
                });
        }
        
        function loadTables() {
            fetch('/api/tables')
                .then(r => r.json())
                .then(tables => {
                    const select = document.getElementById('table-select');
                    select.innerHTML = '<option value="">เลือกตาราง...</option>';
                    tables.forEach(table => {
                        select.innerHTML += `<option value="${table}">${table}</option>`;
                    });
                });
        }
        
        function loadTableData() {
            const table = document.getElementById('table-select').value;
            if (!table) return;
            
            fetch(`/api/data?table=${table}`)
                .then(r => r.json())
                .then(data => {
                    if (data.length === 0) {
                        document.getElementById('table-content').innerHTML = '<p>ไม่มีข้อมูลในตาราง</p>';
                        return;
                    }
                    
                    let html = '<table><thead><tr>';
                    Object.keys(data[0]).forEach(key => {
                        html += `<th>${key}</th>`;
                    });
                    html += '</tr></thead><tbody>';
                    
                    data.forEach(row => {
                        html += '<tr>';
                        Object.values(row).forEach(value => {
                            html += `<td>${value || ''}</td>`;
                        });
                        html += '</tr>';
                    });
                    html += '</tbody></table>';
                    
                    document.getElementById('table-content').innerHTML = html;
                });
        }
        
        function executeQuery() {
            const sql = document.getElementById('sql-query').value;
            if (!sql.trim()) return;
            
            fetch(`/api/query?sql=${encodeURIComponent(sql)}`)
                .then(r => r.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('query-result').innerHTML = 
                            `<div class="error">❌ Error: ${data.error}</div>`;
                        return;
                    }
                    
                    if (data.length === 0) {
                        document.getElementById('query-result').innerHTML = 
                            '<div class="success">✅ Query executed successfully (no results)</div>';
                        return;
                    }
                    
                    let html = '<div class="success">✅ Query executed successfully</div><table><thead><tr>';
                    
                    // Headers (use array indices as column names)
                    for (let i = 0; i < data[0].length; i++) {
                        html += `<th>Column ${i + 1}</th>`;
                    }
                    html += '</tr></thead><tbody>';
                    
                    data.forEach(row => {
                        html += '<tr>';
                        row.forEach(value => {
                            html += `<td>${value || ''}</td>`;
                        });
                        html += '</tr>';
                    });
                    html += '</tbody></table>';
                    
                    document.getElementById('query-result').innerHTML = html;
                })
                .catch(err => {
                    document.getElementById('query-result').innerHTML = 
                        `<div class="error">❌ Error: ${err.message}</div>`;
                });
        }
        
        // Load overview on page load
        loadOverview();
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
            conn = sqlite3.connect('/root/โรงแรม.db')
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
    
    def serve_table_data(self, table):
        """Serve table data"""
        try:
            conn = sqlite3.connect('/root/โรงแรม.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table}")
            rows = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(rows, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            self.send_error(500, str(e))
    
    def serve_query_result(self, sql):
        """Execute SQL query and return results"""
        try:
            conn = sqlite3.connect('/root/โรงแรม.db')
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(rows, ensure_ascii=False).encode('utf-8'))
        except Exception as e:
            error_response = {"error": str(e)}
            self.send_response(400)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
    
    def log_message(self, format, *args):
        """Suppress log messages"""
        pass

def start_web_interface():
    """Start web interface server"""
    server = HTTPServer(('0.0.0.0', 8081), DatabaseWebInterface)
    print("🌐 Web Interface เริ่มทำงานที่ http://localhost:8080")
    server.serve_forever()

if __name__ == "__main__":
    # Start web interface in background thread
    web_thread = threading.Thread(target=start_web_interface, daemon=True)
    web_thread.start()
    
    print("🌐 Database Web Interface พร้อมใช้งาน!")
    print("📍 URL: http://localhost:8080")
    print("🔧 กด Ctrl+C เพื่อหยุด")
    
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 หยุดการทำงาน")
