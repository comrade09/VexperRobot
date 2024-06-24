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


@Bot.on_callback_query(group=2747746)
async def nots_cb(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "help_mod4":
        await query.message.reply_photo( photo,
            caption = f'''🏮 Modules 4.0 ''',
            
            reply_markup = InlineKeyboardMarkup(
                [
                   [
                        InlineKeyboardButton("PHY 11", url= "https://t.me/Voltaic_Robot?start=Z2V0LTIxMDI3NjY2MDQ0MzAxMDA"),
                        InlineKeyboardButton("PHY 12", url= "https://t.me/Voltaic_Robot?start=Z2V0LTIxMDQ3NjkyMzkyOTE0NjI"),
                   ],
                   [
                        InlineKeyboardButton("BIO 11", url= "https://t.me/Voltaic_Robot?start=Z2V0LTIxMDM3Njc5MjE4NjA3ODE"),
                       InlineKeyboardButton("BIO 12", url= "https://t.me/Voltaic_Robot?start=Z2V0LTIxMDE3NjUyODY5OTk0MTk"),
                   ],
                    [
                        InlineKeyboardButton("PHY CHEM", url= "https://t.me/Voltaic_Robot?start=Z2V0LTIxMDY3NzE4NzQxNTI4MjQ"),
                        InlineKeyboardButton("OC", url= "https://t.me/Voltaic_Robot?start=Z2V0LTIxMDU3NzA1NTY3MjIxNDM"),
                        InlineKeyboardButton("IOC", callback_data= "ioc4"),
                   ],
                   [
                        InlineKeyboardButton("Back", callback_data= "help_mod"),
                   ],
                ]
            )
        )
        
    elif data == "ioc4":
        try:
            await query.answer("Not Available at this moment ", show_alert=True)
        except:
            pass          
    
