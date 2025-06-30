# 📈 Discord Earnings Bot

Sends a weekly earnings report to your Discord channel every Sunday at 5PM EST using a webhook and MarketBeat RSS.

## 🚀 Setup

1. Add your Discord webhook to GitHub Secrets (or environment variable):
   - `DISCORD_WEBHOOK` = your webhook URL
2. Use GitHub Actions to run `main.py` every Sunday at 5PM EST.