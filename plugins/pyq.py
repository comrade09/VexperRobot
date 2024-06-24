import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from helper_func import subscribed, encode, decode, get_messages
from pyrogram import __version__
from config import OWNER_ID, BOT_USERNM


@Bot.on_callback_query(group=268)
async def nots_cb(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "help_pyq":
        await query.message.edit_text(
            text = f'''🏮 NEET PREVIOUS YEAR PAPERS 

🎐NEET 2006 <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTYwMjc5MzA5MzI2OTk2Mg"> Click Here </a>
🎐NEET 2007 <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTYwMzc5NDQxMDcwMDY0Mw"> Click Here </a>
🎐NEET 2008 <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTYwNDc5NTcyODEzMTMyNA"> Click Here </a>
🎐NEET 2009 <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTYxMDgwMzYzMjcxNTQxMA"> Click Here </a>
🎐NEET 2010 <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTYxNzgxMjg1NDczMDE3Nw"> Click Here </a>
🎐NEET 2011 <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTYxNjgxMTUzNzI5OTQ5Ng"> Click Here </a>
🎐NEET 2012 <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTYwNTc5NzA0NTU2MjAwNQ"> Click Here </a>
🎐NEET 2013 <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTYxNTgxMDIxOTg2ODgxNQ"> Click Here </a>
🎐NEET 2014 <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTYxMjgwNjI2NzU3Njc3Mg"> Click Here </a>
🎐NEET 2015 <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTYxNDgwODkwMjQzODEzNA"> Click Here </a>
🎐NEET 2016 <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTYwNzc5OTY4MDQyMzM2Nw"> Click Here </a>
🎐NEET 2017 <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTYwOTgwMjMxNTI4NDcyOQ"> Click Here </a> 
🎐NEET 2018 <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTYxMzgwNzU4NTAwNzQ1Mw"> Click Here </a>
🎐NEET 2019 <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTYxOTgxNTQ4OTU5MTUzOQ"> Click Here </a>
🎐NEET 2020 <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTYxMTgwNDk1MDE0NjA5MQ"> Click Here </a>
🎐NEET 2021 <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTYwNjc5ODM2Mjk5MjY4Ng"> Click Here </a>
🎐NEET 2022 <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTYwODgwMDk5Nzg1NDA0OA"> Click Here </a>
🎐NEET 2023 <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTYxODgxNDE3MjE2MDg1OA"> Click Here </a>
            ''',
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Chapterwise PYQ", callback_data= "pyq_ch"),
                        InlineKeyboardButton("Back", callback_data= "help_cb"),
                   ],
                ]
            )
        )
    elif data == "pyq_ch":
     await query.message.edit_text(
     text = f''' 🧧 Chapterwise Pyq 
     
    <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTcyMTk0OTg2NzUyMTAwMQ" >🔮BIOLOGY </a>
    
    <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTcyMDk0ODU1MDA5MDMyMA" >🔮CHEMISTRY  </a>
    
    <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTcyMzk1MjUwMjM4MjM2Mw">🔮PHYSICS  </a>
     ''',
     disable_web_page_preview = True,
     reply_markup = InlineKeyboardMarkup(
                [     
                   [
                       InlineKeyboardButton("Back", callback_data= "help_pyq"),
                   ],
                ]
            )
     )
