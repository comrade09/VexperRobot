

#(©)Codexbotz

import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from helper_func import subscribed, encode, decode, get_messages
from pyrogram import __version__
from config import OWNER_ID, BOT_USERNM


@Bot.on_callback_query(group=467)
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "help_test":
        await query.message.edit_text(
            text = f'''https://t.me/+0W7D1eJNgWAxYWY1''',
            
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Back", callback_data = "help_cb")
                    ]
                ]
            )
        )
        
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
