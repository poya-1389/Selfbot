import sqlite3
import os
from typing import Optional, Dict, Any

class DatabaseManager:
    def __init__(self):
        db_path = os.getenv("DATABASE_URL", "sqlite:///selfbot.db").replace("sqlite:///", "")
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
    
    def add_user(self, user_id: int, phone: str, session_string: str):
        """افزودن کاربر جدید"""
        self.cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, phone, session_string)
            VALUES (?, ?, ?)
        ''', (user_id, phone, session_string))
        self.conn.commit()
        
        # تنظیمات پیش‌فرض
        self.cursor.execute('''
            INSERT OR IGNORE INTO settings (user_id)
            VALUES (?)
        ''', (user_id,))
        self.conn.commit()
    
    def approve_user(self, user_id: int):
        """تایید کاربر توسط ادمین"""
        self.cursor.execute('''
            UPDATE users SET is_approved = 1 WHERE user_id = ?
        ''', (user_id,))
        self.conn.commit()
    
    def activate_user(self, user_id: int, active: bool = True):
        """فعال/غیرفعال کردن سلف‌بات کاربر"""
        self.cursor.execute('''
            UPDATE users SET is_active = ? WHERE user_id = ?
        ''', (1 if active else 0, user_id))
        self.conn.commit()
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """دریافت اطلاعات کاربر"""
        self.cursor.execute('''
            SELECT u.*, s.bio_time, s.name_time, s.update_interval
            FROM users u
            LEFT JOIN settings s ON u.user_id = s.user_id
            WHERE u.user_id = ?
        ''', (user_id,))
        row = self.cursor.fetchone()
        if row:
            columns = [description[0] for description in self.cursor.description]
            return dict(zip(columns, row))
        return None
    
    def get_all_users(self) -> list:
        """دریافت همه کاربران"""
        self.cursor.execute('''
            SELECT u.*, s.bio_time, s.name_time, s.update_interval
            FROM users u
            LEFT JOIN settings s ON u.user_id = s.user_id
            WHERE u.is_approved = 1 AND u.is_active = 1
        ''')
        rows = self.cursor.fetchall()
        columns = [description[0] for description in self.cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    def update_setting(self, user_id: int, setting: str, value):
        """به‌روزرسانی تنظیمات کاربر"""
        self.cursor.execute(f'''
            UPDATE settings SET {setting} = ? WHERE user_id = ?
        ''', (value, user_id))
        self.conn.commit()
    
    def update_user_info(self, user_id: int, field: str, value):
        """به‌روزرسانی اطلاعات کاربر"""
        self.cursor.execute(f'''
            UPDATE users SET {field} = ? WHERE user_id = ?
        ''', (value, user_id))
        self.conn.commit()
    
    def close(self):
        self.conn.close()
