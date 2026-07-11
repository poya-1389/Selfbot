import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db_manager import DatabaseManager
from userbot.functions import SelfBotFunctions
from utils.fonts import FONTS
from config import Config

logger = logging.getLogger(__name__)
db = DatabaseManager()
active_selfbots = {}

# ============================================================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    if user_data and user_data.get('is_approved'):
        await update.message.reply_text(
            "✅ حساب شما قبلاً تایید شده است!\n"
            "برای مشاهده پنل از دستور .پنل استفاده کنید."
        )
        return
    
    await update.message.reply_text(
        "👋 به ربات مدیریت سلف‌بات خوش آمدید!\n\n"
        "برای فعال‌سازی، این سه خط رو ارسال کن:\n"
        "1️⃣ شماره تلفن (با کد کشور)\n"
        "2️⃣ کد تایید\n"
        "3️⃣ هش‌آیدی (String Session)\n\n"
        "مثال:\n"
        "`+989123456789`\n"
        "`12345`\n"
        "`1BQAN...`",
        parse_mode='Markdown'
    )
    context.user_data['state'] = 'WAITING_FOR_INFO'

# ============================================================
async def handle_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('state') != 'WAITING_FOR_INFO':
        return
    
    user_id = update.effective_user.id
    lines = update.message.text.strip().split('\n')
    
    if len(lines) < 3:
        await update.message.reply_text("❌ سه خط رو کامل بفرست!")
        return
    
    phone = lines[0].strip()
    code = lines[1].strip()
    session_string = lines[2].strip()
    
    db.add_user(user_id, phone, session_string)
    context.user_data['state'] = None
    
    admin_id = Config.ADMIN_USER_ID
    if admin_id:
        keyboard = [[
            InlineKeyboardButton("✅ تایید", callback_data=f"approve_{user_id}"),
            InlineKeyboardButton("❌ رد", callback_data=f"reject_{user_id}")
        ]]
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=f"📢 درخواست جدید!\n👤 کاربر: {user_id}\n📱 شماره: {phone}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            logger.error(f"خطا در ارسال به ادمین: {e}")
    
    await update.message.reply_text("✅ ثبت شد! منتظر تایید ادمین باش.")

# ============================================================
async def panel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    if not user_data or not user_data.get('is_approved'):
        await update.message.reply_text("❌ دسترسی نداری!")
        return
    
    status = "فعال ✅" if user_data.get('is_active') else "غیرفعال ❌"
    font_name = FONTS.get(user_data.get('font_name', 'default'), {}).get('name', 'پیش‌فرض')
    
    keyboard = [
        [
            InlineKeyboardButton(
                "🟢 فعال" if not user_data.get('is_active') else "🔴 غیرفعال",
                callback_data="toggle_active"
            )
        ],
        [
            InlineKeyboardButton("🎨 انتخاب فونت", callback_data="select_font")
        ],
        [
            InlineKeyboardButton("📊 وضعیت", callback_data="status")
        ]
    ]
    
    await update.message.reply_text(
        f"🎛 **پنل مدیریت**\n\n"
        f"وضعیت: {status}\n"
        f"فونت: {font_name}\n",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ============================================================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    data = query.data
    
    logger.info(f"📥 کالبک: {data} از {user_id}")
    
    if data.startswith("approve_"):
        if user_id != Config.ADMIN_USER_ID:
            await query.edit_message_text("❌ شما ادمین نیستید!")
            return
        
        target_user_id = int(data.split('_')[1])
        logger.info(f"👑 تایید کاربر {target_user_id}")
        
        db.approve_user(target_user_id)
        db.activate_user(target_user_id, True)
        
        user_data = db.get_user(target_user_id)
        logger.info(f"📊 اطلاعات کاربر: {user_data}")
        
        if user_data and user_data.get('session_string'):
            logger.info(f"🔄 استارت سلف‌بات برای {target_user_id}")
            await start_selfbot(target_user_id, user_data)
        else:
            logger.error(f"❌ session_string برای {target_user_id} پیدا نشد!")
            await query.edit_message_text(f"❌ هش‌آیدی برای {target_user_id} پیدا نشد!")
            return
        
        await query.edit_message_text(f"✅ کاربر {target_user_id} تایید شد!")
        
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text="🎉 حساب شما تایید شد! از .پنل استفاده کن."
            )
        except:
            pass
        return
    
    if data.startswith("reject_"):
        if user_id != Config.ADMIN_USER_ID:
            await query.edit_message_text("❌ شما ادمین نیستید!")
            return
        
        target_user_id = int(data.split('_')[1])
        db.activate_user(target_user_id, False)
        await query.edit_message_text(f"❌ کاربر {target_user_id} رد شد!")
        return
    
    if data == "toggle_active":
        user_data = db.get_user(user_id)
        if not user_data:
            await query.edit_message_text("❌ کاربر پیدا نشد!")
            return
        
        new_status = not user_data.get('is_active', False)
        db.activate_user(user_id, new_status)
        
        if new_status:
            await start_selfbot(user_id, user_data)
        else:
            if user_id in active_selfbots:
                await active_selfbots[user_id].stop()
                del active_selfbots[user_id]
        
        await query.edit_message_text(f"✅ سلف‌بات {'فعال' if new_status else 'غیرفعال'} شد!")
        await panel_command(update, context)
        return
    
    if data == "select_font":
        keyboard = []
        for font_key in FONTS.keys():
            keyboard.append([
                InlineKeyboardButton(FONTS[font_key]['name'], callback_data=f"set_font_{font_key}")
            ])
        keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_panel")])
        await query.edit_message_text(
            "🎨 انتخاب فونت:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    if data.startswith("set_font_"):
        font_name = data.replace("set_font_", "")
        db.update_setting(user_id, 'font_name', font_name)
        await query.edit_message_text(f"✅ فونت به {FONTS[font_name]['name']} تغییر یافت!")
        await panel_command(update, context)
        return
    
    if data == "status":
        user_data = db.get_user(user_id)
        status_text = f"""
📊 وضعیت سلف‌بات

👤 کاربر: {user_id}
🔄 وضعیت: {'فعال ✅' if user_data.get('is_active') else 'غیرفعال ❌'}
🎨 فونت: {FONTS.get(user_data.get('font_name', 'default'), {}).get('name', 'پیش‌فرض')}
        """
        await query.edit_message_text(status_text)
        await panel_command(update, context)
        return
    
    if data == "back_to_panel":
        await panel_command(update, context)
        return

# ============================================================
async def start_selfbot(user_id: int, user_data: dict):
    logger.info(f"🚀 شروع استارت سلف‌بات برای کاربر {user_id}")
    
    if user_id in active_selfbots:
        logger.info(f"⏹ توقف سلف‌بات قبلی برای {user_id}")
        try:
            await active_selfbots[user_id].stop()
        except Exception as e:
            logger.error(f"خطا در توقف: {e}")
        del active_selfbots[user_id]
    
    try:
        session = user_data.get('session_string')
        if not session:
            logger.error(f"❌ session_string برای {user_id} خالی است!")
            return
        
        logger.info(f"📱 ایجاد کلاینت برای {user_id}")
        selfbot = SelfBotFunctions(
            session_string=session,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH
        )
        
        logger.info(f"🔌 اتصال به تلگرام برای {user_id}")
        if not await selfbot.start():
            logger.error(f"❌ استارت سلف‌بات برای {user_id} ناموفق بود!")
            return
        
        logger.info(f"✅ کلاینت برای {user_id} متصل شد")
        active_selfbots[user_id] = selfbot
        
        logger.info(f"🔄 شروع حلقه به‌روزرسانی برای {user_id}")
        asyncio.create_task(selfbot.run_loop(
            user_id=user_id,
            db_manager=db,
            font_name=user_data.get('font_name', 'default'),
            bio_time=bool(user_data.get('bio_time', 1)),
            name_time=bool(user_data.get('name_time', 1)),
            update_interval=user_data.get('update_interval', 60)
        ))
        
        logger.info(f"✅✅✅ سلف‌بات برای کاربر {user_id} با موفقیت راه‌اندازی شد!")
        
    except Exception as e:
        logger.error(f"❌❌❌ خطا در راه‌اندازی سلف‌بات {user_id}: {e}")
        import traceback
        traceback.print_exc()
