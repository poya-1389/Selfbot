import sqlite3
import os

def create_tables():
    db_path = os.getenv("DATABASE_URL", "sqlite:///selfbot.db").replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # جدول کاربران
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            phone TEXT,
            session_string TEXT,
            is_active BOOLEAN DEFAULT 0,
            is_approved BOOLEAN DEFAULT 0,
            font_name TEXT DEFAULT 'default',
            last_bio TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # جدول تنظیمات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            user_id INTEGER PRIMARY KEY,
            bio_time BOOLEAN DEFAULT 1,
            name_time BOOLEAN DEFAULT 1,
            update_interval INTEGER DEFAULT 60,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ دیتابیس با موفقیت ساخته شد!")

if __name__ == "__main__":
    create_tables()
