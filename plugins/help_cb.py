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
            text = f'''[✨](https://telegra.ph/file/aae81838e9198e85680b2.jpg) Hey there... I'm `Vexper Bot` 
 🔮I have lots of features ''',
            parse_mode = ParseMode.MARKDOWN,
            disable_web_page_preview = False,
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("1st Year", callback_data="year_1"),
                        InlineKeyboardButton("2nd Year", callback_data="year_2"),
                    ],
                    [
                        InlineKeyboardButton("3rd Year", callback_data="year_3"),
                        InlineKeyboardButton("4th Year", callback_data="year_4"),
                    ],
                    [
                        InlineKeyboardButton("Close", callback_data="close"),
                    ],
                ]
            )
        )



    elif data == "year_1":
        await query.message.edit_text(
            text="📖 **1st Year Books:** Choose a subject below.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                      InlineKeyboardButton("📚 Lectures", callback_data="first_lectures"),
                      InlineKeyboardButton("📖 Books", callback_data="first_books")
                    ],
                    [
                      InlineKeyboardButton("📝 Notes", callback_data="first_notes"),
                      InlineKeyboardButton("🎲 Random Stuff", callback_data="first_random")
                    ]           
                    [
                        InlineKeyboardButton("🔙 Back", callback_data="help_cb"),
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
