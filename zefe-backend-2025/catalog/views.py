from django.shortcuts import render
from rest_framework import generics
from .serializers import FileUploadSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from core import boto3
import json
from django.http import JsonResponse
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes
from .bot import bot  # Assume your bot instance is in bot.py
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
import requests
from core.renderers import DISCORD_WEBHOOK_URL
from django.views.decorators.csrf import csrf_exempt
from .telegram_bot.handlers import send_intro_message_with_buttons, more_about_zefe_callback_manual
import asyncio

# Create your views here.
class UploadImageView(generics.CreateAPIView):
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = FileUploadSerializer


@csrf_exempt
def telegram_webhook(request):
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        update = Update.de_json(data, bot)

        user = update.effective_user
        message = update.effective_message
        callback_query = update.callback_query  # <--- Add this line

        payload = {
            "content": f"🚨 New Telegram Update\n"
                       f"User: {user.full_name} (@{user.username})\n"
                       f"Message: {message.text if message else ''}\n"
                       f"CallbackData: {callback_query.data if callback_query else ''}"
        }

        try:
            requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
        except Exception as e:
            print(f"⚠️ Failed to send to Discord: {e}")

        try:
            loop = None
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            if message and message.text and message.text.startswith('/start'):
                chat_id = update.effective_chat.id
                loop.run_until_complete(send_intro_message_with_buttons(chat_id))

            elif callback_query and callback_query.data == "more_about_zefe":
                chat_id = callback_query.message.chat.id
                loop.run_until_complete(more_about_zefe_callback_manual(chat_id))

        except Exception as e:
            print(f"⚠️ Failed to process Telegram event: {e}")

    return JsonResponse({"ok": True})
