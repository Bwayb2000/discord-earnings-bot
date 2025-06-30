import requests
import feedparser
from datetime import datetime, timedelta
import pytz
import os

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
RSS_FEED = 'https://www.marketbeat.com/earnings/upcoming.rss'

SECTOR_EMOJIS = {
    'Technology': '💻',
    'Healthcare': '💊',
    'Financial': '💰',
    'Energy': '⚡',
    'Consumer': '🛒',
    'Industrial': '🏭'
}

def fetch_earnings():
    feed = feedparser.parse(RSS_FEED)
    earnings_by_day = {}

    today = datetime.now(pytz.timezone('US/Eastern'))
    start = today
    end = today + timedelta(days=6)

    print(f"🔎 Checking earnings from {start.date()} to {end.date()}")
    print(f"📰 Entries found in feed: {len(feed.entries)}")

    for entry in feed.entries:
        pub_date = datetime(*entry.published_parsed[:6], tzinfo=pytz.utc).astimezone(pytz.timezone('US/Eastern'))
        print(f"📅 Entry date: {pub_date.date()} | Title: {entry.title}")

        if start.date() <= pub_date.date() <= end.date():
            date_str = pub_date.strftime('%A %b %d')
            title = entry.title
            link = entry.link
            ticker = title.split('(')[-1].split(')')[0]
            sector = "Technology" if 'tech' in title.lower() else "Financial"
            emoji = SECTOR_EMOJIS.get(sector, '📈')
            if date_str not in earnings_by_day:
                earnings_by_day[date_str] = []
            earnings_by_day[date_str].append(f"{emoji} **{title}**\n<{link}>")
    return earnings_by_day

def format_message(earnings_by_day):
    if not earnings_by_day:
        return "📉 No earnings reports found for the upcoming week."
    message = "**📅 Upcoming Earnings Reports This Week:**\n"
    for day, reports in sorted(earnings_by_day.items()):
        message += f"\n__**{day}**__\n"
        for report in reports:
            message += f"- {report}\n"
    return message

def send_to_discord(message):
    data = {"content": message}
    response = requests.post(WEBHOOK_URL, json=data)
    if response.status_code != 204:
        print("❌ Failed to send message:", response.text)

if __name__ == "__main__":
    earnings = fetch_earnings()
    msg = format_message(earnings)
    print(f"\n✅ Final message preview:\n{msg}")
    send_to_discord(msg)
