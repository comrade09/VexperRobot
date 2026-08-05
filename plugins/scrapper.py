import os
import json
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from bot import Bot
from config import OWNER_ID
from helper_func import subscribed

# Import your newly refactored database functions
from database import update_batch_data, get_all_batches, get_batch

UPLOAD_STATE = {}

# Custom Batch Names Mapping
BATCH_MAP = {
    "5NDPLQ9R": "Master Pro 1",
    "0KFLQAGZ": "Master Pro 3"
}

# --- 1. JSON Update Command ---
@Bot.on_message(filters.command("update") & filters.private & filters.user(OWNER_ID),group=9253)
async def ask_for_json(client: Bot, message: Message):
    UPLOAD_STATE[message.from_user.id] = True
    await message.reply_text("Please send the JSON file containing the batch updates.")

@Bot.on_message(filters.document & filters.private & filters.user(OWNER_ID),group=9234)
async def handle_json_file(client: Bot, message: Message):
    if not UPLOAD_STATE.get(message.from_user.id):
        return
    
    if not message.document.file_name.endswith(".json"):
        await message.reply_text("Please send a valid .json file.")
        return

    msg = await message.reply_text("Downloading and parsing JSON into Database...")
    file_path = await message.download()
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        batches = data if isinstance(data, list) else [data]
        
        for batch in batches:
            # Sort lectures for each teacher so newest date is always index 0
            for teacher in batch.get("teachers", []):
                lectures = teacher.get("lectures", [])
                
                def sort_by_date(lec):
                    try:
                        return datetime.strptime(lec.get("date", ""), "%b %d, %Y").timestamp()
                    except ValueError:
                        return 0
                        
                teacher["lectures"] = sorted(lectures, key=sort_by_date, reverse=True)

            await update_batch_data(
                batch_id=batch.get("batch_id", ""),
                batch_title=batch.get("batch_title", f"Batch {batch.get('batch_id')}"),
                batch_url=batch.get("batch_url", ""),
                teachers=batch.get("teachers", []),
                last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
                        
        await msg.edit_text("✅ Database updated successfully! All new and previous links have been merged and sorted.")
        
    except Exception as e:
        await msg.edit_text(f"❌ Error parsing JSON: `{str(e)}`")
    finally:
        UPLOAD_STATE[message.from_user.id] = False
        if os.path.exists(file_path):
            os.remove(file_path)

# --- 2. User Batches Menu ---
@Bot.on_message(filters.command("batches") & filters.private,group=3656)
async def batches_command(client: Bot, message: Message):
    batches = await get_all_batches()
    
    if not batches:
        await message.reply_text("No batches are currently available.")
        return

    buttons = []
    for b in batches:
        b_id = b.get("batch_id")
        b_name = BATCH_MAP.get(b_id, b.get("batch_title", f"Batch {b_id}"))
        buttons.append([InlineKeyboardButton(b_name, callback_data=f"bch_{b_id}")])
    
    await message.reply_text(
        "📚 **Select a Batch:**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# --- 3. Teachers Menu ---
@Bot.on_callback_query(filters.regex(r"^bch_(.*)"),group=3653)
async def show_teachers(client: Bot, callback_query: CallbackQuery):
    batch_id = callback_query.matches[0].group(1)
    batch = await get_batch(batch_id)
    
    if not batch or not batch.get("teachers"):
        await callback_query.answer("No teachers found for this batch.", show_alert=True)
        return

    buttons = []
    # Using index `idx` to keep callback data short and avoid 64-byte limit errors
    for idx, teacher in enumerate(batch["teachers"]):
        raw_name = teacher.get("teacher_name", f"Teacher {idx+1}")
        clean_name = raw_name.split("\n")[0].strip()
        buttons.append([InlineKeyboardButton(clean_name, callback_data=f"tch_{batch_id}_{idx}_0")])
    
    buttons.append([InlineKeyboardButton("⬅️ Back to Batches", callback_data="back_to_batches")])
    batch_name = BATCH_MAP.get(batch_id, batch.get("batch_title", batch_id))

    await callback_query.message.edit_text(
        f"👨‍🏫 **Teachers for {batch_name}:**\nSelect a teacher to view their classes.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Bot.on_callback_query(filters.regex(r"^back_to_batches$"),group=4763)
async def back_to_batches_callback(client: Bot, callback_query: CallbackQuery):
    batches = await get_all_batches()
    buttons = []
    for b in batches:
        b_id = b.get("batch_id")
        b_name = BATCH_MAP.get(b_id, b.get("batch_title", f"Batch {b_id}"))
        buttons.append([InlineKeyboardButton(b_name, callback_data=f"bch_{b_id}")])
        
    await callback_query.message.edit_text(
        "📚 **Select a Batch:**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# --- 4. Lectures Menu (Paginated & Sorted) ---
@Bot.on_callback_query(filters.regex(r"^tch_(.*)_(.*)_(.*)"),group=8547)
async def show_lectures(client: Bot, callback_query: CallbackQuery):
    batch_id = callback_query.matches[0].group(1)
    teacher_idx = int(callback_query.matches[0].group(2))
    page = int(callback_query.matches[0].group(3))
    
    batch = await get_batch(batch_id)
    if not batch or teacher_idx >= len(batch.get("teachers", [])):
        return await callback_query.answer("Data not found.", show_alert=True)
        
    teacher = batch["teachers"][teacher_idx]
    teacher_name = teacher.get("teacher_name", "Teacher").split("\n")[0].strip()
    all_lectures = teacher.get("lectures", [])
    
    limit = 5
    skip = page * limit
    page_lectures = all_lectures[skip:skip+limit]
    
    if not page_lectures:
        return await callback_query.answer("No lectures found.", show_alert=True)

    batch_name = BATCH_MAP.get(batch_id, batch.get("batch_title", batch_id))
    text = f"**📖 Lectures by {teacher_name}**\n**Batch:** {batch_name}\n\n"
    
    for lec in page_lectures:
        text += f"🗓 **Date:** `{lec.get('date', 'Unknown')}`\n"
        text += f"📝 **Title:** `{lec.get('lecture_title', 'Untitled')}`\n"
        text += f"🎬 [Watch Video]({lec.get('video_url')}) | 📥 [Download PDF]({lec.get('pdf_url')})\n\n"
        
    # Navigation Buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"tch_{batch_id}_{teacher_idx}_{page-1}"))
    if skip + limit < len(all_lectures):
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"tch_{batch_id}_{teacher_idx}_{page+1}"))
        
    buttons = []
    if nav_buttons:
        buttons.append(nav_buttons)
        
    buttons.append([InlineKeyboardButton("⬅️ Back to Teachers", callback_data=f"bch_{batch_id}")])

    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )
