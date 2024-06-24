import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from helper_func import subscribed, encode, decode, get_messages
from pyrogram import __version__
from config import OWNER_ID, BOT_USERNM

photo = "https://telegra.ph/file/4af76bb84c73cfe86f332.jpg"


@Bot.on_callback_query(group=26566)
async def nots_cb(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "help_mod":
        await query.message.reply_photo( photo,
            caption = f'''🏮Select From below Buttons ''',
            
            reply_markup = InlineKeyboardMarkup(
                [
                   [
                        InlineKeyboardButton("Module 3.0", callback_data= "help_mod3"),
                        InlineKeyboardButton("Module 4.0", callback_data= "help_mod4"),
 
                   ],
                   [
                        InlineKeyboardButton("Back", callback_data= "help_cb"),
                   ],
                ]
            )
        )
          
