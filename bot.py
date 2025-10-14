import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from pydub import AudioSegment

# ضع توكن البوت هنا (أدخل التوكن داخل علامات الاقتباس)
BOT_TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"

# ضع رابط الـ API المنشور على GitHub/Replit هنا (مثال: https://your-app.repl.co/download?url=)
API_URL = "https://YOUR_DEPLOY_URL/download?url="

video_links = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أرسل رابط من أي منصة (يوتيوب، إنستغرام، تيك توك، فيسبوك، تويتر، ساوند كلاود...)\n"
        "وسأحمّله لك مباشرة 🎥"
    )

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    chat_id = update.message.chat_id
    await update.message.reply_text("🔄 جاري التحميل...")

    try:
        r = requests.get(API_URL + url, timeout=30)
        data = r.json()

        if data.get('status') != 'ok' or not data.get('url'):
            raise Exception('فشل الحصول على رابط التحميل من الـ API')

        video_url = data['url']
        video_links[chat_id] = video_url

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton('🎵 استخراج الصوت', callback_data='extract_audio')]
        ])

        await update.message.reply_video(video_url, caption='✅ تم التحميل بنجاح!', reply_markup=keyboard)

    except Exception as e:
        await update.message.reply_text(f"⚠️ حدث خطأ أثناء التحميل:\n{e}")

async def extract_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id
    await query.answer()
    await query.message.reply_text('🎧 جارٍ استخراج الصوت...')

    try:
        video_url = video_links.get(chat_id)
        if not video_url:
            await query.message.reply_text('⚠️ لا يوجد فيديو لاستخراج الصوت منه.')
            return

        video_path = 'temp_video.mp4'
        audio_path = 'temp_audio.mp3'

        with open(video_path, 'wb') as f:
            f.write(requests.get(video_url).content)

        AudioSegment.from_file(video_path).export(audio_path, format='mp3')
        await query.message.reply_audio(open(audio_path, 'rb'), caption='🎵 تم استخراج الصوت بنجاح!')

        os.remove(video_path)
        os.remove(audio_path)

    except Exception as e:
        await query.message.reply_text(f"⚠️ خطأ أثناء استخراج الصوت:\n{e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(extract_audio, pattern='extract_audio'))
    app.run_polling()
