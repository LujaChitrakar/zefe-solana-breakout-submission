from telegram import Bot
import os

# Your Telegram Bot Token
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Create a global bot instance
bot = Bot(token=TOKEN)
