import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from helper_func import subscribed, encode, decode, get_messages
from pyrogram import __version__
from config import OWNER_ID, BOT_USERNM

ELP_PIC = "https://te.legra.ph/file/b9eaf31b3e53edf870ce0.jpg"


@Bot.on_callback_query(group=270)
async def elp_cb(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "help_elp":
        stik=await query.message.reply_sticker(sticker="CAACAgUAAxkBAAIM2WVuXSKjb5hD7Ira3MNtHkQvvfyLAALFEQACFORxV6azoG5YB84EHgQ")
        await asyncio.sleep(0.1)
        a =await query.message.reply_text("🌗L")
        await asyncio.sleep(0.1)
        z =await a.edit_text("🌘Lo")
        await asyncio.sleep(0.1)
        b= await z.edit_text("🌑Loa")
        await asyncio.sleep(0.1)
        c=await b.edit_text("🌒Load")
        await asyncio.sleep(0.1)
        d =await c.edit_text("🌓Loadi")
        await asyncio.sleep(0.1)
        e =await d.edit_text("🌔Loadin")
        await asyncio.sleep(0.1)
        f =await e.edit_text("🌕Loading")
        await asyncio.sleep(0.1)
        g =await f.edit_text("🌖Loading .")
        await asyncio.sleep(0.1)
        h =await g.edit_text("🌗Loading . .")
        await asyncio.sleep(0.1)
        i =await h.edit_text("🌘Loading . . .")
        await asyncio.sleep(0.1)
        await h.delete()
        await stik.delete()
        await query.message.reply_text("🌀Cremdits @Romlex69")
        await query.message.reply_photo(photo = ELP_PIC,
            caption = """🌀CHOOSE THE BATCH: """,
            reply_markup=InlineKeyboardMarkup(
                [
        [
            InlineKeyboardButton("Master Pro 1", callback_data="mp1_1"),
            InlineKeyboardButton("Master Pro 2", callback_data="mp2_1"),
        ],
        [
            InlineKeyboardButton("Growth", callback_data="growth_1"),
            InlineKeyboardButton("Elite", callback_data="elite_1"),
        ],
        [
            InlineKeyboardButton("Dream", callback_data="dream_1"),
            InlineKeyboardButton("CB 2", callback_data="cb2_1"),
        ],
        [
            InlineKeyboardButton("Early Excel", callback_data="earlyexcel_1"),
            InlineKeyboardButton("CC 3", callback_data="cc3_1"),
        ],
        [
            InlineKeyboardButton("CB 4", callback_data="cb4_1"),
            InlineKeyboardButton("CE 4", callback_data="ce4_1"),
        ],
        [
            InlineKeyboardButton("Conquer 1", callback_data="cq1_1"),
            InlineKeyboardButton("Conquer 2", callback_data="cq2_1"),
        ],
        [
            InlineKeyboardButton("Conquer 11", callback_data="cq11_1"),
            InlineKeyboardButton("Conquer 13", callback_data="cq13_1"),
        ],
        [
            InlineKeyboardButton("Conquer-3(Hindi)", callback_data="cq3_1"),
            InlineKeyboardButton("Conquer 9(Hindi)", callback_data="cq9_1"),
        ], 
        [
            InlineKeyboardButton("Back", callback_data="help_cb"),
            InlineKeyboardButton("✗", callback_data="close"),
        ],            
        
        ]
    ),
    parse_mode=ParseMode.MARKDOWN,        
    )
