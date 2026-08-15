import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError

# Import the DB functions
from database.database import save_session, get_session, delete_session

# Configuration for the Telethon User Client
API_ID = 13678305
API_HASH = 'a5d9be6f810f31e5c56bad6eebbd7ba8'

# Dictionary to store the conversational state of users
FORWARD_STATE = {}

def parse_link(link: str):
    """Extracts the chat ID/username and message ID from a Telegram message link."""
    parts = link.strip('/').split('/')
    msg_id = int(parts[-1])

    if 'c' in parts:
        chat_id = int('-100' + parts[-2])
    else:
        chat_id = parts[-2]

    return chat_id, msg_id

# --- 1. Start Command ---
@Client.on_message(filters.command("forward") & filters.private)
async def start_forward_command(client: Client, message: Message):
    user_id = message.from_user.id
    
    # Check if the user already has a saved session in MongoDB
    saved_session = await get_session(user_id)
    
    if saved_session:
        FORWARD_STATE[user_id] = {"step": "WAIT_START", "session": saved_session}
        await message.reply_text("✅ Saved String Session found!\n\n🔗 Please send the **START** message link:")
    else:
        FORWARD_STATE[user_id] = {"step": "WAIT_SESSION"}
        await message.reply_text(
            "❌ No String Session found in the database.\n\n"
            "Please send your **Telethon String Session** to continue:"
        )

# Command to clear saved session
@Client.on_message(filters.command("logout_session") & filters.private)
async def logout_session_command(client: Client, message: Message):
    await delete_session(message.from_user.id)
    if message.from_user.id in FORWARD_STATE:
        del FORWARD_STATE[message.from_user.id]
    await message.reply_text("🗑 Your saved String Session has been deleted from the database.")

# --- 2. Step-by-Step Conversation Handler ---
@Client.on_message(filters.text & filters.private, group=50)
async def handle_forward_steps(client: Client, message: Message):
    user_id = message.from_user.id
    
    if user_id not in FORWARD_STATE:
        return
        
    state = FORWARD_STATE[user_id]
    step = state.get("step")
    text = message.text.strip()
    
    if step == "WAIT_SESSION":
        await save_session(user_id, text)
        state["session"] = text
        state["step"] = "WAIT_START"
        await message.reply_text("✅ Session saved to MongoDB successfully!\n\n🔗 Please send the **START** message link:")
        
    elif step == "WAIT_START":
        state["start_link"] = text
        state["step"] = "WAIT_END"
        await message.reply_text("🔗 Please send the **LAST (END)** message link:")
        
    elif step == "WAIT_END":
        state["end_link"] = text
        state["step"] = "WAIT_DEST"
        await message.reply_text(
            "🎯 Please send the **DESTINATION**.\n\n"
            "For normal channels, send ID or Username (e.g., `-100123...`).\n"
            "For **Topics/Forums**, send with format: `TopicName -100...:TopicID`\n"
            "(e.g., `Lectures 1 -1003715781387:4610`)"
        )
        
    elif step == "WAIT_DEST":
        # Parse the text to extract topic ID if present
        parts = text.split()
        last_part = parts[-1] # Getting the ID section at the end
        
        state["reply_to"] = None # Default: No topic ID
        
        if ":" in last_part:
            chat_part, topic_part = last_part.split(":", 1)
            try:
                state["dest"] = int(chat_part)
                state["reply_to"] = int(topic_part)
            except ValueError:
                state["dest"] = chat_part
                state["reply_to"] = int(topic_part)
        else:
            try:
                state["dest"] = int(last_part)
            except ValueError:
                state["dest"] = last_part
            
        await message.reply_text("⏳ Initializing User Client. Please wait...")
        asyncio.create_task(run_forwarder(client, message, state))
        
        del FORWARD_STATE[user_id]


# --- 3. The Core Forwarding Logic ---
async def run_forwarder(bot: Client, message: Message, state: dict):
    user_id = message.from_user.id
    status_msg = await message.reply_text("🔄 Connecting to Telegram via String Session...")
    
    user_client = TelegramClient(StringSession(state["session"]), API_ID, API_HASH)
    
    try:
        await user_client.connect()
        if not await user_client.is_user_authorized():
            await status_msg.edit_text("❌ String Session is invalid or expired. Please generate a new one and use /logout_session.")
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
        topic_id = state.get("reply_to") # Will be None if standard channel, or Topic ID for forums
        
        total_msgs = end_id - start_id + 1
        processed_count = 0
        success_count = 0
        
        await status_msg.edit_text(f"⏳ Forwarding messages...\n\n📈 Progress: **0** out of **{total_msgs}** processed.")

        for msg_id in range(start_id, end_id + 1):
            try:
                msg = await user_client.get_messages(source_chat, ids=msg_id)
                
                if msg:
                    # In Telethon, sending with reply_to = topic_id correctly sends it into the topic thread
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
            
            # Update progress every 5 messages to avoid Telegram floodwait for message edits
            if processed_count % 5 == 0 or processed_count == total_msgs:
                try:
                    await status_msg.edit_text(
                        f"⏳ Forwarding in progress...\n\n"
                        f"📈 **Progress:** {processed_count} out of {total_msgs} processed.\n"
                        f"✅ **Successful:** {success_count}\n"
                        f"🎯 **Destination:** `{dest_chat}`" + (f" (Topic: `{topic_id}`)" if topic_id else "")
                    )
                except Exception:
                    # Ignore MessageNotModified errors
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
