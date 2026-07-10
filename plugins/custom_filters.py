import os
import asyncio
import random
from pyrogram import filters, enums
from pyrogram.enums import ParseMode
from pyrogram.types import Message
from bot import Bot
from config import GEMINI # Importing your key from config like a pro

# ==========================================
# 1. CONFIGURATION (NEW SDK)
# ==========================================

# Import the new SDK
from google import genai

# Initialize the new Client
# (You don't need to define the model here anymore, you pass it in the function)
client = genai.Client(api_key=GEMINI) 

ELP_LINK = "https://t.me/+0YrmrOzS40wzYTU1"

# [Keep your group_message_counters and trigger_responses dictionaries here exactly as they were]

# ==========================================
# 2. AI GENERATION FUNCTION (UPDATED)
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
        # NEW SDK Syntax: Using client.aio for async calls
        response = await client.aio.models.generate_content(
            model='gemini-1.5-flash', # You can also upgrade to 'gemini-2.0-flash' here if you want!
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"AI Generation Error: {e}")
        return "Bhai, mera network thoda slow chal raha hai. Thodi der mein aana! 😵‍💫"

# [Keep your background deletion helper and message handler exactly as they were]
