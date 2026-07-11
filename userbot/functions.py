from telethon import TelegramClient, errors
from telethon.sessions import StringSession
import asyncio
import logging
from utils.helpers import get_tehran_time

logger = logging.getLogger(__name__)

class SelfBotFunctions:
    def __init__(self, session_string: str, api_id: int, api_hash: str):
        self.client = TelegramClient(StringSession(session_string), api_id, api_hash)
        self.is_running = False
        self.me = None

    async def start(self):
        try:
            await self.client.start()
            self.me = await self.client.get_me()
            logger.info(f"✅ سلف‌بات برای {self.me.first_name} راه‌اندازی شد")
            return True
        except Exception as e:
            logger.error(f"❌ خطا در استارت: {e}")
            return False

    async def stop(self):
        self.is_running = False
        try:
            await self.client.disconnect()
        except:
            pass
        logger.info("⏹ سلف‌بات متوقف شد")

    async def update_bio(self, text: str):
        try:
            await self.client.set_bio(text)
            return True
        except errors.FloodWaitError as e:
            logger.warning(f"⏳ محدودیت: {e.seconds} ثانیه صبر کن")
            await asyncio.sleep(e.seconds)
            return False
        except Exception as e:
            logger.error(f"❌ خطا در بروزرسانی بیو: {e}")
            return False

    async def update_name(self, first_name: str, last_name: str = ""):
        try:
            await self.client.set_name(first_name, last_name)
            return True
        except errors.FloodWaitError as e:
            logger.warning(f"⏳ محدودیت: {e.seconds} ثانیه صبر کن")
            await asyncio.sleep(e.seconds)
            return False
        except Exception as e:
            logger.error(f"❌ خطا در بروزرسانی نام: {e}")
            return False

    async def update_profile_with_time(self, font_name: str = 'default', bio_time: bool = True, name_time: bool = True):
        try:
            now = get_tehran_time()
            time_str = now.strftime("%H:%M")
            date_str = now.strftime("%Y/%m/%d")
            
            if bio_time:
                bio_text = f"⌚ {time_str} | {date_str}"
                await self.update_bio(bio_text)
            
            if name_time:
                first_name = "🕐"
                last_name = time_str
                await self.update_name(first_name, last_name)
            
            return True
        except Exception as e:
            logger.error(f"❌ خطا در به‌روزرسانی پروفایل: {e}")
            return False

    async def run_loop(self, user_id: int, db_manager, font_name: str = 'default',
                      bio_time: bool = True, name_time: bool = True,
                      update_interval: int = 60):
        self.is_running = True
        logger.info(f"🔄 شروع حلقه به‌روزرسانی برای کاربر {user_id}")
        
        while self.is_running:
            try:
                user_data = db_manager.get_user(user_id)
                if not user_data or not user_data.get('is_active'):
                    logger.info(f"⏹ سلف‌بات برای {user_id} غیرفعال شد")
                    break
                
                success = await self.update_profile_with_time(
                    font_name=user_data.get('font_name', 'default'),
                    bio_time=bool(user_data.get('bio_time', 1)),
                    name_time=bool(user_data.get('name_time', 1))
                )
                
                if success:
                    logger.info(f"✅ پروفایل {user_id} به‌روز شد")
                else:
                    logger.warning(f"⚠️ خطا در به‌روزرسانی {user_id}")
                
                await asyncio.sleep(update_interval)
                
            except Exception as e:
                logger.error(f"❌ خطا در حلقه {user_id}: {e}")
                await asyncio.sleep(10)
