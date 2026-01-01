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


import asyncio
from pyrogram import filters
from pyrogram.errors import FloodWait
from bot import Bot
from config import ADMINS
from database.videos import add_video, count

indexing = False
cancel_flag = False

@Bot.on_message(filters.command("index") & filters.user(ADMINS),group=898989)
async def index_cmd(client, msg):
    global indexing, cancel_flag

    if indexing:
        await msg.reply("⚠ Index already running\nUse /cancel to stop")
        return

    indexing = True
    cancel_flag = False

    # Ask admin to forward last message
    last = await client.ask(
        msg.chat.id,
        "📤 Forward me the *last message* of the channel (with quotes, not as copy)",
        timeout=120
    )

    try:
        last_id = last.forward_from_message_id
        chat = last.forward_from_chat.id if last.forward_from_chat.id else last.forward_from_chat.username
        await client.get_messages(chat, last_id)
    except:
        indexing = False
        await msg.reply("❌ Invalid forward. Try again.")
        return

    status = await client.send_message(msg.from_user.id, "🔎 Starting index…")

    current = 1
    total = last_id
    added = 0
    scanned = 0

    while current <= total:
        if cancel_flag:
            break

        try:
            m = await client.get_messages(chat, current)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            continue
        except:
            current += 1
            continue

        scanned += 1

        if m and m.video and m.caption:
            code = m.caption.strip().upper()
            if add_video(code, m.video.file_id, m.id):
                added += 1

        if current % 20 == 0:
            await status.edit(
                f"🔎 Indexing…\n\n"
                f"📥 Scanned: {current}/{total}\n"
                f"➕ Added: {added}\n"
                f"📦 In DB: {count()}\n\n"
                f"Use /cancel to stop"
            )

        current += 1

    if cancel_flag:
        await status.edit(
            f"⛔ Index cancelled\n\n"
            f"📥 Scanned: {current}/{total}\n"
            f"➕ Added: {added}\n"
            f"📦 In DB: {count()}"
        )
    else:
        await status.edit(
            f"✅ Index complete\n\n"
            f"📥 Scanned: {total}/{total}\n"
            f"➕ Added: {added}\n"
            f"📦 In DB: {count()}"
        )

    cancel_flag = False
    indexing = False


@Bot.on_message(filters.command("cancel") & filters.user(ADMINS),group=898989)
async def cancel_cmd(_, msg):
    global cancel_flag, indexing

    if not indexing:
        await msg.reply("ℹ No index running")
        return

    cancel_flag = True
    indexing = False
    await msg.reply("⛔ Cancelled")


