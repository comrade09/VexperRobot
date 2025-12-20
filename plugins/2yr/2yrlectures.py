import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from helper_func import subscribed, encode, decode, get_messages
from pyrogram import __version__
from config import OWNER_ID, BOT_USERNM


@Bot.on_callback_query(group=2748787)
async def book_cb(client: Bot, query: CallbackQuery):
    data = query.data

    if data == "second_lectures":
        await query.message.edit_text(
            text='''📖 **2nd Year Lectures :** Choose a subject below.''',
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Pharmacology", callback_data="lec_Pharmacology"),
                        InlineKeyboardButton("Microbiology", callback_data="lec_Microbiology"),
                    ],
                    [
                        InlineKeyboardButton("Pathology", callback_data="lec_Pathology"),
                        InlineKeyboardButton("Back", callback_data="help_cb"),
                    ],
                ]
            )
        )

    elif data == "lec_Pharmacology":
        await query.message.edit_text(
            text=f'''Pharmacology Lectures

<a href="https://t.me/?start=Z2V0LTIxNjU0NDE3MzEzNjMyOTYtMjIxNjU0NjU1NzA0NTYzMg">Vishram Singh - General Anatomy.pdf</a><br>


📚 Tap on any book title to download or view.''',
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=False,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="first_books")]]
            )
        )

    elif data == "lec_Microbiology":
        await query.message.edit_text(
            text='''**Microbiology Lectures**:

<a href="https://t.me/{BOT_USERNM}?start=Z2V0LTIxNjU0NDE3MzEzNjMyOTYtMjIxNjU0NjU1NzA0NTYzMg"><b>Dr. Preeti Sharma ✘ PrepLadder Version X</b></a><br>

''',
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="first_books")]]
            )
        )

    elif data == "lec_Pathology":
        await query.message.edit_text(
            text=''' **Pathology Lectures**:

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
