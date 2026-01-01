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

from pyrogram import filters
from bot import Bot
from config import CHANNEL_ID
from database.videos import add_video

@Bot.on_message(filters.chat(CHANNEL_ID) & filters.video)
async def auto_index(_, msg):
    if not msg.caption:
        return

    code = msg.caption.strip().upper()
    if add_video(code, msg.video.file_id, msg.id):
        print("Auto indexed:", code)
