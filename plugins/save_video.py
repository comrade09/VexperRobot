import re
from pyrogram import Client, filters
from pyrogram.types import Message
from database.videos import save_video_code

DUMP_CHANNEL_ID = -1003946902565

@Client.on_message(filters.chat(DUMP_CHANNEL_ID) & (filters.video | filters.document),group=8643)
async def auto_save_channel_video(bot: Client, message: Message):
    caption = message.caption or message.text or ""
    
    match = re.search(r"([a-zA-Z]{2}\d{4})", caption)
    
    if not match:
        return
        
    question_code = match.group(1).upper()
    await save_video_code(question_code, message.id)
    
    print(f"✅ Extracted & Saved Code: {question_code} -> Message ID: {message.id}")
