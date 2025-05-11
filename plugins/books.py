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
            text='''📖 **1st Year Books:** Choose a subject below.''',
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Anatomy", callback_data="book_anatomy"),
                        InlineKeyboardButton("Biochemistry", callback_data="book_biochem"),
                    ],
                    [
                        InlineKeyboardButton("Physiology", callback_data="book_physiology"),
                        InlineKeyboardButton("Back", callback_data="help_cb"),
                    ],
                ]
            )
        )

    elif data == "book_anatomy":
        await query.message.edit_text(
            text='''🧠 **Anatomy Books**:

1. [BD Chaurasia Vol 1](https://example.com/bd-chaurasia-1)
2. [BD Chaurasia Vol 2](https://example.com/bd-chaurasia-2)
3. [Gray's Anatomy for Students](https://example.com/grays-anatomy)
4. [Vishram Singh – Neuroanatomy](https://example.com/vishram-neuro)

📚 Tap on any book title to download or view.''',
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="first_books")]]
            )
        )

    elif data == "book_biochem":
        await query.message.edit_text(
            text='''🧪 **Biochemistry Books**:

1. [Lippincott's Illustrated Biochemistry](https://example.com/lippincott-biochem)
2. [Harper's Illustrated Biochemistry](https://example.com/harper-biochem)
3. [Satyanarayana Biochemistry](https://example.com/satyanarayana)

🔬 Essential for understanding metabolic pathways and clinical biochemistry.''',
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="first_books")]]
            )
        )

    elif data == "book_physiology":
        await query.message.edit_text(
            text='''❤️ **Physiology Books**:

1. [Guyton and Hall Textbook of Medical Physiology](https://example.com/guyton)
2. [Ganong's Review of Medical Physiology](https://example.com/ganong)
3. [Sembulingam – Essentials of Medical Physiology](https://example.com/sembulingam)

🫀 These are key books for mastering body functions and systems.''',
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="first_books")]]
            )
        )
