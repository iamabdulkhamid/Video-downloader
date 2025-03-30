import os
import telebot
import yt_dlp
from flask import Flask, request

# Flask server yaratamiz
app = Flask(__name__)

# Telegram bot tokeni
TELEGRAM_TOKEN = os.getenv("Telegramtoken")
if not TELEGRAM_TOKEN:
    raise ValueError("Telegram bot tokeni topilmadi! Environment variable-ni tekshiring.")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Webhook URL
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://telegram-instagram-bot.onrender.com").rstrip("/") + f"/{TELEGRAM_TOKEN}"

# Instagram videolarni yuklab oluvchi funksiya
def download_instagram_video(url):
    ydl_opts = {
        "format": "best",
        "outtmpl": "downloads/%(title)s.%(ext)s",
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_path = ydl.prepare_filename(info_dict)
    
    return video_path

# Bot xabarlarni qabul qiladi
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if "instagram.com" in url:
        try:
            bot.send_message(message.chat.id, "📥 Videoni yuklab olmoqdaman, iltimos kuting...")
            video_path = download_instagram_video(url)
            with open(video_path, "rb") as video:
                bot.send_video(message.chat.id, video)
            os.remove(video_path)  # Faylni o‘chiramiz
        except Exception as e:
            bot.send_message(message.chat.id, f"Xatolik yuz berdi: {e}")
    else:
        bot.send_message(message.chat.id, "Iltimos, Instagram video havolasini yuboring.")

# Webhook uchun endpoint
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# Webhookni sozlash
@app.route('/set_webhook')
def set_webhook():
    bot.remove_webhook()
    success = bot.set_webhook(url=WEBHOOK_URL)
    return f"Webhook o‘rnatildi! Status: {success}", 200

# Bosh sahifa
@app.route('/')
def home():
    return "Instagram video yuklovchi bot ishlamoqda!", 200

if __name__ == "__main__":
    bot.remove_webhook()
    success = bot.set_webhook(url=WEBHOOK_URL)
    if not success:
        print("Webhook o‘rnatilmadi! Telegram API bilan bog‘lanishda muammo bo‘lishi mumkin.")
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
