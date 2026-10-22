import os
import telebot
import yt_dlp
from flask import Flask, request

app = Flask(__name__)

TELEGRAM_TOKEN = "7472815918:AAHH7R0HIjAA8T7x1YvgCWq48reACMb5tnI"
WEBHOOK_URL = f"https://video-downloader-akb8.onrender.com/{TELEGRAM_TOKEN}"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# downloads papkasi mavjudligini ta'minlash
os.makedirs("downloads", exist_ok=True)

# Gunicorn start olganda avtomatik webhookni o'rnatish
try:
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    print("Webhook muvaffaqiyatli ulandi!")
except Exception as e:
    print(f"Webhook ulashda xatolik: {e}")

# Instagram video yuklab oluvchi funksiya
def download_instagram_video(url):
    ydl_opts = {
        "format": "best",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "quiet": True,
        "no_warnings": True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_path = ydl.prepare_filename(info_dict)
    
    return video_path

# Bot xabarlarni qabul qiladi
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Salom! Menga Instagram video havolasini yuboring, men uni yuklab beraman.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if url and "instagram.com" in url:
        try:
            bot.send_message(message.chat.id, "📥 Videoni yuklab olmoqdaman, iltimos kuting...")
            video_path = download_instagram_video(url)
            if os.path.exists(video_path):
                with open(video_path, "rb") as video:
                    bot.send_video(message.chat.id, video)
                os.remove(video_path)
        except Exception as e:
            bot.send_message(message.chat.id, f"Xatolik yuz berdi: {e}")
    else:
        bot.send_message(message.chat.id, "Iltimos, to'g'ri Instagram video havolasini yuboring.")

# Telegram xabarlari keladigan endpoint (POST)
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "OK", 200
    return "Forbidden", 403

# Bosh sahifa
@app.route('/', methods=["GET", "POST"])
def home():
    return "Bot faol ishlamoqda!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)