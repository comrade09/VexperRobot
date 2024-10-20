import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from helper_func import subscribed, encode, decode, get_messages
from pyrogram import __version__
from config import OWNER_ID, BOT_USERNM

@Bot.on_callback_query(group=253)
async def phynots(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "phy_nots":
        await query.message.reply_text(
            text = f'''🌱𝙋𝙅 𝙎𝙄𝙍 𝙋𝙃𝙔𝙎𝙄𝘾𝙎 𝘾𝙇𝘼𝙎𝙎 𝙉𝙊𝙏𝙀𝙎

🔮Units and Measurements <a href= "https://t.me/Voltaic_Network/18"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Basic Maths <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTgxNTA3MjM4ODU3NDMzNA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Vectors <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTgwMDA1MjYyNzExNDExOQ"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Kinematics <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTgxMDA2NTgwMTQyMDkyOQ"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Newton Laws of motion <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTgwODA2MzE2NjU1OTU2Nw"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Work Energy and power <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTgwNjA2MDUzMTY5ODIwNQ"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Circular Motion <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTgwOTA2NDQ4Mzk5MDI0OA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮COM <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTgwNzA2MTg0OTEyODg4Ng"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Rotation <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTgwNTA1OTIxNDI2NzUyNA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Gravitation <a href= "https://t.me/Voltaic_Network/18"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Elasticity <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTgwNDA1Nzg5NjgzNjg0Mw"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Fluids <a href= "https://t.me/Voltaic_Network/18"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
       
🔮Thermodynamics <a href= "https://t.me/Voltaic_Network/18"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Simple Harmonic Motion <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTgwMzA1NjU3OTQwNjE2Mg"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Waves <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTgwMjA1NTI2MTk3NTQ4MQ"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 

🔮Electrostatics <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTE0Njg5MzI2NzA4MDkwMjc">ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮Current Electricity <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTE0Njk5MzM5ODgyMzk3MDg">ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮Capacitors <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTE0NzA5MzUzMDU2NzAzODk">ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮Moving Charges and Magnetism <a href="https://t.me/Voltaic_Network/18">ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮Magnetism and Matter <a href="https://t.me/Voltaic_Network/18">ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮Electromagnetic Induction <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTE0NzE5MzY2MjMxMDEwNzA">ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮Alternating Current Old <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTE0NzI5Mzc5NDA1MzE3NTE">ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮Alternating Current New <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTE0NzM5MzkyNTc5NjI0MzI">ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮Electromagnetic Waves <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTE0NzQ5NDA1NzUzOTMxMTM">ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮Ray Optics  <a href="https://t.me/Voltaic_Network/18">ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮Wave Optics <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTE0Nzc5NDQ1Mjc2ODUxNTY">ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮Modern <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTE0Nzk5NDcxNjI1NDY1MTg">ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮Semiconductor 1  <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTE0NzU5NDE4OTI4MjM3OTQ">ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮Semiconductor 2 <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTE0NzY5NDMyMTAyNTQ0NzU">ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>
            ''',
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                   [
                       InlineKeyboardButton("Back", callback_data= "help_nots"),
                   ],
                ]
            )
        )
        
@Bot.on_callback_query(group=254)
async def pcnots(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "pc_nots":
        await query.message.edit_text(
            text = f'''🌱𝙋𝙃𝙔𝙎𝙄𝘾𝘼𝙇 𝘾𝙃𝙀𝙈𝙄𝙎𝙏𝙍𝙔 𝙉𝙊𝙏𝙀𝙎

🔮Mole Concept   <a href = "https://t.me/{BOT_USERNM}?start=Z2V0LTUyMjY4NzY5ODgxNTQ4Mg" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Atomic structure    <a href = "https://t.me/{BOT_USERNM}?start=Z2V0LTUxOTY4Mzc0NjUyMzQzOQ" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Chemical Equilibrium   <a href = "https://t.me/{BOT_USERNM}?start=Z2V0LTUyMDY4NTA2Mzk1NDEyMA" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 

🔮Ionic Equilibrium   <a href = "https://t.me/{BOT_USERNM}?start=Z2V0LTUyMTY4NjM4MTM4NDgwMQ" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Redox   <a href = "https://t.me/{BOT_USERNM}?start=Z2V0LTU2OTc0OTYxODA1NzQ4OQ" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Thermodyanamics   <a href = "https://t.me/{BOT_USERNM}?start=Z2V0LTUyNzY5NDI4NTk2ODg4Nw" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮States of Matter   <a href = "https://t.me/{BOT_USERNM}?start=Z2V0LTUzMjcwMDg3MzEyMjI5Mg" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Solution   <a href = "https://t.me/{BOT_USERNM}?start=Z2V0LTUyNTY5MTY1MTEwNzUyNQ" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Chemical Kinetics   <a href = "https://t.me/{BOT_USERNM}?start=Z2V0LTUyNDY5MDMzMzY3Njg0NA" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Surface Chemistry   <a href = "https://t.me/{BOT_USERNM}?start=Z2V0LTU2ODc0ODMwMDYyNjgwOA" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Electrochemistry <a href = "https://t.me/{BOT_USERNM}?start=Z2V0LTUyODY5NTYwMzM5OTU2OA" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Solid States   <a href = "https://t.me/{BOT_USERNM}?start=Z2V0LTUyMzY4OTAxNjI0NjE2Mw" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>


🧧ᴄʀᴇᴅɪᴛꜱ  <a href = "http://t.me/linklockernet" > ʟɪɴᴋ ʟᴏᴄᴋᴇʀ ɴᴇᴛᴡᴏʀᴋ </a>''',
                      
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                   [
                       InlineKeyboardButton("Back", callback_data= "help_nots"),
                   ],
                ]
            )
        )
        

@Bot.on_callback_query(group=258)
async def zoo_nots(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "zoo_nots":
        await query.message.edit_text(
            text = f'''🌱Zoology Notes Ag sir 
🔮Application Biotech <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTQxNDU0NTQxNjMwMTkzNA">cʟɪᴄᴋ ʜᴇʀᴇ </a> 

🔮Microbes in Human Welfare <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTQxNTU0NjczMzczMjYxNQ">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 

🔮Human Reproduction <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTQxNjU0ODA1MTE2MzI5Ng">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 

🔮Evolution <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTQxNzU0OTM2ODU5Mzk3Nw">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 

🔮Human Health &amp; Diseases <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTQxODU1MDY4NjAyNDY1OA">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 

🔮Animal Diversity <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTQxOTU1MjAwMzQ1NTMzOQ">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 

🔮Earthworm <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTQyMDU1MzMyMDg4NjAyMA">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 

🔮Neural Control <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTQyMTU1NDYzODMxNjcwMQ">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 

🔮Endocrine X <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTQyMjU1NTk1NTc0NzM4Mg">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 

🔮Human Skeleton <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTQyMzU1NzI3MzE3ODA2Mw">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 

🔮Animal Tissue<a href="https://t.me/{BOT_USERNM}?start=Z2V0LTQyNDU1ODU5MDYwODc0NA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 

🔮Human Circulatory...<a href="https://t.me/{BOT_USERNM}?start=Z2V0LTQyNjU2MTIyNTQ3MDEwNg"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 

🔮Excretion <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTQyNTU1OTkwODAzOTQyNQ">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 

🔮Sensory Organs <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTQyNzU2MjU0MjkwMDc4Nw"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 

🔮Muscles <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTQyODU2Mzg2MDMzMTQ2OA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 

🔮Digestion <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTQyOTU2NTE3Nzc2MjE0OQ">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 

🔮Respiratory system <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTQzMDU2NjQ5NTE5MjgzMA">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 

🧧ᴄʀᴇᴅɪᴛꜱ <a href="http://t.me/linklockernet">ʟɪɴᴋ ʟᴏᴄᴋᴇʀ ɴᴇᴛᴡᴏʀᴋ ''',
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                   [
                       InlineKeyboardButton("Back", callback_data= "help_nots"),
                   ],
                ]
            )
        )
@Bot.on_callback_query(group=254848)
async def zoo_nots(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "org_nots":
        await query.message.edit_text(
            text = f'''
🔮YSY SIR Handouts : <a href="https://t.me/Voltaic_Robot?start=Z2V0LTIyNzA5ODc5MzI3ODQ1MDg"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮YSY SIR GOC 2 NOTES : <a href="https://t.me/Voltaic_Robot?start=Z2V0LTIyNzA5ODc5MzI3ODQ1MDg"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 
🔮SKC SIR  Notes  <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTY5NzkxODI0OTE4NDY1Nw">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 
🔮SKC SIR  GOC 1 NOTES <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTI0MjUxOTA4MTcxMDkzODI">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 
🔮SKC SIR  GOC 2 NOTES <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTI0MjYxOTIxMzQ1NDAwNjM">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 

''',
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                   [
                       InlineKeyboardButton("Back", callback_data= "help_nots"),
                   ],
                ]
            )
        )

@Bot.on_callback_query(group=2)
async def bot_nots(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "bot_nots":
        await query.message.edit_text(
            text = f'''🌱Botany notes Sn Sir 

🔮 The Living World <a href="https://t.me/Voltaic_Robot?start=Z2V0LTkxMjIwMDE3OTM1MDM5MQ">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Biological Classification<a href="https://t.me/Voltaic_Robot?start=Z2V0LTkwODE5NDkwOTYyNzY2Nw">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Plant Kingdom <a href="https://t.me/Voltaic_Robot?start=Z2V0LTkwNDE4OTYzOTkwNDk0Mw">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Morphology of Flowering Plants <a href="https://t.me/Voltaic_Robot?start=Z2V0LTkwMTE4NTY4NzYxMjkwMA">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Morpho Extra <a href="https://t.me/Voltaic_Robot?start=Z2V0LTkxMTE5ODg2MTkxOTcxMA">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Anatomy of Flowering Plants <a href="https://t.me/Voltaic_Robot?start=Z2V0LTkwNzE5MzU5MjE5Njk4Ng">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Cell The Unit of Life <a href="https://t.me/Voltaic_Robot?start=Z2V0LTkxMDE5NzU0NDQ4OTAyOQ">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Biomolecules <a href="https://t.me/Voltaic_Robot?start=Z2V0LTkwOTE5NjIyNzA1ODM0OA">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Cell Cycle & Cell Division <a href="https://t.me/Voltaic_Robot?start=Z2V0LTkxNTIwNDEzMTY0MjQzNA">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Fruit Chart <a href="https://t.me/Voltaic_Robot?start=Z2V0LTkxNDIwMjgxNDIxMTc1Mw">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Transport Plants <a href="https://t.me/Voltaic_Robot?start=Z2V0LTkwMjE4NzAwNTA0MzU4MQ">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Mineral Nutrition <a href="https://t.me/Voltaic_Robot?start=Z2V0LTkxMzIwMTQ5Njc4MTA3Mg">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Mineral chart <a href="https://t.me/Voltaic_Robot?start=Z2V0LTkwMDE4NDM3MDE4MjIxOQ">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Photosynthesis Higher Plants <a href="https://t.me/Voltaic_Robot?start=Z2V0LTkwNjE5MjI3NDc2NjMwNQ">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Respiration Plants <a href="https://t.me/Voltaic_Robot?start=Z2V0LTkwMzE4ODMyMjQ3NDI2Mg">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Plant Growth & Development <a href="https://t.me/Voltaic_Robot?start=Z2V0LTkwNTE5MDk1NzMzNTYyNA">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Sexual Reproduction Flowering Plants <a href="https://t.me/Voltaic_Robot?start=Z2V0LTg4OTE2OTg3ODQ0NDcyOA">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Pre Mendelism <a href="https://t.me/Voltaic_Robot?start=Z2V0LTg5NTE3Nzc4MzAyODgxNA">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Principles of Inheritance & Variation <a href="https://t.me/Voltaic_Robot?start=Z2V0LTg5NDE3NjQ2NTU5ODEzMw">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Gentics <a href="https://t.me/Voltaic_Robot?start=Z2V0LTg5NjE3OTEwMDQ1OTQ5NQ">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Gentics Incomplete Linkage  <a href="https://t.me/Voltaic_Robot?start=Z2V0LTg5NzE4MDQxNzg5MDE3Ng">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Molecular Basis of Inheritance <a href="https://t.me/Voltaic_Robot?start=Z2V0LTg5MjE3MzgzMDczNjc3MQ">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Strategies for Enhancement Food Production <a href="https://t.me/Voltaic_Robot?start=Z2V0LTg4ODE2ODU2MTAxNDA0Nw">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Microbes Human Welfare <a href="https://t.me/Voltaic_Robot?start=Z2V0LTg5MzE3NTE0ODE2NzQ1Mg">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Biotechnology:Principles & Processes <a href="">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Organisms & Populations <a href="https://t.me/Voltaic_Robot?start=Z2V0LTg5MTE3MjUxMzMwNjA5MA">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Ecosystem <a href="https://t.me/Voltaic_Robot?start=Z2V0LTg5ODE4MTczNTMyMDg1Nw">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Biodiversity & Conservation <a href="https://t.me/Voltaic_Robot?start=Z2V0LTg5OTE4MzA1Mjc1MTUzOA">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>
🔮 Environmental Issues <a href="https://t.me/Voltaic_Robot?start=Z2V0LTg4NzE2NzI0MzU4MzM2Ng">ᴄʟɪᴄᴋ ʜᴇʀᴇ </a> 

🧧ᴄʀᴇᴅɪᴛꜱ <a href="http://t.me/linklockernet">ʟɪɴᴋ ʟᴏᴄᴋᴇʀ ɴᴇᴛᴡᴏʀᴋ ''',
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                   [
                       InlineKeyboardButton("Back", callback_data= "help_nots"),
                   ],
                ]
            )
        )
       
        
