import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ربات مدیریت
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", 0))
    
    # سلف‌بات
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH")
    
    # دیتابیس
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///selfbot.db")
    
    # تنظیمات تایم
    TIMEZONE = "Asia/Tehran"
    UPDATE_INTERVAL = 60  # ثانیه
    
    # مسیرها
    SESSION_DIR = "sessions"
