from pyrogram import __version__
from bot import Bot
from config import OWNER_ID, BOT_USERNM
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from pyrogram import filters
from pyrogram.enums import ParseMode


@Bot.on_callback_query(group=250)
async def hlpcallback(client: Bot, query: CallbackQuery):
    data = query.data

    # ================= HELP MAIN MENU =================
    if data == "help_cb":
        await query.message.edit_text(
            text=(
                "[✨](https://graph.org/file/9a1fac95deb33b3b14528-2b7e0c9f1aef47697c.jpg) "
                "Hey there... I'm `Vexper Bot`\n"
                "🔮 I have lots of features"
            ),
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=False,
            reply_markup=InlineKeyboardMarkup(
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
                        InlineKeyboardButton("❌ Close", callback_data="close"),
                    ],
                ]
            )
        )

    # ================= 1ST YEAR =================
    elif data == "year_1":
        await query.message.edit_text(
            text="📖 **1st Year Books:** Choose a category below.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("📚 Lectures", callback_data="first_lectures"),
                        InlineKeyboardButton("📖 Books", callback_data="first_books"),
                    ],
                    [
                        InlineKeyboardButton("📝 Notes", callback_data="first_notes"),
                        InlineKeyboardButton("🎲 Random Stuff", callback_data="first_random"),
                    ],
                    [
                        InlineKeyboardButton("🔙 Back", callback_data="help_cb"),
                    ],
                ]
            )
        )

    # ================= 2ND YEAR =================
    elif data == "year_2":
        await query.message.edit_text(
            text="📘 **2nd Year Books:** Choose a category below.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("📚 Lectures", callback_data="second_lectures"),
                        InlineKeyboardButton("📖 Books", callback_data="second_books"),
                    ],
                    [
                        InlineKeyboardButton("📝 Notes", callback_data="second_notes"),
                        InlineKeyboardButton("🎲 Random Stuff", callback_data="second_random"),
                    ],
                    [
                        InlineKeyboardButton("🔙 Back", callback_data="help_cb"),
                    ],
                ]
            )
        )

    # ================= 3RD YEAR =================
    elif data == "year_3":
        await query.message.edit_text(
            text="📗 **3rd Year Books:** Choose a category below.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("📚 Lectures", callback_data="third_lectures"),
                        InlineKeyboardButton("📖 Books", callback_data="third_books"),
                    ],
                    [
                        InlineKeyboardButton("📝 Notes", callback_data="third_notes"),
                        InlineKeyboardButton("🎲 Random Stuff", callback_data="third_random"),
                    ],
                    [
                        InlineKeyboardButton("🔙 Back", callback_data="help_cb"),
                    ],
                ]
            )
        )

    # ================= 4TH YEAR =================
    elif data == "year_4":
        await query.message.edit_text(
            text="📕 **4th Year Books:** Choose a category below.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("📚 Lectures", callback_data="fourth_lectures"),
                        InlineKeyboardButton("📖 Books", callback_data="fourth_books"),
                    ],
                    [
                        InlineKeyboardButton("📝 Notes", callback_data="fourth_notes"),
                        InlineKeyboardButton("🎲 Random Stuff", callback_data="fourth_random"),
                    ],
                    [
                        InlineKeyboardButton("🔙 Back", callback_data="help_cb"),
                    ],
                ]
            )
        )

    # ================= CLOSE =================
    elif data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass

   
