import tweepy
import os
import json
from datetime import datetime
from config import TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET

# الاتصال بتويتر
auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
twitter_api = tweepy.API(auth)

# ملف حفظ عدد التغريدات
COUNTER_FILE = "tweet_counter.json"

# الحدود
DAILY_LIMIT = 50
MONTHLY_LIMIT = 1500

def load_counter():
    """تحميل عدد التغريدات المخزن"""
    if not os.path.exists(COUNTER_FILE):
        return {"date": datetime.now().strftime("%Y-%m-%d"), "month": datetime.now().strftime("%Y-%m"), "daily_count": 0, "monthly_count": 0}
    
    with open(COUNTER_FILE, "r") as f:
        return json.load(f)

def save_counter(counter):
    """حفظ عدد التغريدات"""
    with open(COUNTER_FILE, "w") as f:
        json.dump(counter, f)

def reset_counter_if_needed(counter):
    """إعادة تعيين العداد يوميًا أو شهريًا"""
    today = datetime.now().strftime("%Y-%m-%d")
    month = datetime.now().strftime("%Y-%m")

    if counter["date"] != today:
        counter["date"] = today
        counter["daily_count"] = 0

    if counter["month"] != month:
        counter["month"] = month
        counter["monthly_count"] = 0

    return counter

def can_tweet():
    """التحقق من إمكانية النشر"""
    counter = load_counter()
    counter = reset_counter_if_needed(counter)

    if counter["daily_count"] >= DAILY_LIMIT:
        print("⚠️ الحد اليومي للتغريدات تم الوصول إليه.")
        return False

    if counter["monthly_count"] >= MONTHLY_LIMIT:
        print("⚠️ الحد الشهري للتغريدات تم الوصول إليه.")
        return False

    return True

def post_to_twitter(news_text, media_path, source):
    """نشر الخبر على تويتر"""
    counter = load_counter()
    counter = reset_counter_if_needed(counter)

    if not can_tweet():
        return

    tweet_text = f"{news_text}\n\n📡 المصدر: {source}" if news_text else f"📡 المصدر: {source}"

    try:
        if media_path:
            media = twitter_api.media_upload(media_path)
            twitter_api.update_status(status=tweet_text, media_ids=[media.media_id])
            os.remove(media_path)  # حذف الملف بعد النشر
        else:
            twitter_api.update_status(tweet_text)

        counter["daily_count"] += 1
        counter["monthly_count"] += 1
        save_counter(counter)

        print(f"✅ تم النشر ({counter['daily_count']}/{DAILY_LIMIT} اليوم، {counter['monthly_count']}/{MONTHLY_LIMIT} هذا الشهر).")
    
    except Exception as e:
        print(f"⚠️ خطأ أثناء النشر على تويتر: {e}")
