from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from telegram.ext import ContextTypes
import asyncio
from ..bot import bot  # Assume your bot instance is in bot.py
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import CallbackContext


async def more_about_zefe_callback_manual(chat_id):
    await bot.send_message(
        chat_id=chat_id,
        text=(
            "🔵 *More about ZEFE*\n\n"
            "When you attend major events like Token2049, you meet hundreds of people. Your Telegram quickly floods with DMs, making it overwhelming to sort through messages or track important new connections.\n\n"
            "With *ZEFE*, you don’t have to worry about that.\n"
            "Instead of sharing your Telegram QR, simply share your ZEFE QR. With one scan, ZEFE instantly captures and organizes key details like names, affiliations, roles, social handles, notes, and even prompts you to take selfies (because we all take selfies at these events).\n\n"
            "No app downloads. No sign-ups.\n"
            "*Just open the ZEFE mini-app and start networking.*\n\n"
            "And don’t worry, the people you meet don’t need to have a ZEFE account beforehand.\n\n"
            "When they scan your QR, they’re onboarded in seconds. no setup required. no friction.\n\n"
            "🔗 [Follow us on X](https://x.com/ZEFExyz)\n"
            "📬 DM for collabs: @founderAZIAN"
        ),
        parse_mode="Markdown"
    )



async def send_intro_message_with_buttons(chat_id):
    intro_text = (
        "👋 Welcome to ZEFE\n\n"
        "ZEFE is a Telegram mini-app that helps you save, manage and filter your crypto event connections, making post-event follow-ups effortless and effective.\n\n"
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Start Networking",
                    web_app=WebAppInfo(url="https://app.zefe.xyz"),
                )
            ],
            [
                InlineKeyboardButton(
                    text="Join the ZEFE journey on X", url="https://x.com/zefexyz"
                )
            ],
            [
                InlineKeyboardButton(
                    text="More about ZEFE",
                    callback_data="more_about_zefe",  # <-- ici on utilise callback_data
                )
            ],
        ]
    )

    await bot.send_message(
        chat_id=chat_id, text=intro_text, parse_mode="Markdown", reply_markup=keyboard
    )
