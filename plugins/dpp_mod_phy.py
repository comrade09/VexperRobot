import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from helper_func import subscribed, encode, decode, get_messages
from pyrogram import __version__
from config import OWNER_ID, BOT_USERNM

photo = "https://telegra.ph/file/f27dae61c59513d5e25fc.jpg"

@Bot.on_callback_query(group=10)
async def phymods(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "pj_mod_12":
        await query.message.reply_photo( photo ,
            caption = f'''🌱 𝙋𝙅 𝙎𝙄𝙍 𝘾𝙇𝘼𝙎𝙎 12 𝙈𝙊𝘿𝙐𝙇𝙀𝙎
            
🔮Electrostatics <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTk4MzI5MzcxNjkyODc0Mi05NzgyODcxMjk3NzUzMzc"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 

🔮Capacitors <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTk4NDI5NTAzNDM1OTQyMy05OTAzMDI5Mzg5NDM1MDk"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Current & Electricty <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTk5MTMwNDI1NjM3NDE5MC05OTczMTIxNjA5NTgyNzY"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Magnetism & Matter <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTk5ODMxMzQ3ODM4ODk1Ny0xMDAzMzIwMDY1NTQyMzYy"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮EMI <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEwMDQzMjEzODI5NzMwNDMtMTAwOTMyNzk3MDEyNjQ0OA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮AC <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEwMTAzMjkyODc1NTcxMjktMTAxNTMzNTg3NDcxMDUzNA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Em waves <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEwMTYzMzcxOTIxNDEyMTUtMTAxNjMzNzE5MjE0MTIxNQ"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Geometrical Optics  <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEwMTgzMzk4MjcwMDI1NzctMTAyMzM0NjQxNDE1NTk4Mg"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Wave Optics <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEwMjQzNDc3MzE1ODY2NjMtMTAyOTM1NDMxODc0MDA2OA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Modern Physics <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEwMzAzNTU2MzYxNzA3NDktMTAzNTM2MjIyMzMyNDE1NA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Semiconductor <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEwMzYzNjM1NDA3NTQ4MzUtMTAzOTM2NzQ5MzA0Njg3OA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>''',
            reply_markup = InlineKeyboardMarkup(
                [
                   [
                       InlineKeyboardButton("Back", callback_data= "help_six"),
                   ],
                ]
            )
        )
        
@Bot.on_callback_query(group=11)
async def pcnots(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "pj_mod_11":
        await query.message.reply_photo( photo ,
            caption = f''' 🌱𝙋𝙅 𝙎𝙄𝙍 𝘾𝙇𝘼𝙎𝙎 11 𝙈𝙊𝘿𝙐𝙇𝙀𝙎
            
🔮Units and Measurements <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEwNDIzNzE0NDUzMzg5MjEtMTA0NzM3ODAzMjQ5MjMyNg"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Basic Maths <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEwNDgzNzkzNDk5MjMwMDctMTA0OTM4MDY2NzM1MzY4OA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Vectors <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEwNTAzODE5ODQ3ODQzNjktMTA1NTM4ODU3MTkzNzc3NA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Kinematics <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEwNTYzODk4ODkzNjg0NTUtMTA2MzM5OTExMTM4MzIyMg"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Newton Laws of motion <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEwNjQ0MDA0Mjg4MTM5MDMtMTA2OTQwNzAxNTk2NzMwOA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Work Energy and power <a href= "https://t.me/Voltaic_Robot?start=Z2V0LTIzNzAxMTgzNTg0MjE5MjctMjM3NTEyNDk0NTU3NTMzMg"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Circular Motion <a href= "https://t.me/Voltaic_Robot?start=Z2V0LTIzMjgwNjMwMjYzMzMzMjUtMjMzMzA2OTYxMzQ4NjczMA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮COM <a href= "https://t.me/Voltaic_Robot?start=Z2V0LTIzMjgwNjMwMjYzMzMzMjUtMjMzMzA2OTYxMzQ4NjczMA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Rotation <a href= "https://t.me/Voltaic_Robot?start=Z2V0LTIzMzQwNzA5MzA5MTc0MTEtMjMzOTA3NzUxODA3MDgxNg"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Gravitation <a href= "https://t.me/Voltaic_Robot?start=Z2V0LTIzNzYxMjYyNjMwMDYwMTMtMjM4MTEzMjg1MDE1OTQxOA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Fluids <a href= "https://t.me/Voltaic_Robot?start=Z2V0LTIzNDAwNzg4MzU1MDE0OTctMjM0NTA4NTQyMjY1NDkwMg"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
       
🔮Thermo & Elasticity <a href="https://t.me/Voltaic_Robot?start=Z2V0LTIzNzAxMTgzNTg0MjE5MjctMjM3NTEyNDk0NTU3NTMzMg"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Ktg <a href= "https://t.me/Voltaic_Robot?start=Z2V0LTIzODgxNDIwNzIxNzQxODUtMjM5MzE0ODY1OTMyNzU5MA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Simple Harmonic Motion <a href= "https://t.me/Voltaic_Robot?start=Z2V0LTIzNDYwODY3NDAwODU1ODMtMjM1MTA5MzMyNzIzODk4OA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Waves <a href= "https://t.me/Voltaic_Robot?start=Z2V0LTIzNTgxMDI1NDkyNTM3NTUtMjM2MzEwOTEzNjQwNzE2MA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
''',
                      
            
            reply_markup = InlineKeyboardMarkup(
                [
                   [
                       InlineKeyboardButton("Back", callback_data= "help_six"),
                   ],
                ]
            )
        )
        
@Bot.on_callback_query(group=12)
async def ask_cb(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "dpp_12":
        await query.message.reply_photo( photo ,
            caption = f'''🌱 𝙋𝙅 𝙎𝙄𝙍 𝘿𝙋𝙋 𝘾𝙇𝘼𝙎𝙎  12
 
🔮Electrostatics <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTExNDE1MDE4NzA5NzYzNDAtMTE0NzUwOTc3NTU2MDQyNg"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 

🔮Capacitors <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTExNTE1MTUwNDUyODMxNTAtMTE1NTUyMDMxNTAwNTg3NA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Current & Electricty <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTExNTc1MjI5NDk4NjcyMzYtMTE2NTUzMzQ4OTMxMjY4NA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Magnetism  <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTExNjg1Mzc0NDE2MDQ3MjctMTE3MzU0NDAyODc1ODEzMg"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Magnetism & Matter <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTExNzY1NDc5ODEwNTAxNzUtMTE3OTU1MTkzMzM0MjIxOA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮EMI <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTExOTE1Njc3NDI1MTAzOTAtMTE5NzU3NTY0NzA5NDQ3Ng"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮AC <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTExODI1NTU4ODU2MzQyNjEtMTE4NDU1ODUyMDQ5NTYyMw"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Em waves <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTExODc1NjI0NzI3ODc2NjYtMTE4ODU2Mzc5MDIxODM0Nw"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Geometrical Optics  <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEyMDA1Nzk1OTkzODY1MTktMTIxMDU5Mjc3MzY5MzMyOQ"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Optical Instruments  <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEyNDA2MzIyOTY2MTM3NTktMTI0MTYzMzYxNDA0NDQ0MA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Wave Optics <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEyMTM1OTY3MjU5ODUzNzItMTIxNjYwMDY3ODI3NzQxNQ"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Modern Physics <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEyMTk2MDQ2MzA1Njk0NTgtMTIyODYxNjQ4NzQ0NTU4Nw"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Semiconductor <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEyMzE2MjA0Mzk3Mzc2MzAtMTIzNTYyNTcwOTQ2MDM1NA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
''',
            
            reply_markup = InlineKeyboardMarkup(
                [
                   [
                       InlineKeyboardButton("Back", callback_data= "help_six"),
                   ],
                ]
            )
        )
@Bot.on_callback_query(group=13)
async def zoo_nots(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "dpp_11":
        await query.message.reply_photo( photo ,
            caption = f'''🌱 𝙋𝙅 𝙎𝙄𝙍 𝘿𝙋𝙋 𝘾𝙇𝘼𝙎𝙎  11
🔮Units and Measurements <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEyNDQ2Mzc1NjYzMzY0ODMtMTI0OTY0NDE1MzQ4OTg4OA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Basic Maths <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEyNTc2NTQ2OTI5MzUzMzYtMTI2NTY2NTIzMjM4MDc4NA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Vectors <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEyNTE2NDY3ODgzNTEyNTAtMTI1NTY1MjA1ODA3Mzk3NA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Kinematics <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEyNjg2NjkxODQ2NzI4MjctMTI3NjY3OTcyNDExODI3NQ"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮NLM & Friction <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEyNzk2ODM2NzY0MTAzMTgtMTI4NTY5MTU4MDk5NDQwNA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Friction <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEyODc2OTQyMTU4NTU3NjYtMTI4ODY5NTUzMzI4NjQ0Nw"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Work Energy and power <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEyOTE2OTk0ODU1Nzg0OTAtMTI5NjcwNjA3MjczMTg5NQ"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Circular Motion <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEzMDU3MTc5Mjk2MDgwMjQtMTMwOTcyMzE5OTMzMDc0OA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮COM <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEzMjQ3NDI5NjA3OTA5NjMtMTMzMTc1MjE4MjgwNTczMA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Rotation <a href= "https://t.me/Voltaic_Robot?start=Z2V0LTIzMTQwNDQ1ODIzMDM3OTEtMjMyMTA1MzgwNDMxODU1OA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Gravitation <a href= "https://t.me/Voltaic_Robot?start=Z2V0LTIzMjIwNTUxMjE3NDkyMzktMjMyNzA2MTcwODkwMjY0NA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Fluids <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEyOTg3MDg3MDc1OTMyNTctMTMwMzcxNTI5NDc0NjY2Mg"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
       
🔮Thermo part 1  <a href="https://t.me/Voltaic_Robot?start=Z2V0LTIzOTQxNDk5NzY3NTgyNzEtMjQwMTE1OTE5ODc3MzAzOA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Thermo part 2  <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTEzNDM3Njc5OTE5NzM5MDItMTM1MDc3NzIxMzk4ODY2OQ"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Elasticity <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEzMjE3MzkwMDg0OTg5MjAtMTMyMjc0MDMyNTkyOTYwMQ"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Simple Harmonic Motion <a href= "https://t.me/Voltaic_Robot?start=Z2V0LTI0MDIxNjA1MTYyMDM3MTktMjQwNzE2NzEwMzM1NzEyNA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Waves & Sound <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTEzMTE3MjU4MzQxOTIxMTAtMTMxOTczNjM3MzYzNzU1OA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>''',
            
            reply_markup = InlineKeyboardMarkup(
                [
                   [
                       InlineKeyboardButton("Back", callback_data= "help_six"),
                   ],
                ]
            )
        )
@Bot.on_callback_query(group=13)
async def bot_nots(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "pj_neet_pyq":
        await query.message.edit_text(
            text = f'''
🔮Neet PYQ <a href= "https://t.me/Voltaic_Robot?start=Z2V0LTEzODA4MTY3MzY5MDkwOTktMTM4MTgxODA1NDMzOTc4MA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
            
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
       
        
