from django.core.management.base import BaseCommand
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Updater, CommandHandler, CallbackContext
import os

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MINI_APP_URL = 'https://app.zefe.xyz'

class Command(BaseCommand):
    help = 'Run Telegram Bot'

    def handle(self, *args, **kwargs):
        updater = Updater(TOKEN, use_context=True)
        dispatcher = updater.dispatcher

        def start(update: Update, context: CallbackContext) -> None:
            args = context.args  # payloads after /start
            payload = args[0] if args else None

            button_url = MINI_APP_URL
            if payload:
                button_url += f"?start={payload}"

            keyboard = [
                [InlineKeyboardButton("🚀 Open Zefe Mini App", web_app=WebAppInfo(url=button_url))]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            update.message.reply_text('Welcome! 👋 Click below to open the zefe app:', reply_markup=reply_markup)

        # Register the /start handler
        dispatcher.add_handler(CommandHandler("start", start))

        self.stdout.write(self.style.SUCCESS('Bot is running...'))
        updater.start_polling()
        updater.idle()
