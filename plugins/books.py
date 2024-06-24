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
            text = f''' BOOKS
    <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTcxMzkzOTMyODA3NTU1Mw">  🌱TRUEMAN VOL 1</a>
    <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTcxNDk0MDY0NTUwNjIzNA">  🌱TRUEMAN VOL 2  </a>
    <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTcxNzk0NDU5Nzc5ODI3Nw">  🌱HCV 1 </a>
    <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTcxOTk0NzIzMjY1OTYzOQ">  🌱HCV 2 </a>
    <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTcxODk0NTkxNTIyODk1OA">  🌱HCV SOLUTIONS </a>
    <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTcxNTk0MTk2MjkzNjkxNQ">  🌱DC PANDEY 1</a>
    <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTcxNjk0MzI4MDM2NzU5Ng">  🌱DC PANDEY 2 </a> 
    <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTcyMjk1MTE4NDk1MTY4Mg">  🌱MTG PHYSICS FINGERTIPS </a> 
    <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTcyNTk1NTEzNzI0MzcyNQ">  🌱MTG BIOLOGY FINGERTIPS </a> 
    <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTcyNDk1MzgxOTgxMzA0NA">  🌱MTG CHEMISTRY FINGERTIPS </a>
    <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTczMDk2MTcyNDM5NzEzMA">  🌱NCERT NICHOD </a>''',
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                   [
                        InlineKeyboardButton("Back", callback_data= "help_cb"),
                   ],
                ]
            )
        )
