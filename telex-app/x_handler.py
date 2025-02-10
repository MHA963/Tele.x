import tweepy
import os
import json
from datetime import datetime
from config import TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET

# Connect to Twitter
auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
twitter_api = tweepy.API(auth)

# File to save tweet count
COUNTER_FILE = "tweet_counter.json"

# Limits
DAILY_LIMIT = 50
MONTHLY_LIMIT = 1500

def load_counter():
    """Load stored tweet count"""
    if not os.path.exists(COUNTER_FILE):
        return {"date": datetime.now().strftime("%Y-%m-%d"), "month": datetime.now().strftime("%Y-%m"), "daily_count": 0, "monthly_count": 0}
    
    with open(COUNTER_FILE, "r") as f:
        return json.load(f)

def save_counter(counter):
    """Save tweet count"""
    with open(COUNTER_FILE, "w") as f:
        json.dump(counter, f)

def reset_counter_if_needed(counter):
    """Reset counter daily or monthly"""
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
    """Check if tweeting is allowed"""
    counter = load_counter()
    counter = reset_counter_if_needed(counter)

    if counter["daily_count"] >= DAILY_LIMIT:
        print("⚠️ Daily tweet limit reached.")
        return False

    if counter["monthly_count"] >= MONTHLY_LIMIT:
        print("⚠️ Monthly tweet limit reached.")
        return False

    return True

def post_to_twitter(news_text, media_path, source):
    """Post news to Twitter"""
    counter = load_counter()
    counter = reset_counter_if_needed(counter)

    if not can_tweet():
        return

    tweet_text = f"{news_text}\n\n📡 Source: {source}" if news_text else f"📡 Source: {source}"

    try:
        if media_path:
            media = twitter_api.media_upload(media_path)
            twitter_api.update_status(status=tweet_text, media_ids=[media.media_id])
            os.remove(media_path)  # Delete file after posting
        else:
            twitter_api.update_status(tweet_text)

        counter["daily_count"] += 1
        counter["monthly_count"] += 1
        save_counter(counter)

        print(f"✅ Posted ({counter['daily_count']}/{DAILY_LIMIT} today, {counter['monthly_count']}/{MONTHLY_LIMIT} this month).")
    
    except Exception as e:
        print(f"⚠️ Error posting to Twitter: {e}")
