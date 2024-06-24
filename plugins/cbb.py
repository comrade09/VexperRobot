#(©)Codexbotz


from pyrogram import __version__
from bot import Bot
from config import OWNER_ID
from database.database import add_user, del_user, full_userbase, present_user
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery


@Bot.on_callback_query(group=278)
async def features(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "features":
        await query.message.edit_text(
            text = f'''🌱 I am developed by <a href = "t.me/Voltaic_Network" > Voltaic Network \n 📡 Hosted on Heroku ''',
            disable_web_page_preview = True,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("close", callback_data = "close")
                    ]
                ]
            )
        )




@Bot.on_callback_query()
async def cb_handler(client: Bot, query: CallbackQuery):
    data = query.data
    if data == "about":

        user_first_name = query.from_user.first_name
        users = await full_userbase()
        await query.message.edit_text(
            text = f'''
🪐**Hey there! `{user_first_name}`**

🌀**Current Users** : {len(users)} Users 

☘️I'm here to make your Learning fun and easy! 

Any issues or need help related to me? Come visit us in Support Chat @linklockernet

This Bot Is  Licensed Under The GNU (General Public License v3.0)
''',
            disable_web_page_preview = True,
            parse_mode = ParseMode.MARKDOWN,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Back", callback_data = "start_cb")
                    ]
                ]
            )
        )
        
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
