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

# تنظیم لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت خطاها"""
    logger.error(f"خطا: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ خطایی رخ داد! لطفاً دوباره تلاش کنید."
        )

def main():
    """تابع اصلی"""
    # ساخت دیتابیس
    create_tables()
    
    # ساخت اپلیکیشن
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # اضافه کردن هندلرها
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("panel", panel_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_info))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_error_handler(error_handler)
    
    # استارت ربات
    logger.info("🚀 ربات شروع به کار کرد...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
