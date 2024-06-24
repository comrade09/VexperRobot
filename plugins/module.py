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


@Bot.on_callback_query(group=266)
async def nots_cb(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "help_mod3":
        await query.message.reply_photo( photo,
            caption = f'''🏮Select From below Buttons ''',
            
            reply_markup = InlineKeyboardMarkup(
                [
                   [
                        InlineKeyboardButton("Physics", callback_data= "mod_una_phy"),
                        InlineKeyboardButton("Chemisty", callback_data= "mod_un_chem"),
                        InlineKeyboardButton("Biology", callback_data= "mod_una_bio"),
                   ],
                   [
                        InlineKeyboardButton("Back", callback_data= "help_cb"),
                   ],
                ]
            )
        )
          
    elif data == "mod_una_phy":
     await query.message.edit_text(text = f''' 🏮PHYSICS MODULES 
     
🔮AC [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2NjYxOTIyMDQ2NTMxODQ)
🔮Bar Magnet  [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2NjcxOTM1MjIwODM4NjU)
🔮Capacitor[ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2NjgxOTQ4Mzk1MTQ1NDY)
🔮Basic Math [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2NjkxOTYxNTY5NDUyMjc)
🔮Modern Phy [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2NzAxOTc0NzQzNzU5MDg)
🔮Kinematics [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2NzExOTg3OTE4MDY1ODk)
🔮Mec [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2NzIyMDAxMDkyMzcyNzA)
🔮Magnetic Properties [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2NzMyMDE0MjY2Njc5NTE)
🔮Nlm [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2NzQyMDI3NDQwOTg2MzI)
🔮Nuclear Physics [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2NzUyMDQwNjE1MjkzMTM)
🔮Shm [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2NzYyMDUzNzg5NTk5OTQ)
🔮Rotation [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2NzcyMDY2OTYzOTA2NzU)
🔮Semiconductor [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2NzgyMDgwMTM4MjEzNTY)
🔮KTG [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2ODAyMTA2NDg2ODI3MTg)
🔮Thermodynamic [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2NzkyMDkzMzEyNTIwMzc)
🔮Surface tension [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2ODEyMTE5NjYxMTMzOTk)
🔮Thermodynaimcs [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2ODIyMTMyODM1NDQwODA)
🔮Heat transfer [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2ODQyMTU5MTg0MDU0NDI)
🔮Thermo metry [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2ODMyMTQ2MDA5NzQ3NjE)
🔮Thermal Expansion [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2ODUyMTcyMzU4MzYxMjM)
🔮Gravitation [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2ODYyMTg1NTMyNjY4MDQ)
🔮Emi [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2ODkyMjI1MDU1NTg4NDc)
🔮Fluid [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2ODgyMjExODgxMjgxNjY)
🔮Electrostatics [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2OTAyMjM4MjI5ODk1Mjg)
🔮Emw [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2ODcyMTk4NzA2OTc0ODU)
🔮Unit and Dimension [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2OTEyMjUxNDA0MjAyMDk)
🔮Work power and energy [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2OTMyMjc3NzUyODE1NzE)
🔮Vector [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2OTIyMjY0NTc4NTA4OTA)
🔮Current and electricty [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2OTQyMjkwOTI3MTIyNTI)
🔮Com [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE2OTUyMzA0MTAxNDI5MzM)
''',
     
     reply_markup = InlineKeyboardMarkup([[ InlineKeyboardButton("Back", callback_data= "help_cb"),],]),
     parse_mode=ParseMode.MARKDOWN,                              
     )
    elif data == "mod_un_chem":
     await query.message.edit_text(
     text = f''' 🏮PHYSICAL CHEMISTRY MODULES

🔮Mole Concept    [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTk0MTIzODM4NDg0MDE0MA) 
🔮Atomic structure     [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTk0MDIzNzA2NzQwOTQ1OQ) 
🔮Chemical Equilibrium    [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTkzNDIyOTE2MjgyNTM3Mw)
🔮Ionic Equilibrium    [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTkzMTIyNTIxMDUzMzMzMA) 
🔮Redox    [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTkzMzIyNzg0NTM5NDY5Mg) 
🔮Thermodyanamics    [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTkzMjIyNjUyNzk2NDAxMQ) 
🔮States of Matter    [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTkzMDIyMzg5MzEwMjY0OQ) 
🔮Solution    [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTkzNjIzMTc5NzY4NjczNQ) 
🔮Chemical Kinetics    [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTkzODIzNDQzMjU0ODA5Nw) 
🔮Surface Chemistry    [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me{BOT_USERNM}?start=Z2V0LTkzOTIzNTc0OTk3ODc3OA) 
🔮Electrochemistry  [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTkzNzIzMzExNTExNzQxNg) 
🔮Solid States    [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTkzNTIzMDQ4MDI1NjA1NA)
 

     ''',
    
     reply_markup = InlineKeyboardMarkup(
                [ 
                    [
                       InlineKeyboardButton("Inorganic", callback_data= "mod_un_ioc"),
                       InlineKeyboardButton("Organic", callback_data= "mod_un_oc"),
                    ],
                    [
                       InlineKeyboardButton("Back", callback_data= "help_mod"),
                   ],
                ]
            ),
     parse_mode=ParseMode.MARKDOWN,
     )
    elif data == "mod_un_ioc":
     await query.message.edit_text(
     text = f''' 🏮INORGANIC MODULES

🔮Periodic table [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE3MTYyNTgwNzYxODcyMzQ)
🔮Metallurgy [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE3MTUyNTY3NTg3NTY1NTM)
🔮D andF Block [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE3MTQyNTU0NDEzMjU4NzI)
🔮Coordination Compounds [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE3MTMyNTQxMjM4OTUxOTE)
🔮Chemical Bonding [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE3MTIyNTI4MDY0NjQ1MTA)
🔮S block [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/{BOT_USERNM}?start=Z2V0LTE3MTEyNTE0ODkwMzM4Mjk)
 

     ''',
    
     reply_markup = InlineKeyboardMarkup(
                [ 
                    [
                       InlineKeyboardButton("Physical", callback_data= "mod_un_chem"),
                       InlineKeyboardButton("Organic", callback_data= "mod_un_oc"),
                    ],
                    [
                       InlineKeyboardButton("Back", callback_data= "help_mod"),
                   ],
                ]
            ),
     parse_mode=ParseMode.MARKDOWN,
     )  
    elif data == "mod_un_oc":
     await query.message.edit_text(
     text = f''' 🏮ORGANIC MODULES 

🔮Goc [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/Voltaic_Robot?start=Z2V0LTE2OTgyMzQzNjI0MzQ5NzY)
🔮Qualtative and Qualitative  [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/Voltaic_Robot?start=Z2V0LTE2OTkyMzU2Nzk4NjU2NTc)
🔮Isomer [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/Voltaic_Robot?start=Z2V0LTE3MDAyMzY5OTcyOTYzMzg)
🔮Polymer [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/Voltaic_Robot?start=Z2V0LTE3MDEyMzgzMTQ3MjcwMTk)
🔮Alcohol Phenol and Ether [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/Voltaic_Robot?start=Z2V0LTE3MDIyMzk2MzIxNTc3MDA)
🔮Hydrocarbon [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/Voltaic_Robot?start=Z2V0LTE3MDMyNDA5NDk1ODgzODE)
🔮Chemsitry in Every Day Life [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/Voltaic_Robot?start=Z2V0LTE3MDYyNDQ5MDE4ODA0MjQ)
🔮Amines [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/Voltaic_Robot?start=Z2V0LTE3MDUyNDM1ODQ0NDk3NDM)
🔮Biomolecules [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/Voltaic_Robot?start=Z2V0LTE3MDQyNDIyNjcwMTkwNjI)
🔮Environmental Chemistry [ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/Voltaic_Robot?start=Z2V0LTE3MDgyNDc1MzY3NDE3ODY)
    ''',
    
     reply_markup = InlineKeyboardMarkup(
                [ 
                    [
                       InlineKeyboardButton("Physical", callback_data= "mod_un_chem"),
                       InlineKeyboardButton("Inorganic", callback_data= "mod_un_ioc"),
                    ],
                    [
                       InlineKeyboardButton("Back", callback_data= "help_mod"),
                   ],
                ]
            ),
     parse_mode=ParseMode.MARKDOWN,
     )  
        
