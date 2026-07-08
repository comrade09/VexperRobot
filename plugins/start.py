import os
import asyncio
import humanize
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated

from bot import Bot
from config import ADMINS, FORCE_MSG, START_MSG, CUSTOM_CAPTION, DISABLE_CHANNEL_BUTTON, PROTECT_CONTENT, BOT_USERNM
from helper_func import subscribed, encode, decode, get_messages
from database.database import add_user, del_user, full_userbase, present_user

FILE_AUTO_DELETE = 600
file_auto_delete = humanize.naturaldelta(FILE_AUTO_DELETE)

# Example string incorporating standard quote and expandable blockquote
WLCM = """
✨ <b>Hello... {first}</b> I am Vexper <a href="https://graph.org/file/2a159572f780916b5d806-eb17c7aa3287170859.jpg">🦋</a>

<b>Citations & Info:</b>
<blockquote>Welcome to the Vexper Bot Network!</blockquote>
<blockquote expandable>Access exclusive contents, files, and updates seamlessly. Tap to expand/collapse this section if text gets too long!</blockquote>
"""

async def delete_files(messages: list, client: Client, status_msg: Message):
    await asyncio.sleep(FILE_AUTO_DELETE)
    for msg in messages:
        try:
            await msg.delete()
        except Exception:
            pass
    try:
        await status_msg.delete()
    except Exception:
        pass


@Bot.on_message(filters.command('start') & filters.private & subscribed)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    if not await present_user(user_id):
        try:
            await add_user(user_id)
        except Exception:
            pass
            
    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
        except Exception:
            return
            
        string = await decode(base64_string)
        argument = string.split("-")
        
        if len(argument) == 3:
            try:
                start = int(int(argument[1]) / abs(client.db_channel.id))
                end = int(int(argument[2]) / abs(client.db_channel.id))
            except Exception:
                return
                
            ids = list(range(start, end + 1)) if start <= end else list(range(start, end - 1, -1))
                        
        elif len(argument) == 2:
            try:
                ids = [int(int(argument[1]) / abs(client.db_channel.id))]
            except Exception:
                return
        else:
            return

        temp_msg = await message.reply("Please Wait...")
        try:
            messages = await get_messages(client, ids)
        except Exception:
            await message.reply_text("Something Went Wrong..!")
            return
            
        await temp_msg.delete()

        sent_messages = []

        for msg in messages:
            caption = (
                CUSTOM_CAPTION.format(
                    previouscaption="" if not msg.caption else msg.caption.html,
                    filename=msg.document.file_name
                ) if bool(CUSTOM_CAPTION) and bool(msg.document)
                else ("" if not msg.caption else msg.caption.html)
            )

            reply_markup = msg.reply_markup if DISABLE_CHANNEL_BUTTON else None

            try:
                sent_msg = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT
                )
                sent_messages.append(sent_msg)
                
            except FloodWait as e:
                await asyncio.sleep(e.value)
                sent_msg = await msg.copy(
                    chat_id=message.from_user.id,
                    caption=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    protect_content=PROTECT_CONTENT
                )
                sent_messages.append(sent_msg)
                
            except Exception:
                pass

        status_msg = await client.send_message(
            chat_id=message.from_user.id,
            text="<b>DONE ✅</b>",
            parse_mode=ParseMode.HTML
        )

        asyncio.create_task(delete_files(sent_messages, client, status_msg))
        return

    else:
        # SCENARIO 1 IMPLEMENTATION: Using raw dictionary layout for custom styling
        reply_markup = InlineKeyboardMarkup([
            [
                {
                    "text": "Access Contents 📂",
                    "callback_data": "help_cb",
                    "style": "primary"  # Blue Button
                }
            ],
            [
                {
                    "text": "About Me 📓",
                    "callback_data": "neet_countdown",
                    "style": "success"  # Green Button
                }
            ],
            [
                {
                    "text": "Support ✨",
                    "url": "https://t.me/vexper_network"
                },
                {
                    "text": "Updates 📡",
                    "url": "https://t.me/vexper_network",
                    "style": "danger"  # Red Button
                }
            ]
        ])

        await message.reply_text(
            text=WLCM.format(
                first=message.from_user.first_name,
                last=message.from_user.last_name or "",
                username=f"@{message.from_user.username}" if message.from_user.username else "None",
                mention=message.from_user.mention,
                id=message.from_user.id
            ),
            reply_markup=reply_markup,
            disable_web_page_preview=False,
            quote=True,
            parse_mode=ParseMode.HTML
        )
        return


# =====================================================================================#

WAIT_MSG = "<b>Processing ...</b>"
REPLY_ERROR = "<code>Use this command as a reply to any Telegram message without spaces.</code>"

# =====================================================================================#


@Bot.on_message(filters.command("start") & filters.private)
async def not_joined(client: Client, message: Message):
    # SCENARIO 1 IMPLEMENTATION for Force-Sub Buttons:
    buttons = [
        [
            {
                "text": "Join Channel 📢",
                "url": client.invitelink,
                "style": "primary"
            }
        ]
    ]
    try:
        buttons.append([
            {
                "text": "Try Again 🔄",
                "url": f"https://t.me/{client.username}?start={message.command[1]}",
                "style": "success"
            }
        ])
    except IndexError:
        pass

    await message.reply(
        text=FORCE_MSG.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name or "",
            username=f"@{message.from_user.username}" if message.from_user.username else "None",
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True,
        disable_web_page_preview=True,
        parse_mode=ParseMode.HTML
    )


@Bot.on_message(filters.command('users') & filters.private & filters.user(ADMINS))
async def get_users(client: Client, message: Message):
    msg = await client.send_message(chat_id=message.chat.id, text=WAIT_MSG, parse_mode=ParseMode.HTML)
    users = await full_userbase()
    await msg.edit(f"{len(users)} users are using this bot")


@Bot.on_message(filters.private & filters.command('broadcast') & filters.user(ADMINS))
async def send_text(client: Client, message: Message):
    if message.reply_to_message:
        query = await full_userbase()
        broadcast_msg = message.reply_to_message
        total = successful = blocked = deleted = unsuccessful = 0

        pls_wait = await message.reply("<i>Broadcasting Message.. This will take some time.</i>", parse_mode=ParseMode.HTML)
        
        for chat_id in query:
            try:
                await broadcast_msg.copy(chat_id)
                successful += 1
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await broadcast_msg.copy(chat_id)
                successful += 1
            except UserIsBlocked:
                await del_user(chat_id)
                blocked += 1
            except InputUserDeactivated:
                await del_user(chat_id)
                deleted += 1
            except Exception:
                unsuccessful += 1
            total += 1

        status = f"""<b><u>Broadcast Completed</u>

Total Users: <code>{total}</code>
Successful: <code>{successful}</code>
Blocked Users: <code>{blocked}</code>
Deleted Accounts: <code>{deleted}</code>
Unsuccessful: <code>{unsuccessful}</code></b>"""

        return await pls_wait.edit(status, parse_mode=ParseMode.HTML)
    else:
        msg = await message.reply(REPLY_ERROR, parse_mode=ParseMode.HTML)
        await asyncio.sleep(8)
        await msg.delete()
