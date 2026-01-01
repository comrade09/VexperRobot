from telethon import TelegramClient
from pyrogram import filters
from bot import Bot
from config import APP_ID, API_HASH, CHANNEL_ID, ADMINS
from database.videos import add_video, count
import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from helper_func import subscribed, encode, decode, get_messages
from pyrogram import __version__
from config import OWNER_ID,BOT_USERNM
from pyrogram.enums import ParseMode

import threading, asyncio
from telethon import TelegramClient
from pyrogram import filters
from bot import Bot

from database.videos import add_video, count

indexing = False
cancel_flag = False

def run_index(status_chat_id, status_msg_id):
    async def worker():
        global indexing, cancel_flag
        user = TelegramClient("user", APP_ID, API_HASH)
        await user.start()

        scanned = 0
        added = 0

        async for m in user.iter_messages(CHANNEL_ID):
            if cancel_flag:
                break

            scanned += 1

            if m.video and m.text:
                code = m.text.strip().upper()
                if add_video(code, m.video.file_id, m.id):
                    added += 1

            if scanned % 25 == 0:
                Bot.loop.call_soon_threadsafe(
                    asyncio.create_task,
                    Bot.edit_message_text(
                        chat_id=status_chat_id,
                        message_id=status_msg_id,
                        text=(
                            f"🔎 Indexing...\n"
                            f"📥 {scanned}\n"
                            f"➕ {added}\n"
                            f"📦 {count()}\n\n"
                            f"Use /cancel to stop"
                        )
                    )
                )

        if cancel_flag:
            Bot.loop.call_soon_threadsafe(
                asyncio.create_task,
                Bot.edit_message_text(
                    chat_id=status_chat_id,
                    message_id=status_msg_id,
                    text=(
                        f"⛔ Index cancelled\n\n"
                        f"📥 {scanned}\n"
                        f"➕ {added}\n"
                        f"📦 {count()}"
                    )
                )
            )
        else:
            Bot.loop.call_soon_threadsafe(
                asyncio.create_task,
                Bot.edit_message_text(
                    chat_id=status_chat_id,
                    message_id=status_msg_id,
                    text=(
                        f"✅ Index complete\n\n"
                        f"📥 {scanned}\n"
                        f"➕ {added}\n"
                        f"📦 {count()}"
                    )
                )
            )

        cancel_flag = False
        indexing = False

    asyncio.run(worker())

@Bot.on_message(filters.command("index"))
async def index_cmd(_, msg):
    global indexing, cancel_flag

    if msg.from_user.id not in ADMINS:
        await msg.reply("❌ Not allowed")
        return

    if indexing:
        await msg.reply("⚠ Index already running\nUse /cancel to stop")
        return

    indexing = True
    cancel_flag = False

    status = await msg.reply("🔄 Starting index...")
    threading.Thread(
        target=run_index,
        args=(status.chat.id, status.id),
        daemon=True
    ).start()

@Bot.on_message(filters.command("cancel"))
async def cancel_cmd(_, msg):
    global cancel_flag

    if msg.from_user.id not in ADMINS:
        await msg.reply("❌ Not allowed")
        return

    if not indexing:
        await msg.reply("ℹ No index is running")
        return

    cancel_flag = True
    await msg.reply("⛔ Cancel signal sent. Stopping…")
