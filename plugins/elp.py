import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from helper_func import subscribed, encode, decode, get_messages
from pyrogram import __version__
from config import OWNER_ID, BOT_USERNM




@Bot.on_callback_query(group=270)
async def elp_cb(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "year_1":
        
            text = """Choose what you want """,
            reply_markup=InlineKeyboardMarkup(
                [
        [
            InlineKeyboardButton("Lectures", callback_data="first_lectures"),
            InlineKeyboardButton("Books", callback_data="first_books")
        ],
        [
            InlineKeyboardButton("Notes", callback_data="first_notes"),
            InlineKeyboardButton("Random Stuff", callback_data="first_random")
        ],
        [
            InlineKeyboardButton("Back", callback_data="help_cb"),
            InlineKeyboardButton("✗", callback_data="close"),
        ],            
        
        ]
    ),
    parse_mode=ParseMode.MARKDOWN,        
    )
 
elif data == "first_books":
        await query.message.edit_text(
            text="📖 **1st Year Books:** Choose a subject below.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Anatomy", callback_data="book_anatomy"),
                        InlineKeyboardButton("Biochemistry", callback_data="book_biochem"),
                    ],
                    [
                        InlineKeyboardButton("Physiology", callback_data="book_physiology"),
                        InlineKeyboardButton("🔙 Back", callback_data="year_1"),
                    ]
                ]
            )
        )            
