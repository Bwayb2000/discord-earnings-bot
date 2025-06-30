import requests
from datetime import datetime, timedelta
import pytz
import os
import re

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")
RSS_FEED = 'https://api.rss2json.com/v1/api.json?rss_url=https://www.marketbeat.com/earnings/upcoming.rss'

SECTOR_EMOJIS = {
    'Technology': '💻',
    'Healthcare': '💊',
    'Financial': '💰',
    'Energy': '⚡',
    'Consumer': '🛒',
    'Industrial': '🏭'
}

def extract_date_from_title(title):
    match = re.search(r'on (\w+ \d{1,2}, \d{4})', title)
    if match:
        try:
            return datetime.strptime(match.group(1), '%B %d, %Y').date()
        except ValueError:
            return None
    return None

def fetch_earnings():
    response = requests.get(RSS_FEED)
    data = response.json()
    earnings_by_day = {}

    today = datetime.now(pytz.timezone('US/Eastern')).date()
    end = today + timedelta(days=6)

    print(f"🔎 Checking earnings from {today} to {end}")
    print(f"📰 Entries found in feed: {len(data.get('items', []))}")

    for item in data.get("items", []):
        title = item.get("title", "")
        link = item.get("link", "")
        earnings_date = extract_date_from_title(title)

        if earnings_date:
            print(f"📅 Found entry: {earnings_date} | Title: {title}")
            if today <= earnings_date <= end:
                date_str = earnings_date.strftime('%A %b %d')
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