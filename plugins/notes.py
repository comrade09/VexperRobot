import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from helper_func import subscribed, encode, decode, get_messages
from pyrogram import __version__
from config import OWNER_ID, BOT_USERNM


@Bot.on_message(filters.command('notes') & filters.private, group=251)
async def help(bot: Bot, message: Message):
 buttons = [
        [
            InlineKeyboardButton("Physics", callback_data= "phy_nots"),
            InlineKeyboardButton("Physical ", callback_data= "pc_nots"),
            InlineKeyboardButton("Inorganic ",   callback_data= "ioc_nots")
        ],
        [
            
            InlineKeyboardButton("Organic ", callback_data= "org_nots"),
            InlineKeyboardButton("Zoology", callback_data= "zoo_nots"),
            InlineKeyboardButton("Botany", callback_data= "bot_nots"),
        ],
        [
           InlineKeyboardButton("Back", callback_data= "help_cb"),
        ],
    ]
 
 
 
 
 
 await message.reply_text( text = f'''Notes of Unacademy Plus classes merged  ''',
   reply_markup = InlineKeyboardMarkup(buttons),                       
   disable_web_page_preview = False
   )
 
@Bot.on_callback_query(group=256)
async def nots_cb(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "help_nots":
        await query.message.edit_text(
            text = f'''Notes of Unacademy Plus classes merged ''',
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                   [
                        InlineKeyboardButton("Physics", callback_data= "phy_nots"),
                        InlineKeyboardButton("Physical ", callback_data= "pc_nots"),
                        InlineKeyboardButton("Inorganic ",   callback_data= "ioc_nots")
                   ],
                   [            
                       InlineKeyboardButton("Organic ", callback_data= "org_nots"),
                       InlineKeyboardButton("Zoology", callback_data= "zoo_nots"),
                       InlineKeyboardButton("Botany", callback_data= "bot_nots"),
                  ],
                  [
                       InlineKeyboardButton("Back", callback_data= "help_cb"),
                 ],
    
  
                ]
            )
        )
 
 
 
 

    
 
 
 
 

