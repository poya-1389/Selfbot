from telethon import TelegramClient, errors
from telethon.sessions import StringSession
import asyncio
import logging
from typing import Optional
from utils.fonts import convert_to_font
from utils.helpers import format_time_for_bio, format_time_for_name, get_tehran_time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SelfBotFunctions:
    def __init__(self, session_string: str, api_id: int, api_hash: str):
        self.client = TelegramClient(
            StringSession(session_string),
            api_id,
            api_hash
        )
        self.is_running = False
        self.me = None
    
    async def start(self):
        """استارت سلف‌بات"""
        try:
            await self.client.start()
            self.me = await self.client.get_me()
            logger.info(f"✅ سلف‌بات برای {self.me.first_name} راه‌اندازی شد")
            return True
        except Exception as e:
            logger.error(f"❌ خطا در استارت سلف‌بات: {e}")
            return False
    
    async def update_bio(self, text: str):
        """به‌روزرسانی بیو"""
        try:
            await self.client.set_bio(text)
            return True
        except errors.FloodWaitError as e:
            logger.warning(f"⏳ محدودیت تلگرام: {e.seconds} ثانیه صبر کن")
            await asyncio.sleep(e.seconds)
            return False
        except Exception as e:
            logger.error(f"❌ خطا در بروزرسانی بیو: {e}")
            return False
    
    async def update_name(self, first_name: str, last_name: str = ""):
        """به‌روزرسانی نام و نام خانوادگی"""
        try:
            await self.client.set_name(first_name, last_name)
            return True
        except errors.FloodWaitError as e:
            logger.warning(f"⏳ محدودیت تلگرام: {e.seconds} ثانیه صبر کن")
            await asyncio.sleep(e.seconds)
            return False
        except Exception as e:
            logger.error(f"❌ خطا در بروزرسانی نام: {e}")
            return False
    
    async def update_profile_with_time(self, font_name: str = 'default', 
                                       bio_time: bool = True, 
                                       name_time: bool = True):
        """به‌روزرسانی کامل پروفایل با تایم"""
        now = get_tehran_time()
        time_str = now.strftime("%H:%M")
        
        # ساخت بیو با تایم
        if bio_time:
            bio_text = f"⌚ {time_str} | {now.strftime('%Y/%m/%d')}"
        else:
            bio_text = ""
        
        # ساخت نام با تایم (در فامیلی)
        if name_time:
            name_text = time_str
            # اعمال فونت روی نام
            font_name_display = convert_to_font(name_text, font_name)
            first_name = "🕐"  # یا هر نام دیگری
            last_name = font_name_display
        else:
            first_name = self.me.first_name if self.me else ""
            last_name = self.me.last_name if self.me else ""
        
        # به‌روزرسانی
        tasks = []
        if bio_time:
            tasks.append(self.update_bio(bio_text))
        if name_time:
            tasks.append(self.update_name(first_name, last_name))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return all(r is True for r in results)
    
    async def run_loop(self, user_id: int, db_manager, font_name: str = 'default',
                      bio_time: bool = True, name_time: bool = True,
                      update_interval: int = 60):
        """حلقه اصلی به‌روزرسانی"""
        self.is_running = True
        logger.info(f"🔄 شروع حلقه به‌روزرسانی برای کاربر {user_id}")
        
        while self.is_running:
            try:
                # دریافت تنظیمات جدید از دیتابیس
                user_data = db_manager.get_user(user_id)
                if not user_data or not user_data.get('is_active'):
                    logger.info(f"⏹ سلف‌بات برای کاربر {user_id} غیرفعال شد")
                    break
                
                # به‌روزرسانی پروفایل
                success = await self.update_profile_with_time(
                    font_name=user_data.get('font_name', 'default'),
                    bio_time=bool(user_data.get('bio_time', 1)),
                    name_time=bool(user_data.get('name_time', 1))
                )
                
                if success:
                    logger.info(f"✅ پروفایل کاربر {user_id} به‌روز شد")
                else:
                    logger.warning(f"⚠️ خطا در به‌روزرسانی پروفایل کاربر {user_id}")
                
                # انتظار برای دور بعد
                await asyncio.sleep(update_interval)
                
            except Exception as e:
                logger.error(f"❌ خطا در حلقه سلف‌بات {user_id}: {e}")
                await asyncio.sleep(10)  # در صورت خطا، ۱۰ ثانیه صبر کن
    
    async def stop(self):
        """متوقف کردن سلف‌بات"""
        self.is_running = False
        await self.client.disconnect()
        logger.info("⏹ سلف‌بات متوقف شد")
