#(©)Codexbotz


from pyrogram import __version__
from bot import Bot
from config import OWNER_ID
from database.database import add_user, del_user, full_userbase, present_user
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery



@Bot.on_callback_query(group=6754674)
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "start_cb":
    
        await query.message.edit_text(
            text = f'''
✨ʜᴇʟʟᴏ... I am Voltaic  <a href=https://telegra.ph/file/4a482570d3919af8ea784.jpg >🦋</a>
''',
            disable_web_page_preview = False,
            parse_mode = ParseMode.HTML,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
        InlineKeyboardButton(text="Help", callback_data="help_cb")
    ],
    [
        InlineKeyboardButton(text="About Me 📓", callback_data="about"),
        
    ],
    [
        InlineKeyboardButton(text="Channels & Groups 📓", callback_data="grps"),
        
    ],            
    [
        InlineKeyboardButton(text="Support ✨", url=f"https://t.me/voltaic_network"),
        InlineKeyboardButton(text="Updates 📡 ", url=f"https://t.me/voltaic_network"),
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
