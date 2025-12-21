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
            text='''📖<b> 2nd Year Lectures </b>: Choose a subject below.''',
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

<a href="https://t.me/{BOT_USERNM}?start=Z2V0LTI0NjUwNTYyOTc2MTg1NjAtMjUwNTEzODUxMzg0MDAwMA"><b>Dr Gobind Rai Garg ✘ Cerebellum Part 1</b></a><
<a href="https://t.me/{BOT_USERNM}?start=Z2V0LTI1MDYxNDA1NjkyNDU1MzYtMjU0NTIyMDczMDA2MTQ0MA"><b>Dr Gobind Rai Garg ✘ Cerebellum Part 2</b></a>

<a href="https://t.me/{BOT_USERNM}?start=Z2V0LTI1NDYyMjI3ODU0NjY5NzYtMjU5NTMyMzUwMDMzODI0MA"><b>Dr Gobind Rai Garg ✘ PrepLadder Part 1</b></a>
<a href="https://t.me/{BOT_USERNM}?start=Z2V0LTI1OTYzMjU1NTU3NDM3NzYtMjYzOTQxMzkzODE4MTgyNA"><b>Dr Gobind Rai Garg ✘ PrepLadder Part 2</b></a>

''',
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=False,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="second_lectures")]]
            )
        )

    elif data == "lec_Microbiology":
        await query.message.edit_text(
            text=f'''<b>Microbiology Lectures</b>:

<a href="https://t.me/{BOT_USERNM}?start=Z2V0LTIxNjU0NDE3MzEzNjMyOTYtMjIxNjU0NjU1NzA0NTYzMg"><b>Dr. Preeti Sharma ✘ PrepLadder Version X</b></a>
<a href="https://t.me/{BOT_USERNM}?start=Z2V0LTI2NDA0MTU5OTM1ODczNjAtMjY4OTUxNjcwODQ1ODYyNA"><b>Dr. Preeti Sharma ✘ Prepladder old</b></a>


''',
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=False,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="second_lectures")]]
            )
        )

    elif data == "lec_Pathology":
        await query.message.edit_text(
            text=f''' **Pathology Lectures**:
            
<a href="https://t.me/{BOT_USERNM}?start=Z2V0LTI2NDA0MTU5OTM1ODczNjAtMjY4OTUxNjcwODQ1ODYyNA"><b>Dr. Preeti Sharma ✘ Prepladder old</b></a>

<a href="https://t.me/{BOT_USERNM}?start=Z2V0LTIyMjA1NTQ3Nzg2Njc3NzYtMjI2MDYzNjk5NDg4OTIxNg"><b>Priyanka Sachdeva ✘ Medlive Part 1</b></a>
<a href="https://t.me/{BOT_USERNM}?start=Z2V0LTIyNjE2MzkwNTAyOTQ3NTItMjMxMTc0MTgyMDU3MTU1Mg"><b>Priyanka Sachdeva ✘ Medlive Part 2</b></a>
<a href="https://t.me/{BOT_USERNM}?start=Z2V0LTIzMTI3NDM4NzU5NzcwODgtMjM2Mjg0NjY0NjI1Mzg4OA"><b>Priyanka Sachdeva ✘ Medlive Part 3</b></a>
<a href="https://t.me/{BOT_USERNM}?start=Z2V0LTIzNjM4NDg3MDE2NTk0MjQtMjQxMjk0OTQxNjUzMDY4OA"><b>Priyanka Sachdeva ✘ Medlive Part 4</b></a>
<a href="https://t.me/{BOT_USERNM}?start=Z2V0LTI0MTM5NTE0NzE5MzYyMjQtMjQ2MzA1MjE4NjgwNzQ4OA"><b>Priyanka Sachdeva ✘ Medlive Part 5</b></a>





''',
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔙 Back", callback_data="second_lectures")]]
            )
        )
