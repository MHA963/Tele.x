import time
from tlg_handler import fetch_latest_news
from x_handler import post_to_twitter, can_tweet
from datetime import datetime

def run_scheduler():
    # running scheduler every 30 minutes
    while True:
        current_minute = datetime.now().minute
        if current_minute == 0 or current_minute == 30:  # بداية الساعة ونهايتها
            if can_tweet():
                news = fetch_latest_news()
                if news:
                    post_to_twitter(news["text"], news["media"], news["source"])
            time.sleep(60)  # انتظر دقيقة لتجنب النشر المكرر
        time.sleep(10)  # تحقق كل 10 ثوانٍ

if __name__ == "__main__":
    run_scheduler()
