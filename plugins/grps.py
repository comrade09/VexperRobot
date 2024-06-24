#(©)Codexbotz


from pyrogram import __version__
from bot import Bot
from config import OWNER_ID
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode



@Bot.on_callback_query(group=274378)
async def features(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "grps":
        await query.message.edit_text(
            text = f'''📈 | ALL Channels and Groups

💬  Link Locker Network 📊
🔗  [Link](https://t.me/+1FCayjoFnrphYWU1)

💬  PDF HEAVEN X ZEN 📊
🔗  [Link](https://t.me/+aDYa9xddKew2MzM1)

💬  Test Series Channel 📊
🔗  [Link](https://t.me/+Qq7kvzT083RmNWI1)

💬  Unacademy Offline Test Series Channel 📊
🔗  [Link](https://t.me/UnacademyXOffline)

💬  Vortex 📊
🔗  [Link](https://t.me/+5UjBcKb8zd00OGZl)

💬  Voltaic Network 🥀 📊
🔗  [Link](https://t.me/Voltaic_Network)

💬  Zen Network 📊
🔗  [Link](https://t.me/+I6q4d-FViExmOWNl)

💬  【V๏ɪ፝֟𝔡】Ꭺᴛʜ 
🔗  [Link](https://t.me/+CUpR_Kg-kcUwZjg1)

💬  Unacademy Offline Course Channel 📊
🔗  [Link](https://t.me/UnacademyXOffline)

''',
            disable_web_page_preview = True,
            parse_mode = ParseMode.MARKDOWN,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("close", callback_data = "close")
                    ]
                ]
            )
        )




