import os
import asyncio
import random
import instaloader
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# تحميل المتغيرات من ملف .env
load_dotenv()

# قراءة البيانات من البيئة (أكثر أماناً)
TELEGRAM_TOKEN = os.getenv('BOT_TOKEN')
import os
from dotenv import load_dotenv

load_dotenv() # هذه الوظيفة تفتح ملف .env وتقرأ ما بداخله

INSTA_USER = os.getenv('INSTA_USER') # سيأخذ اسم الحساب من الملف
INSTA_PASS = os.getenv('INSTA_PASS') # سيأخذ كلمة السر من الملف


# تهيئة Instaloader
L = instaloader.Instaloader()

def smart_login():
    session_file = f"session-{INSTA_USER}"
    try:
        if os.path.exists(session_file):
            L.load_session_from_file(INSTA_USER, filename=session_file)
            print("✅ Session loaded.")
        else:
            L.login(INSTA_USER, INSTA_PASS)
            L.save_session_to_file(filename=session_file)
            print("✅ New session created.")
    except Exception as e:
        print(f"❌ Login error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! أرسل يوزر إنستغرام لجلب الستوريات مخفياً 🕵️‍♂️")

async def handle_insta_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip().replace("@", "")
    msg = await update.message.reply_text(f"⏳ جاري فحص {username}...")

    try:
        await asyncio.sleep(random.randint(2, 4))
        profile = instaloader.Profile.from_username(L.context, username)
        
        found = False
        for story in L.get_stories(userids=[profile.userid]):
            for item in story.get_items():
                found = True
                if item.is_video:
                    await update.message.reply_video(video=item.video_url)
                else:
                    await update.message.reply_photo(photo=item.url)
                await asyncio.sleep(1)

        if not found:
            await msg.edit_text("❌ لا توجد ستوريات حالياً.")
        else:
            await msg.delete()

    except Exception as e:
        await msg.edit_text("⚠️ خطأ أو الحساب خاص.")

def main():
    if not TELEGRAM_TOKEN:
        print("❌ Error: BOT_TOKEN not found in .env file")
        return
    
    smart_login()
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_insta_request))
    
    print("🚀 Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
