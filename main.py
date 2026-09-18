import os
import asyncio
import threading
from flask import Flask
import telebot
from shazamio import Shazam

# Render port binding xatoligi bermasligi uchun Flask server
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot status: Running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# Telegram Bot
BOT_TOKEN = "8601459584:AAGwCow9zMu6JqwcDyt9cLzu_ih1lvzdC68"
bot = telebot.TeleBot(BOT_TOKEN)
shazam = Shazam()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Salom! Menga musiqa yoki ovozli xabar yuboring, men uni topib beraman.")

@bot.message_handler(content_types=['voice', 'audio'])
def handle_audio(message):
    msg = bot.reply_to(message, "🔍 Qo'shiq qidirilmoqda...")
    file_path = None
    try:
        file_id = message.voice.file_id if message.voice else message.audio.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        file_path = f"audio_{message.message_id}.ogg"
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        out = loop.run_until_complete(shazam.recognize(file_path))
        
        track = out.get('track', {})
        title = track.get('title')
        subtitle = track.get('subtitle')
        
        if title and subtitle:
            bot.edit_message_text(f"🎵 **Topildi:** {title}\n👤 **Ijrochi:** {subtitle}", message.chat.id, msg.message_id, parse_mode="Markdown")
        else:
            bot.edit_message_text("Afsuski, bu qo'shiqni topa olmadim.", message.chat.id, msg.message_id)
            
    except Exception as e:
        bot.edit_message_text("Xatolik yuz berdi, qaytadan urinib ko'ring.", message.chat.id, msg.message_id)
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    # Flask serverni alohida oqimda ishga tushirish
    threading.Thread(target=run_flask).start()
    bot.infinity_polling()
