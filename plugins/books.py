import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from helper_func import subscribed, encode, decode, get_messages
from pyrogram import __version__
from config import OWNER_ID, BOT_USERNM


@Bot.on_callback_query(group=274)
async def book_cb(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "help_books":
        await query.message.edit_text(
            text = f''' BOOKS SOON
    ''',
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                   [
                        InlineKeyboardButton("Back", callback_data= "help_cb"),
                   ],
                ]
            )
        )
