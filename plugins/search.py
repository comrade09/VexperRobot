import re
import time
import hmac
import hashlib
import base64
import json
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.videos import get_video_message_id

STREAM_DOMAIN = "https://stable-meggy-coderkadin-f41f2942.koyeb.app"
SECRET_KEY = b"84b6f10c7931c890e0e1a967f6515f40192ea62f25608d0f7a75932598be6f2d"

def generate_expiring_link(message_id: int) -> str:
    expire_time = int(time.time()) + 900
    
    payload = {"mid": message_id, "exp": expire_time}
    payload_bytes = json.dumps(payload).encode("utf-8")
    encoded_payload = base64.urlsafe_b64encode(payload_bytes).decode("utf-8").rstrip("=")
    
    signature = hmac.new(SECRET_KEY, encoded_payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{STREAM_DOMAIN}/watch?data={encoded_payload}&sig={signature}"

@Client.on_message(filters.command(["search"]) & filters.private,group=3838)
async def search_question_code(bot: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("⚠️ **Format:** `/search DB0149`")
        return
        
    question_code = message.command[1].upper()
    
    if not re.match(r"^[A-Z]{2}\d{4}$", question_code):
        await message.reply_text("❌ **Invalid Code!** Must be 2 letters + 4 digits (e.g., DB0149).")
        return
        
    message_id = await get_video_message_id(question_code)
    
    if not message_id:
        await message.reply_text(f"❌ **Not Found:** No video saved for code `{question_code}`.")
        return
        
    stream_url = generate_expiring_link(message_id)
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎥 Watch Video", url=stream_url)]
    ])
    
    await message.reply_text(
        text=f"✅ **Found Video for {question_code}**\n\n⏳ *This link will expire in 15 minutes.*",
        reply_markup=keyboard
    )
