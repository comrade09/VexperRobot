import re
from pyrogram import Client, filters
from pyrogram.types import Message
from database.videos import save_video_code

# Replace with your actual Dump Channel ID (Must start with -100)
SECRET_KEY = b"84b6f10c7931c890e0e1a967f6515f40192ea62f25608d0f7a75932598be6f2d"
DUMP_CHANNEL_ID = -1003946902565

@Client.on_message(filters.chat(DUMP_CHANNEL_ID) & filters.video,group=3878)
async def auto_save_channel_video(bot: Client, message: Message):
    caption = message.caption or ""
    
    # Scans for 2 letters followed by 4 digits anywhere in the caption
    match = re.search(r"([A-Za-z]{2}\d{4})", caption)
    
    if not match:
        return
        
    question_code = match.group(1).upper()
    await save_video_code(question_code, message.id)
    print(f"Saved Code: {question_code} -> Message ID: {message.id}")
