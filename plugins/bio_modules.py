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

@Bot.on_callback_query(group=15)
async def bio_module(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "mod_una_bio":
     await query.message.reply_text( 
     text = f'''
🏮 𝘾𝙇𝘼𝙎𝙎 12 𝙏𝙃 𝘼𝙇𝙇 𝘽𝙄𝙊𝙇𝙊𝙂𝙔 𝙈𝙊𝘿𝙐𝙇𝙀𝙎

🔮Repro. in Organisms  <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTgzMTA5MzQ2NzQ2NTIzMA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>  

🔮Sexual Repro. in Flr Plant <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTgzMjA5NDc4NDg5NTkxMQ"> ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮Human Reproduction <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTg0NTExMTkxMTQ5NDc2NA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Reproductive Health <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTgzNDA5NzQxOTc1NzI3Mw"> ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮Principles of Inheritance  <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTg0NzExNDU0NjM1NjEyNg"> ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮Molecular Basis of Inher. <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTg0ODExNTg2Mzc4NjgwNw"> ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮Evolution <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTgzODEwMjY4OTQ3OTk5Nw"> ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮Human Health and Disease <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTgzOTEwNDAwNjkxMDY3OA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮Strategies for Enhancement <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTg0MDEwNTMyNDM0MTM1OQ"> ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮Animal Husbandary <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTgzNzEwMTM3MjA0OTMxNg"> ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮 Microbes in Human Welfare  <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTg0NjExMzIyODkyNTQ0NQ"> ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮 Biotechnology:Principles <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTg0OTExNzE4MTIxNzQ4OA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮 Biotech & it's Apps  <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTg0MTEwNjY0MTc3MjA0MA"> ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮 Ecosystem <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTg0MzEwOTI3NjYzMzQwMg"> ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮 Biodiversity and Conservation <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTg0NDExMDU5NDA2NDA4Mw"> ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>

🔮 Environmental Issues <a href= "https://t.me/{BOT_USERNM}?start=Z2V0LTg0MjEwNzk1OTIwMjcyMQ"> ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>
     ''',
     disable_web_page_preview = True,
     reply_markup = InlineKeyboardMarkup(
                [  
                   [
                       InlineKeyboardButton("Class 11", callback_data= "mod_una_bio_11"),
                       InlineKeyboardButton("Back", callback_data= "help_cb"),
                   ],
                ]
            )
        
        )

    elif data == "mod_una_bio_11":
     await query.message.edit_text(  text = f''' 🏮 𝘾𝙇𝘼𝙎𝙎 11 𝙏𝙃 𝘼𝙇𝙇 𝘽𝙄𝙊𝙇𝙊𝙂𝙔 𝙈𝙊𝘿𝙐𝙇𝙀𝙎
     
🔮Living World              <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTY3OTg5NDUzNTQzMjM5OQ" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Biological Classi.        <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTY4MDg5NTg1Mjg2MzA4MA" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Plant Kingdom             <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTY4MTg5NzE3MDI5Mzc2MQ" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Animal Kingdom            <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTgxMzA2OTc1MzcxMjk3Mg" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮 Morpho Of Flr. Plants    <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTY4Mzg5OTgwNTE1NTEyMw" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Ana. of Flr. Plants       <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTY4NDkwMTEyMjU4NTgwNA" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Str. Orgna. in Animals    <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTY4NjkwMzc1NzQ0NzE2Ng" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Cell The Unit of Life     <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTY4NzkwNTA3NDg3Nzg0Nw" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Enzyme                    <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTY4NTkwMjQ0MDAxNjQ4NQ" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Biomolecules              <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTY5MDkwOTAyNzE2OTg5MA" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Cell Cycle                <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTY4ODkwNjM5MjMwODUyOA" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Transport in Plants       <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTY4OTkwNzcwOTczOTIwOQ" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Photosyn. In Plants       <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTY5MTkxMDM0NDYwMDU3MQ" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Respiration in Plants     <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTY5MzkxMjk3OTQ2MTkzMw" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Plant Growth & Dev       <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTY5MjkxMTY2MjAzMTI1Mg" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Neural Control           <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTgyMzA4MjkyODAxOTc4Mg" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>  

🔮Endocrine                <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTgyMjA4MTYxMDU4OTEwMQ" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>  

🔮Human Skeleton           <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTgyNTA4NTU2Mjg4MTE0NA" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>  

🔮Human Circulatory...     <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTgxOTA3NzY1ODI5NzA1OA" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>  

🔮Sensory Organs           <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTgyNDA4NDI0NTQ1MDQ2Mw" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Muscles                  <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTgyMTA4MDI5MzE1ODQyMA" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>  

🔮Digestion               <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTgxNzA3NTAyMzQzNTY5Ng" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Respiratory system      <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTgxODA3NjM0MDg2NjM3Nw" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>

🔮Excretory System        <a href="https://t.me/{BOT_USERNM}?start=Z2V0LTgyMDA3ODk3NTcyNzczOQ" > ᴄʟɪᴄᴋ ʜᴇʀᴇ </a>''',
         disable_web_page_preview = True,
         reply_markup = InlineKeyboardMarkup(
                [  
                   [    
                       InlineKeyboardButton("Back", callback_data= "help_cb"),
                   ],
                ]
            )
         
        )
