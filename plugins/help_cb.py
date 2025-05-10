#help call back 
from pyrogram import __version__
from bot import Bot
from config import OWNER_ID,BOT_USERNM
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
@Bot.on_callback_query(group=250)
async def hlpcallback(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "help_cb":
        await query.message.edit_text(
            text = f'''[✨](https://telegra.ph/file/aae81838e9198e85680b2.jpg) Hey there... I'm `Voltaic Bot` 
 🔮I have lots of features like  Books, Modules , Notes etc ,  and many others useful commands 
 🌀Click on the buttons below to get documentation about specific modules''',
            parse_mode = ParseMode.MARKDOWN,
            disable_web_page_preview = False,
            reply_markup = InlineKeyboardMarkup(
                [
        [
            InlineKeyboardButton("PYQ",   callback_data= "help_pyq"),
            InlineKeyboardButton("PLP",   callback_data= "helpjhj_elp"),
        ],
        [
            InlineKeyboardButton("Notes",   callback_data= "help_nots"),
            InlineKeyboardButton("Teachers", callback_data= "help_six"),
        ] ,
        [
            InlineKeyboardButton("Bots", url= f"https://t.me/{BOT_USERNM}?start=Z2V0LTE2MjUxMzgxODk5OTUyNjM"),   
            InlineKeyboardButton("Channels", url= f"https://t.me/{BOT_USERNM}?start=Z2V0LTE2MjMxMzU1NTUxMzM5MDE"),
        ],
        [
            InlineKeyboardButton("Close", callback_data= "close"),   
            
        ],            
        ]
            )
        )
        
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
