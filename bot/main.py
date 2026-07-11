from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import logging
import asyncio
import os
from config import Config
from database.create_tables import create_tables
from bot.handlers import (
    start_command, handle_user_info, panel_command,
    button_callback
)
from aiohttp import web  # <-- اضافه کن

# تنظیم لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def health_check(request):
    """Endpoint برای Healthcheck"""
    return web.Response(text="OK", status=200)

async def start_web_server():
    """راه‌اندازی وب سرور برای Healthcheck"""
    app = web.Application()
    app.router.add_get('/health', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    logger.info("✅ Web server started on port 8080")
    return runner

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت خطاها"""
    logger.error(f"خطا: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ خطایی رخ داد! لطفاً دوباره تلاش کنید."
        )

async def main_async():
    """تابع اصلی async"""
    # ساخت دیتابیس
    create_tables()
    
    # استارت وب سرور
    await start_web_server()
    
    # ساخت اپلیکیشن ربات
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # اضافه کردن هندلرها
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("panel", panel_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_info))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_error_handler(error_handler)
    
    # استارت ربات
    logger.info("🚀 ربات شروع به کار کرد...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # نگه داشتن برنامه
    while True:
        await asyncio.sleep(3600)

def main():
    """تابع اصلی"""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("⏹ ربات متوقف شد")

if __name__ == "__main__":
    main()
