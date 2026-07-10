import os
import asyncio
import random
import google.generativeai as genai
from pyrogram import filters, enums
from pyrogram.enums import ParseMode
from pyrogram.types import Message
from bot import Bot # Assuming this is your custom Client instance
# from config import OWNER_ID, BOT_USERNM # Un-comment if you need these later
from config import GEMINI
# ==========================================
# 1. CONFIGURATION
# ==========================================

# Configure the Google Gemini AI Model
genai.configure(api_key=GEMINI)
model = genai.GenerativeModel('gemini-1.5-flash')

ELP_LINK = "https://t.me/+0YrmrOzS40wzYTU1"

# Dictionary to keep track of message counts per chat
group_message_counters = {}

# Dictionary holding fallback stickers for triggers
trigger_responses = {
    "thank": {"sticker_id": "CAACAgUAAxkBAAIM2WVuXSKjb5hD7Ira3MNtHkQvvfyLAALFEQACFORxV6azoG5YB84EHgQ"},
    "thanks": {"sticker_id": "CAACAgUAAxkBAAIM2WVuXSKjb5hD7Ira3MNtHkQvvfyLAALFEQACFORxV6azoG5YB84EHgQ"},
    "elp": {"sticker_id": "YOUR_ELP_STICKER_ID"},     # 🔴 ADD YOUR STICKER IDs HERE
    "hello": {"sticker_id": "YOUR_HELLO_STICKER_ID"},
    "hi": {"sticker_id": "YOUR_HI_STICKER_ID"},
    "sorry": {"sticker_id": "YOUR_SORRY_STICKER_ID"},
    "gm": {"sticker_id": "YOUR_GM_STICKER_ID"},
    "gn": {"sticker_id": "YOUR_GN_STICKER_ID"}
}

# ==========================================
# 2. AI GENERATION FUNCTION
# ==========================================

async def generate_dynamic_reply(trigger_word: str, user_text: str) -> str:
    """Makes the AI 'think' and generate a fresh Hinglish response based on a random mood."""
    
    moods = ["roast", "witty", "cute", "default_genz"]
    current_mood = random.choice(moods)
    
    if current_mood == "roast":
        persona = "a savage, ruthless, but playful roasting bot. Roast the user playfully for their message."
    elif current_mood == "witty":
        persona = "a clever, cheeky, and mischievous bot. Use smart, PG-13 witty humor and harmless double-meaning wordplay (keep it strictly safe for work)."
    elif current_mood == "cute":
        persona = "an incredibly sweet, wholesome, and overly affectionate bot. Reply with pure cuteness and soft vibes."
    else:
        persona = "a highly energetic, humorous, and sarcastic loyal friend."

    if trigger_word == "random_100":
        prompt = f"""
        Act as {persona} You speak in a mix of Hindi and English (Hinglish) using Gen-Z slang.
        You are randomly chiming into the group chat to surprise everyone after 100 messages. 
        The user just sent this random message: "{user_text}"
        Write a 1-2 sentence unique reply to their message in your current mood, making a grand entrance.
        Do not use quotation marks around your response. Use emojis.
        """
    else:
        elp_context = f" Include this invite link naturally at the end: [Tap To Join]({ELP_LINK})" if trigger_word == "elp" else ""
        prompt = f"""
        Act as {persona} You speak in a mix of Hindi and English (Hinglish) using Gen-Z slang.
        The user sent this message: "{user_text}"
        The trigger word detected was: "{trigger_word}"
        Write a 1-2 sentence unique reply addressing the user in your current mood.{elp_context}
        Do not use quotation marks around your response. Use emojis.
        """
    
    try:
        # Use native async AI generation
        response = await model.generate_content_async(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"AI Generation Error: {e}")
        return "Bhai, mera network thoda slow chal raha hai. Thodi der mein aana! 😵‍💫"

# ==========================================
# 3. BACKGROUND DELETION HELPER
# ==========================================

async def delete_after_delay(message: Message, delay: int):
    """Deletes a message after a specified delay without blocking the bot."""
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception as e:
        print(f"Failed to delete message (it might have been deleted manually): {e}")

# ==========================================
# 4. MESSAGE HANDLER
# ==========================================

@Bot.on_message(filters.chat(-1001325358566))
async def handle_messages(client, message: Message):
    if not message.text:
        return

    chat_id = message.chat.id
    
    # 1. Update counter
    if chat_id not in group_message_counters:
        group_message_counters[chat_id] = 0
    group_message_counters[chat_id] += 1
    current_count = group_message_counters[chat_id]
    
    msg_words = message.text.lower().split()
    triggered = False
    
    # 2. Check Triggers
    for trigger_word, response_data in trigger_responses.items():
        if trigger_word.lower() in msg_words:
            triggered = True
            
            # 50% chance for text, 50% chance for sticker
            send_text = random.choice([True, False])

            if send_text:
                try:
                    await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
                    chosen_text = await generate_dynamic_reply(trigger_word, message.text)
                    m = await message.reply_text(chosen_text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
                    
                    # Schedule deletion in the background
                    asyncio.create_task(delete_after_delay(m, 60))
                except Exception as e:
                    print(f"Error sending text reply: {e}")
            else:
                sticker_id = response_data.get("sticker_id", "")
                if sticker_id:
                    try:
                        await message.reply_sticker(sticker_id)
                    except Exception as e:
                        print(f"Error sending sticker: {e}")
            
            break # Stop after finding the first trigger word

    # 3. 100th Message Logic
    if not triggered and current_count % 100 == 0:
        try:
            await client.send_chat_action(chat_id, enums.ChatAction.TYPING)
            chosen_text = await generate_dynamic_reply("random_100", message.text)
            m = await message.reply_text(chosen_text, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
            
            # Schedule deletion in the background
            asyncio.create_task(delete_after_delay(m, 60))
        except Exception as e:
             print(f"Error on 100th message generation: {e}")
