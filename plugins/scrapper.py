import os
import json
import html
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ParseMode
from bot import Bot
from config import OWNER_ID
from helper_func import subscribed

# Import your database functions
from database.database import update_batch_data, get_all_batches, get_batch

UPLOAD_STATE = {}

# Custom Batch Names Mapping
BATCH_MAP = {
    "5NDPLQ9R": "Master Pro 1",
    "0KFLQAGZ": "Master Pro 3"
}

# --- Helper to prevent HTML format crashes ---
def safe_html(text):
    """Escapes special characters (<, >, &) so they don't break HTML parsing."""
    if not text:
        return ""
    return html.escape(str(text))

# --- 1. JSON Update Command ---
@Bot.on_message(filters.command("update") & filters.private & filters.user(OWNER_ID), group=9253)
async def ask_for_json(client: Bot, message: Message):
    UPLOAD_STATE[message.from_user.id] = True
    await message.reply_text("Please send the JSON file containing the batch updates.")

@Bot.on_message(filters.document & filters.private & filters.user(OWNER_ID), group=9234)
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
                        
        await msg.edit_text(
            "✅ Database updated successfully! All new and previous links have been merged and sorted.",
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        await msg.edit_text(f"❌ Error parsing JSON: <code>{safe_html(str(e))}</code>", parse_mode=ParseMode.HTML)
    finally:
        UPLOAD_STATE[message.from_user.id] = False
        if os.path.exists(file_path):
            os.remove(file_path)


# --- 2. User Batches Menu ---
@Bot.on_message(filters.command("batches") & filters.private, group=3656)
async def batches_command(client: Bot, message: Message):
    batches = await get_all_batches()
    
    if not batches:
        await message.reply_text("No batches are currently available.")
        return

    buttons = []
    for b in batches:
        b_id = b.get("batch_id")
        b_name = BATCH_MAP.get(b_id, b.get("batch_title", f"Batch {b_id}"))
        buttons.append([InlineKeyboardButton(b_name, callback_data=f"bch_{b_id}_0")])
    
    await message.reply_text(
        "📚 <b>Select a Batch:</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.HTML
    )


# --- 3. Teachers Menu (Strictly 2 Columns, 8 Teachers Per Page) ---
@Bot.on_callback_query(filters.regex(r"^bch_([^_]+)(?:_(\d+))?$"), group=3653)
async def show_teachers(client: Bot, callback_query: CallbackQuery):
    batch_id = callback_query.matches[0].group(1)
    
    page_str = callback_query.matches[0].group(2)
    page = int(page_str) if page_str else 0
    
    batch = await get_batch(batch_id)
    if not batch or not batch.get("teachers"):
        return await callback_query.answer("No teachers found for this batch.", show_alert=True)

    all_teachers = batch["teachers"]
    total_teachers = len(all_teachers)
    
    # 8 teachers per page = Exactly 4 rows of 2 columns
    limit = 8 
    skip = page * limit
    page_teachers = all_teachers[skip:skip+limit]

    # Create Buttons
    buttons = []
    row = []
    for i, teacher in enumerate(page_teachers):
        true_idx = skip + i
        raw_name = teacher.get("teacher_name", f"Teacher {true_idx+1}")
        clean_name = raw_name.split("\n")[0].strip()
        
        row.append(InlineKeyboardButton(clean_name, callback_data=f"tch_{batch_id}_{true_idx}_0"))
        
        # When we have 2 buttons in the row, append to main buttons and reset
        if len(row) == 2:
            buttons.append(row)
            row = []
            
    # Add any remaining odd button
    if row:
        buttons.append(row)
        
    # Navigation Buttons for Teachers List
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"bch_{batch_id}_{page-1}"))
    if skip + limit < total_teachers:
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"bch_{batch_id}_{page+1}"))
        
    if nav_buttons:
        buttons.append(nav_buttons)
        
    # Back to Batches
    buttons.append([InlineKeyboardButton("⬅️ Back to Batches", callback_data="back_to_batches")])
    
    batch_name = safe_html(BATCH_MAP.get(batch_id, batch.get("batch_title", batch_id)))

    await callback_query.message.edit_text(
        f"👨‍🏫 <b>Teachers for {batch_name}:</b>\nSelect a teacher to view their classes.",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.HTML
    )


@Bot.on_callback_query(filters.regex(r"^back_to_batches$"), group=4763)
async def back_to_batches_callback(client: Bot, callback_query: CallbackQuery):
    batches = await get_all_batches()
    buttons = []
    for b in batches:
        b_id = b.get("batch_id")
        b_name = BATCH_MAP.get(b_id, b.get("batch_title", f"Batch {b_id}"))
        buttons.append([InlineKeyboardButton(b_name, callback_data=f"bch_{b_id}_0")])
        
    await callback_query.message.edit_text(
        "📚 <b>Select a Batch:</b>",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.HTML
    )


# --- 4. Lectures Menu (Paginated & Safe URLs) ---
@Bot.on_callback_query(filters.regex(r"^tch_(.*)_(.*)_(.*)"), group=8547)
async def show_lectures(client: Bot, callback_query: CallbackQuery):
    batch_id = callback_query.matches[0].group(1)
    teacher_idx = int(callback_query.matches[0].group(2))
    page = int(callback_query.matches[0].group(3))
    
    batch = await get_batch(batch_id)
    if not batch or teacher_idx >= len(batch.get("teachers", [])):
        return await callback_query.answer("Data not found.", show_alert=True)
        
    teacher = batch["teachers"][teacher_idx]
    teacher_name = safe_html(teacher.get("teacher_name", "Teacher").split("\n")[0].strip())
    all_lectures = teacher.get("lectures", [])
    
    limit = 5
    skip = page * limit
    page_lectures = all_lectures[skip:skip+limit]
    
    if not page_lectures:
        return await callback_query.answer("No lectures found.", show_alert=True)

    batch_name = safe_html(BATCH_MAP.get(batch_id, batch.get("batch_title", batch_id)))
    
    text = f"<b>📖 Lectures by {teacher_name}</b>\n<b>Batch:</b> {batch_name}\n\n"
    
    for lec in page_lectures:
        lec_date = safe_html(lec.get('date', 'Unknown'))
        lec_title = safe_html(lec.get('lecture_title', 'Untitled'))
        
        text += f"🗓 <b>Date:</b> <code>{lec_date}</code>\n"
        text += f"📝 <b>Title:</b> <code>{lec_title}</code>\n"
        
        vid_url = lec.get("video_url", "")
        pdf_url = lec.get("pdf_url", "")
        
        links = []
        # In HTML mode, we use true <a href='...'> tags for clickable links
        if vid_url and vid_url.startswith("http"):
            links.append(f"🎬 <a href='{vid_url}'>Watch Video</a>")
        if pdf_url and pdf_url.startswith("http"):
            links.append(f"📥 <a href='{pdf_url}'>Download PDF</a>")
            
        if links:
            text += " | ".join(links) + "\n\n"
        else:
            text += "🚫 <i>No links available</i>\n\n"
        
    # Navigation Buttons for Lectures list
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"tch_{batch_id}_{teacher_idx}_{page-1}"))
    if skip + limit < len(all_lectures):
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"tch_{batch_id}_{teacher_idx}_{page+1}"))
        
    buttons = []
    if nav_buttons:
        buttons.append(nav_buttons)
        
    # Go back to the exact teacher list (page 0)
    buttons.append([InlineKeyboardButton("⬅️ Back to Teachers", callback_data=f"bch_{batch_id}_0")])

    await callback_query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True,
        parse_mode=ParseMode.HTML
    )
