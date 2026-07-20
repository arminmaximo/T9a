from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, InlineQueryHandler, InlineQueryResultPhoto
import os

# مسیر پوشه‌ی بات
BOT_DIR = Path(__file__).parent

# توکن بات (توکن جدیدت را اینجا قرار بده)
BOT_TOKEN = "8211735645:AAHHogNnTdxF5NkVSmrdfpjFhe23VTZZC90"  # ❌ توکن قدیمی - جایگزین کن!

# تعریف تصاویر
IMAGES = {
    "share1": "en.png",
    "share2": "he.png",
    "share3": "ru.png",
    "share4": "tr.png",
    "share5": "giften.png",
    "share6": "gifthe.png",
    "share7": "giftru.png",
    "share8": "gifttr.png",
}

# نام‌های فارسی برای دکمه‌ها
BUTTON_LABELS = {
    "share1": "🇬🇧 انگلیسی",
    "share2": "🇮🇱 عبری",
    "share3": "🇷🇺 روسی",
    "share4": "🇹🇷 ترکی",
    "share5": "🎁 هدیه انگلیسی",
    "share6": "🎁 هدیه عبری",
    "share7": "🎁 هدیه روسی",
    "share8": "🎁 هدیه ترکی",
}

def get_image_path(image_key):
    """مسیر کامل تصویر را برگردان"""
    filename = IMAGES.get(image_key)
    if not filename:
        return None
    
    image_path = BOT_DIR / filename
    
    if image_path.exists():
        return image_path
    
    print(f"⚠️ فایل پیدا نشد: {image_path}")
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /start - نمایش 8 دکمه"""
    
    # ساخت 8 دکمه (2 ستون، 4 سطر)
    keyboard = [
        [
            InlineKeyboardButton("🇬🇧 share1", callback_data="share1"),
            InlineKeyboardButton("🇮🇱 share2", callback_data="share2"),
        ],
        [
            InlineKeyboardButton("🇷🇺 share3", callback_data="share3"),
            InlineKeyboardButton("🇹🇷 share4", callback_data="share4"),
        ],
        [
            InlineKeyboardButton("🎁 share5", callback_data="share5"),
            InlineKeyboardButton("🎁 share6", callback_data="share6"),
        ],
        [
            InlineKeyboardButton("🎁 share7", callback_data="share7"),
            InlineKeyboardButton("🎁 share8", callback_data="share8"),
        ],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "👋 سلام! یک تصویر را برای اشتراک‌گذاری انتخاب کنید:",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کلیک دکمه‌ها"""
    query = update.callback_query
    await query.answer()
    
    share_id = query.data  # share1, share2, ...
    
    # دریافت مسیر تصویر
    image_path = get_image_path(share_id)
    
    if not image_path:
        await query.edit_message_text("❌ عکس پیدا نشد!")
        return
    
    # ارسال تصویر
    with open(image_path, 'rb') as f:
        await query.edit_message_media(
            media=__import__('telegram').InputMediaPhoto(
                media=f,
                caption=f"📸 {BUTTON_LABELS.get(share_id, share_id)}\n\n@YourBotUsername"
            )
        )

async def inline_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """برای inline mode - نمایش تصاویر"""
    query = update.inline_query.query
    
    # تشخیص کدام share انتخاب شده
    share_id = None
    for key in IMAGES.keys():
        if key in query.lower():
            share_id = key
            break
    
    if not share_id:
        return
    
    image_path = get_image_path(share_id)
    
    if not image_path:
        return
    
    # ارسال تصویر در inline mode
    results = [
        InlineQueryResultPhoto(
            id=share_id,
            photo_url=f"file://{image_path}",  # مسیر محلی
            thumb_url=f"file://{image_path}",
            title=BUTTON_LABELS.get(share_id, share_id),
            caption=f"🖼️ {BUTTON_LABELS.get(share_id, share_id)}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✓ اشتراک", callback_data=f"shared_{share_id}")
            ]])
        )
    ]
    
    await update.inline_query.answer(results, cache_time=0)

async def shared_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کلیک اشتراک در inline mode"""
    query = update.callback_query
    await query.answer("✅ اشتراک‌گذاری شد!", show_alert=True)

def main():
    # ایجاد Application
    app = Application.builder().token(BOT_TOKEN).build()
    
    # تنظیم handler‌ها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback, pattern="^share[1-8]$"))
    app.add_handler(CallbackQueryHandler(shared_callback, pattern="^shared_"))
    app.add_handler(InlineQueryHandler(inline_query))
    
    # شروع بات
    print("🤖 بات شروع شد...")
    app.run_polling()

if __name__ == "__main__":
    main()
