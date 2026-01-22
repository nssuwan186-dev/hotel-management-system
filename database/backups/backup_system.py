#!/usr/bin/env python3
"""
ระบบสำรองข้อมูล - Database Backup System
"""
import sqlite3
import json
import os
import shutil
from datetime import datetime
import zipfile

class DatabaseBackup:
    def __init__(self, db_path="/root/projects/hotel-management/database/data/โรงแรม.db"):
        self.db_path = db_path
        self.backup_dir = "/root/projects/hotel-management/backup"
        self.ensure_backup_dir()
    
    def ensure_backup_dir(self):
        """สร้างโฟลเดอร์สำรอง"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def create_backup(self):
        """สร้างไฟล์สำรอง"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # สำรองไฟล์ database
        db_backup = os.path.join(self.backup_dir, f"database_{timestamp}.db")
        shutil.copy2(self.db_path, db_backup)
        
        # สำรองเป็น JSON
        json_backup = os.path.join(self.backup_dir, f"data_{timestamp}.json")
        self.export_to_json(json_backup)
        
        # สร้าง ZIP
        zip_backup = os.path.join(self.backup_dir, f"backup_{timestamp}.zip")
        with zipfile.ZipFile(zip_backup, 'w') as zipf:
            zipf.write(db_backup, f"database_{timestamp}.db")
            zipf.write(json_backup, f"data_{timestamp}.json")
        
        # ลบไฟล์ชั่วคราว
        os.remove(db_backup)
        os.remove(json_backup)
        
        print(f"✅ สำรองข้อมูลแล้ว: {zip_backup}")
        return zip_backup
    
    def export_to_json(self, json_path):
        """ส่งออกข้อมูลเป็น JSON"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        data = {}
        
        # ดึงรายชื่อตาราง
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            if table != 'sqlite_sequence':
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                data[table] = [dict(row) for row in rows]
        
        conn.close()
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    def list_backups(self):
        """แสดงรายการไฟล์สำรอง"""
        backups = []
        for file in os.listdir(self.backup_dir):
            if file.startswith('backup_') and file.endswith('.zip'):
                file_path = os.path.join(self.backup_dir, file)
                size = os.path.getsize(file_path)
                mtime = os.path.getmtime(file_path)
                backups.append({
                    'file': file,
                    'path': file_path,
                    'size': size,
                    'date': datetime.fromtimestamp(mtime)
                })
        
        backups.sort(key=lambda x: x['date'], reverse=True)
        return backups
    
    def auto_cleanup(self, keep_count=5):
        """ลบไฟล์สำรองเก่า เก็บไว้แค่ N ไฟล์"""
        backups = self.list_backups()
        if len(backups) > keep_count:
            for backup in backups[keep_count:]:
                os.remove(backup['path'])
                print(f"🗑️ ลบไฟล์เก่า: {backup['file']}")

def main():
    backup = DatabaseBackup()
    
    print("🔄 เริ่มสำรองข้อมูล...")
    backup_file = backup.create_backup()
    
    print("\n📋 รายการไฟล์สำรอง:")
    backups = backup.list_backups()
    for i, b in enumerate(backups[:5], 1):
        size_mb = b['size'] / 1024 / 1024
        print(f"  {i}. {b['file']} ({size_mb:.1f} MB) - {b['date'].strftime('%Y-%m-%d %H:%M')}")
    
    # ลบไฟล์เก่า
    backup.auto_cleanup(5)
    
    print(f"\n✅ สำรองข้อมูลเสร็จสิ้น")

if __name__ == "__main__":
    main()
