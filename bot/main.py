import sys
import os
import logging
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from database.create_tables import create_tables
from bot.handlers import (
    start_command, handle_user_info, panel_command,
    button_callback
)
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"❌ Error: {context.error}")

async def main_async():
    logger.info("🚀 Starting SelfBot...")
    
    if not Config.BOT_TOKEN:
        logger.error("❌ BOT_TOKEN is not set!")
        return
    
    try:
        create_tables()
        logger.info("✅ Database created")
    except Exception as e:
        logger.error(f"❌ Database error: {e}")
    
    try:
        application = Application.builder().token(Config.BOT_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("panel", panel_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_info))
        application.add_handler(CallbackQueryHandler(button_callback))
        application.add_error_handler(error_handler)
        
        logger.info("✅ Bot handlers registered")
        
        # حذف Webhook قبل از استارت Polling
        await application.bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Webhook deleted")
        
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        
        logger.info("✅ Bot is running successfully!")
        
        while True:
            await asyncio.sleep(60)
            
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
        raise

def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("⏹ Bot stopped")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
