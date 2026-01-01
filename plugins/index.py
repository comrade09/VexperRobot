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



import threading, asyncio, time
from telethon import TelegramClient
from pyrogram import filters
from bot import Bot
from database.videos import add_video, count

indexing = False
cancel_flag = False

def run_index(client, admin_id, status_msg_id):
    async def worker():
        global indexing, cancel_flag

        user = TelegramClient("user", APP_ID, API_HASH)
        await user.start()

        total = (await user.get_messages(CHANNEL_ID, limit=0)).total

        scanned = 0
        added = 0
        last_update = time.time()

        async for m in user.iter_messages(CHANNEL_ID):
            if cancel_flag:
                break

            scanned += 1

            if m.video and m.text:
                code = m.text.strip().upper()
                if add_video(code, m.video.file_id, m.id):
                    added += 1

            if time.time() - last_update >= 5:
                remaining = total - scanned
                client.loop.call_soon_threadsafe(
                    asyncio.create_task,
                    client.edit_message_text(
                        chat_id=admin_id,
                        message_id=status_msg_id,
                        text=(
                            f"🔎 Indexing…\n\n"
                            f"📥 Scanned: {scanned} / {total}\n"
                            f"⏳ Remaining: {remaining}\n"
                            f"➕ Added: {added}\n"
                            f"📦 In DB: {count()}\n\n"
                            f"Use /cancel to stop"
                        )
                    )
                )
                last_update = time.time()

        if cancel_flag:
            text = (
                f"⛔ Index cancelled\n\n"
                f"📥 Scanned: {scanned} / {total}\n"
                f"➕ Added: {added}\n"
                f"📦 In DB: {count()}"
            )
        else:
            text = (
                f"✅ Index complete\n\n"
                f"📥 Scanned: {scanned} / {total}\n"
                f"➕ Added: {added}\n"
                f"📦 In DB: {count()}"
            )

        client.loop.call_soon_threadsafe(
            asyncio.create_task,
            client.edit_message_text(
                chat_id=admin_id,
                message_id=status_msg_id,
                text=text
            )
        )

        cancel_flag = False
        indexing = False

    asyncio.run(worker())

@Bot.on_message(filters.command("index"))
async def index_cmd(client, msg):
    global indexing, cancel_flag

    if msg.from_user.id not in ADMINS:
        await msg.reply("❌ Not allowed")
        return

    if indexing:
        await msg.reply("⚠ Index already running\nUse /cancel to stop")
        return

    indexing = True
    cancel_flag = False

    status = await client.send_message(msg.from_user.id, "🔄 Starting index…")

    threading.Thread(
        target=run_index,
        args=(client, msg.from_user.id, status.id),
        daemon=True
    ).start()

@Bot.on_message(filters.command("cancel"))
async def cancel_cmd(_, msg):
    global cancel_flag

    if msg.from_user.id not in ADMINS:
        await msg.reply("❌ Not allowed")
        return

    if not indexing:
        await msg.reply("ℹ No index running")
        return

    cancel_flag = True
    await msg.reply("⛔ Cancel signal sent")
