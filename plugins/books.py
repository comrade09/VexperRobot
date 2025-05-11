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
    if data == "first_books":
        await query.message.edit_text(
            text = f''' 📖 **1st Year Books:** Choose a subject below.
    ''',
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Anatomy", callback_data="book_anatomy"),
                        InlineKeyboardButton("Biochemistry", callback_data="book_biochem"),
                    ],
                    [
                        InlineKeyboardButton("Physiology", callback_data="book_physiology"),
                        InlineKeyboardButton("Back", callback_data= "help_cb"),
                    ],
                ]
            )
        )
