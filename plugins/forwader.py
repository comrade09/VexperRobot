import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError, SessionPasswordNeededError

# Import your database functions
from database.database import save_session, get_session, delete_session

# Configuration for the Telethon User Client
API_ID = 13678305
API_HASH = 'a5d9be6f810f31e5c56bad6eebbd7ba8'

# Dictionaries to store the conversational state of users
FORWARD_STATE = {}
LOGIN_STATE = {}

# Commands that should NEVER be swallowed as step-input text.
# Add every command your bot has, not just these three.
RESERVED_COMMANDS = filters.command(
    ["login", "forward", "logout_session", "cancel", "start", "help"]
)


def parse_link(link: str):
    """Extracts the chat ID/username and message ID from a Telegram message link."""
    parts = link.strip('/').split('/')
    msg_id = int(parts[-1])

    if 'c' in parts:
        chat_id = int('-100' + parts[-2])
    else:
        chat_id = parts[-2]

    return chat_id, msg_id


async def _cleanup_login_state(user_id: int):
    state = LOGIN_STATE.pop(user_id, None)
    if state and state.get("client"):
        try:
            await state["client"].disconnect()
        except Exception:
            pass


def _cleanup_forward_state(user_id: int):
    FORWARD_STATE.pop(user_id, None)


# ==========================================
# 0. CANCEL COMMAND — lets a user escape any stuck state
# ==========================================
@Client.on_message(filters.command("cancel") & filters.private, group=486)
async def cancel_command(client: Client, message: Message):
    user_id = message.from_user.id
    was_stuck = user_id in LOGIN_STATE or user_id in FORWARD_STATE
    await _cleanup_login_state(user_id)
    _cleanup_forward_state(user_id)
    if was_stuck:
        await message.reply_text("❎ Cancelled. You can start again with /login or /forward.")
    else:
        await message.reply_text("Nothing in progress to cancel.")


# ==========================================
# 1. LOGIN COMMAND FLOW
# ==========================================
@Client.on_message(filters.command("login") & filters.private, group=487)
async def start_login_command(client: Client, message: Message):
    user_id = message.from_user.id

    saved_session = await get_session(user_id)
    if saved_session:
        await message.reply_text(
            "✅ You are already logged in! Use `/forward` to start copying messages.\n\n"
            "Use `/logout_session` if you want to log in with a different account."
        )
        return

    # Wipe any stale/half-finished login before starting a new one
    await _cleanup_login_state(user_id)

    LOGIN_STATE[user_id] = {"step": "WAIT_PHONE"}
    await message.reply_text(
        "📱 **Telegram Login**\n\n"
        "Please send your phone number with the country code.\n"
        "Example: `+919876543210` or `+1234567890`\n\n"
        "Send /cancel anytime to abort."
    )


@Client.on_message(filters.command("logout_session") & filters.private, group=4532)
async def logout_session_command(client: Client, message: Message):
    await delete_session(message.from_user.id)
    await _cleanup_login_state(message.from_user.id)
    _cleanup_forward_state(message.from_user.id)
    await message.reply_text("🗑 Your saved String Session has been deleted from the database. You are now logged out.")


# ==========================================
# 2. FORWARD COMMAND FLOW
# ==========================================
@Client.on_message(filters.command("forward") & filters.private, group=993)
async def start_forward_command(client: Client, message: Message):
    user_id = message.from_user.id

    saved_session = await get_session(user_id)

    if not saved_session:
        await message.reply_text(
            "❌ You are not logged in.\n\nPlease send the `/login` command to authenticate your Telegram account first."
        )
        return

    # Wipe any stale/half-finished forward flow before starting a new one
    _cleanup_forward_state(user_id)

    FORWARD_STATE[user_id] = {"step": "WAIT_START", "session": saved_session}
    await message.reply_text("✅ Ready!\n\n🔗 Please send the **START** message link:\n\n(Send /cancel anytime to abort.)")


# ==========================================
# 3. TEXT STEP HANDLER (Handles both Login & Forward)
#    filters.text & ~RESERVED_COMMANDS  ->  commands NEVER get
#    misread as phone/OTP/password/link input.
# ==========================================
@Client.on_message(filters.text & filters.private & ~RESERVED_COMMANDS, group=504)
async def handle_conversation_steps(client: Client, message: Message):
    user_id = message.from_user.id
    text = message.text.strip()

    # -------------------------
    # LOGIN STATE HANDLING
    # -------------------------
    if user_id in LOGIN_STATE:
        state = LOGIN_STATE[user_id]
        step = state.get("step")

        if step == "WAIT_PHONE":
            status_msg = await message.reply_text("⏳ Connecting to Telegram...")
            tc = TelegramClient(StringSession(), API_ID, API_HASH)
            await tc.connect()

            try:
                sent_code = await tc.send_code_request(text)
                state["client"] = tc
                state["phone"] = text
                state["phone_code_hash"] = sent_code.phone_code_hash
                state["step"] = "WAIT_OTP"

                await status_msg.edit_text(
                    "📩 **OTP Sent!**\n\n"
                    "Telegram has sent a code to your app.\n"
                    "⚠️ **IMPORTANT:** Please enter the code with spaces between numbers to avoid Telegram blocking the login.\n"
                    "Example: If code is `12345`, send it as `1 2 3 4 5`"
                )
            except Exception as e:
                await status_msg.edit_text(f"❌ Failed to send code: {e}")
                await tc.disconnect()
                LOGIN_STATE.pop(user_id, None)

        elif step == "WAIT_OTP":
            status_msg = await message.reply_text("⏳ Verifying OTP...")
            tc = state["client"]
            otp_code = text.replace(" ", "").replace("-", "")

            try:
                await tc.sign_in(state["phone"], otp_code, phone_code_hash=state["phone_code_hash"])
                session_str = tc.session.save()
                await save_session(user_id, session_str)
                await tc.disconnect()
                LOGIN_STATE.pop(user_id, None)
                await status_msg.edit_text(
                    "✅ **Login Successful!**\nYour session has been securely saved to the database.\n\n"
                    "You can now use the `/forward` command."
                )
            except SessionPasswordNeededError:
                state["step"] = "WAIT_PASSWORD"
                await status_msg.edit_text("🔐 **Two-Step Verification (2FA) is enabled.**\n\nPlease send your account password:")
            except Exception as e:
                await status_msg.edit_text(f"❌ Failed to verify code: {e}\n\nPlease try `/login` again.")
                await tc.disconnect()
                LOGIN_STATE.pop(user_id, None)

        elif step == "WAIT_PASSWORD":
            status_msg = await message.reply_text("⏳ Verifying Password...")
            tc = state["client"]

            try:
                await tc.sign_in(password=text)
                session_str = tc.session.save()
                await save_session(user_id, session_str)
                await tc.disconnect()
                LOGIN_STATE.pop(user_id, None)
                await status_msg.edit_text(
                    "✅ **Login Successful!**\nYour session has been securely saved to the database.\n\n"
                    "You can now use the `/forward` command."
                )
            except Exception as e:
                await status_msg.edit_text(f"❌ Incorrect Password or Error: {e}\n\nPlease try `/login` again.")
                await tc.disconnect()
                LOGIN_STATE.pop(user_id, None)

        return

    # -------------------------
    # FORWARD STATE HANDLING
    # -------------------------
    if user_id in FORWARD_STATE:
        state = FORWARD_STATE[user_id]
        step = state.get("step")

        try:
            if step == "WAIT_START":
                state["start_link"] = text
                state["step"] = "WAIT_END"
                await message.reply_text("🔗 Please send the **LAST (END)** message link:")

            elif step == "WAIT_END":
                state["end_link"] = text
                state["step"] = "WAIT_DEST"
                await message.reply_text(
                    "🎯 Please send the **DESTINATION**.\n\n"
                    "For normal channels/groups, send ID or Username (e.g., `-100123...`).\n"
                    "For **Topics/Forums**, send with format: `GroupName -100...:TopicID`\n"
                    "(e.g., `Lectures 1 -1003715781387:4610`)"
                )

            elif step == "WAIT_DEST":
                parts = text.split()
                last_part = parts[-1]
                state["reply_to"] = None

                if ":" in last_part:
                    chat_part, topic_part = last_part.split(":", 1)
                    try:
                        state["dest"] = int(chat_part)
                    except ValueError:
                        state["dest"] = chat_part
                    state["reply_to"] = int(topic_part)
                else:
                    try:
                        state["dest"] = int(last_part)
                    except ValueError:
                        state["dest"] = last_part

                # Re-check the session right before launching — it may have
                # been deleted (e.g. via /logout_session) since /forward was issued.
                current_session = await get_session(user_id)
                if not current_session:
                    await message.reply_text(
                        "❌ You're no longer logged in. Please /login again before forwarding."
                    )
                    _cleanup_forward_state(user_id)
                    return
                state["session"] = current_session

                await message.reply_text("⏳ Initializing User Client. Please wait...")
                asyncio.create_task(run_forwarder(client, message, state))
                _cleanup_forward_state(user_id)

        except Exception as e:
            # Never leave the user stuck in a dead state on an unexpected error
            await message.reply_text(f"❌ Something went wrong: {e}\n\nUse /forward to start over.")
            _cleanup_forward_state(user_id)

        return


# ==========================================
# 4. BACKGROUND FORWARDER LOGIC
# ==========================================
async def run_forwarder(bot: Client, message: Message, state: dict):
    status_msg = await message.reply_text("🔄 Connecting to Telegram via String Session...")

    user_client = TelegramClient(StringSession(state["session"]), API_ID, API_HASH)

    try:
        await user_client.connect()
        if not await user_client.is_user_authorized():
            await status_msg.edit_text("❌ String Session is invalid or expired. Please generate a new one using `/logout_session` then `/login`.")
            return

    except Exception as e:
        await status_msg.edit_text(f"❌ Failed to login: {e}")
        return

    try:
        source_chat, start_id = parse_link(state["start_link"])
        _, end_id = parse_link(state["end_link"])

        if start_id > end_id:
            start_id, end_id = end_id, start_id

        dest_chat = state["dest"]
        topic_id = state.get("reply_to")

        total_msgs = end_id - start_id + 1
        processed_count = 0
        success_count = 0

        await status_msg.edit_text(f"⏳ Forwarding messages...\n\n📈 Progress: **0** out of **{total_msgs}** processed.")

        for msg_id in range(start_id, end_id + 1):
            try:
                msg = await user_client.get_messages(source_chat, ids=msg_id)
                if msg:
                    await user_client.send_message(dest_chat, msg, reply_to=topic_id)
                    success_count += 1
                await asyncio.sleep(1.5)

            except FloodWaitError as e:
                await status_msg.edit_text(f"⚠️ Rate limited. Pausing for {e.seconds} seconds...\n\n(Paused at {processed_count}/{total_msgs})")
                await asyncio.sleep(e.seconds)
                msg = await user_client.get_messages(source_chat, ids=msg_id)
                if msg:
                    await user_client.send_message(dest_chat, msg, reply_to=topic_id)
                    success_count += 1

            except Exception as e:
                print(f"Error skipping ID {msg_id}: {e}")

            processed_count += 1

            if processed_count % 5 == 0 or processed_count == total_msgs:
                try:
                    await status_msg.edit_text(
                        f"⏳ Forwarding in progress...\n\n"
                        f"📈 **Progress:** {processed_count} out of {total_msgs} processed.\n"
                        f"✅ **Successful:** {success_count}\n"
                        f"🎯 **Destination:** `{dest_chat}`" + (f" (Topic: `{topic_id}`)" if topic_id else "")
                    )
                except Exception:
                    pass

        await status_msg.edit_text(
            f"🎉 **Finished!**\n\n"
            f"✅ Successfully cloned **{success_count}** out of **{total_msgs}** messages.\n"
            f"🎯 Delivered to: `{dest_chat}`" + (f" Topic `{topic_id}`" if topic_id else "")
        )

    except Exception as e:
        await status_msg.edit_text(f"❌ An error occurred during forwarding: {e}")

    finally:
        await user_client.disconnect()
