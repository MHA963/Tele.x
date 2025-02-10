import telegram
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNELS

bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

def fetch_latest_news():
    """جلب آخر الأخبار من القنوات المحددة"""
    for channel in TELEGRAM_CHANNELS:
        updates = bot.get_updates()
        for update in updates:
            if update.message and update.message.chat.id == int(channel):
                text = update.message.text or ""
                media = None
                
                if update.message.photo:
                    photo = update.message.photo[-1].get_file()
                    media = photo.download()
                
                if update.message.video:
                    video = update.message.video.get_file()
                    media = video.download()
                
                return {"text": text, "media": media, "source": channel}

    return None
