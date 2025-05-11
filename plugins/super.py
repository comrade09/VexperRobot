import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from helper_func import subscribed, encode, decode, get_messages
from pyrogram import __version__
from config import OWNER_ID, BOT_USERNM


@Bot.on_callback_query(group=260)
async def six(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "help_six":
        await query.message.edit_text(
            text = f''' Select your educator ''',
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                       InlineKeyboardButton("AG Sir ", callback_data= "super_ag"),
                       InlineKeyboardButton("Ysy Sir", callback_data= "super_ysy"),
                   ],
                    [
                       InlineKeyboardButton("Skc Sir ", callback_data= "super_skc"),
                       InlineKeyboardButton("Akm Sir", callback_data= "super_akm"),
                   ],
                   [
                       InlineKeyboardButton("Dr AG Sir", callback_data= "super_dr"),
                       InlineKeyboardButton("RS sir", callback_data= "super_rs"),
                   ],
                   [
                       InlineKeyboardButton("PJ Sir ", callback_data= "super_pj"),
                       InlineKeyboardButton("SN Sir", callback_data= "super_sn"),
                   ],
                   [
                       InlineKeyboardButton("Back", callback_data= "help_cb"),
                   ],
                ]  
            )
        )
    elif data == "super_skc":
     await query.message.edit_text(
     text = f''' 🌱 Welcome  
🔮 Notes  <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTY5NzkxODI0OTE4NDY1Nw">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 
🔮 Module Discussions  <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTIyOTkwMjQ4MjA4NDM1NzY">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 
   
     ''',
     disable_web_page_preview = True,
     reply_markup = InlineKeyboardMarkup(
                [
                   [
                       InlineKeyboardButton("Back", callback_data= "help_six"),
                   ],
                ]
            )
        
),
    elif data == "super_sn":
     await query.message.edit_text(
     text = f''' 🌱 Welcome  
🔮 Notes  write /notes to get notes  
    
     ''',
     disable_web_page_preview = True,
     reply_markup = InlineKeyboardMarkup(
                [
                   [
                       InlineKeyboardButton("Back", callback_data= "help_six"),
                   ],
                ]
            )
        
),
    
    
    elif data == "super_akm":
     await query.message.edit_text(
     text = f'''🌱 Welcome 

🔮Notes  :- hit /notes in this bot

🔮Jstar Points <a href="https://t.me/{BOT_USERNM}t?start=Z2V0LTIyNzI5OTA1Njc2NDU4NzAtMjI4NzAwOTAxMTY3NTQwNA">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Dpp/Modules  <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTU3Njc1ODg0MDA3MjI1Ng">ᴄʟɪᴄᴋ ʜᴇʀᴇ  </a>

🔮 PYQ JSTAR SERIES LINKS <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTI0MjIxODY4NjQ4MTczMzk">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮 Module Disscusion Class 11th  <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTIyOTEwMTQyODEzOTgxMjgtMjI5NTAxOTU1MTEyMDg1Mg">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Module Disscusion Class 12th  <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTIyOTYwMjA4Njg1NTE1MzMtMjI5ODAyMzUwMzQxMjg5NQ">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮 Merged Modules 

📡 Class 11 <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTY5NTkxNTYxNDMyMzI5NQ"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 
📡 Class 12 <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTY5NjkxNjkzMTc1Mzk3Ng"> ᴄʟɪᴄᴋ ʜᴇʀᴇ   </a>


       ''',
     disable_web_page_preview = True,
      reply_markup = InlineKeyboardMarkup(
                [
                   [
                       InlineKeyboardButton("Back", callback_data= "help_six"),
                   ],
                ]
            )
        
),
    elif data == "super_dr":
     await query.message.edit_text(
     text = f'''  🌱 Welcome 
🔮Notes  :- hit /notes in this bot
🔮Modules <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTIwODU3NDQyMDgxMDg1MjM">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮Expected Question  <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTIyNzE5ODkyNTAyMTUxODk">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>



 ''',
     disable_web_page_preview = True,
          reply_markup = InlineKeyboardMarkup(
                [
                   [
                       InlineKeyboardButton("Back", callback_data= "help_six"),
                   ],
                ]
            )    
),
    elif data == "super_rs":
     await query.message.edit_text(
     text = f''' 🔮 Handwritten Notes <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTIzMDAwMjYxMzgyNzQyNTc">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 
🔮 Modules Class 11th  <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTIzMDQwMzE0MDc5OTY5ODE">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 
🔮 Modules Class 12th  <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTIzMDUwMzI3MjU0Mjc2NjI">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 
     
     ''',
     disable_web_page_preview = True,
          reply_markup = InlineKeyboardMarkup(
                [
                   [
                       InlineKeyboardButton("Back", callback_data= "help_six"),
                   ],
                ]
            )
        
)
    elif data == "super_ag":
     await query.message.edit_text(
     text = f''' 🔮Handouts : <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTIxMjI3OTI5NTMwNDM3MjAtMjE0MjgxOTMwMTY1NzM0MA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> ''',
     disable_web_page_preview = True,
          reply_markup = InlineKeyboardMarkup(
                [
                   [
                       InlineKeyboardButton("Back", callback_data= "help_six"),
                   ],
                ]
            )
        
)        

    elif data == "super_pj":
     await query.message.edit_text(
     text = f'''🌱 Welcome 

🔮Notes  :- hit /notes in this bot

🔮 Merged Modules 
📡 Class 11 <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTY5ODkxOTU2NjYxNTMzOA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 
📡 Class 12 <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTY5OTkyMDg4NDA0NjAxOQ"> ᴄʟɪᴄᴋ ʜᴇʀᴇ   </a>

🔮Physicaholics Points <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTIzMDEwMjc0NTU3MDQ5Mzg">   ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>   

🔮Physicaholics Bot <a href="https://t.me/physicsaholicsbot">   ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>   ''',
     disable_web_page_preview = True,
       reply_markup = InlineKeyboardMarkup(
                [ 
                   [
                       InlineKeyboardButton("🔮Dpp Class 11", callback_data= "dpp_11"),
                       InlineKeyboardButton("🔮Dpp Class 12", callback_data= "dpp_12"),
                   ],
                   [
                       InlineKeyboardButton("🔮Modules Class 11", callback_data= "pj_mod_11"),
                       InlineKeyboardButton("🔮Modules Class 12", callback_data= "pj_mod_12"),
                   ],
                   [
                       InlineKeyboardButton("Back", callback_data= "help_six"),
                   ],
                ]
            )
)
    elif data == "super_ysy":
     await query.message.edit_text(
     text = f''' 🔮Handouts : <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTIyNzA5ODc5MzI3ODQ1MDg"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮GOC 2 NOTES : <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTIyNzA5ODc5MzI3ODQ1MDg"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 
     ''',
     disable_web_page_preview = True,
          reply_markup = InlineKeyboardMarkup(
                [
                   [
                       InlineKeyboardButton("Back", callback_data= "help_six"),
                   ],
                ]
            )
        
)         

    
 
 
 
 
