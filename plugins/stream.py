from pyrogram import filters
from bot import Bot
from database.videos import get_video
import time, hmac, hashlib, base64, urllib.parse
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

# 🔥 HARD-CODED (you asked for this)
WORKER_URL = "https://telegram-video-bridge.fusionfiner.workers.dev"
SECRET = "Xs93jdK3$kW9xPz_92kslPq"

def sign(file_id):
    exp = int(time.time() * 1000) + 15 * 60 * 1000   # 15 min expiry
    data = f"{file_id}|{exp}"
    sig = hmac.new(SECRET.encode(), data.encode(), hashlib.sha256).digest()
    sig = base64.b64encode(sig).decode()

    return (
        f"{WORKER_URL}"
        f"?id={urllib.parse.quote(str(file_id))}"
        f"&exp={exp}"
        f"&sig={urllib.parse.quote(sig)}"
    )

@Bot.on_message(filters.command("get"),group=656656)
async def get_cmd(_, msg):
    if len(msg.command) != 2:
        await msg.reply("Use: /get CC0056")
        return

    code = msg.command[1].upper()
    v = get_video(code)

    if not v:
        await msg.reply("❌ Code not found")
        return

    link = sign(v["file_id"])
    await msg.reply(f"🎬 {code}\n\n🔗 {link}")
