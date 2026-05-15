import os
import json
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from pyrogram.enums import ParseMode
from bot import Bot  # Standard import for VexperRobot/Voltaic structure

# --- Path Configuration ---
# CURRENT_DIR is the absolute path to the 'plugins' folder
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(CURRENT_DIR, "qbank_data.json")
IMAGE_BASE_DIR = os.path.join(CURRENT_DIR, "qbank_images")

# Load data on startup
if os.path.exists(JSON_PATH):
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            QBANK_DATA = json.load(f)
    except Exception as e:
        print(f"Error loading QBank JSON: {e}")
        QBANK_DATA = {"chapters": []}
else:
    QBANK_DATA = {"chapters": []}

@Bot.on_message(filters.command('qbank') & filters.private ,group=9898983)
async def qbank_start(bot: Bot, message: Message):
    if not QBANK_DATA.get("chapters"):
        await message.reply_text("❌ **Error:** `qbank_data.json` not found or empty in the plugins folder.")
        return
        
    buttons = []
    for idx, chapter in enumerate(QBANK_DATA["chapters"]):
        # Callback format: qb_chap_{chapter_index}_{question_index}
        buttons.append([
            InlineKeyboardButton(
                chapter["chapter_name"], 
                callback_data=f"qb_chap_{idx}_0"
            )
        ])
    
    await message.reply_text(
        text="📚 **Microbiology QBank**\n\nSelect a chapter to begin your practice session:",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.MARKDOWN
    )

async def send_qbank_question(callback_query, chap_idx, q_idx):
    chapter = QBANK_DATA["chapters"][chap_idx]
    
    if q_idx >= len(chapter["questions"]):
        await callback_query.answer("🎉 Congratulations! You've finished this chapter.", show_alert=True)
        return

    question = chapter["questions"][q_idx]
    
    # Construct Message Text
    msg_text = f"📑 **Chapter:** {chapter['chapter_name']}\n"
    msg_text += f"❓ **Question {question.get('q_number', 'N/A')}**\n\n"
    msg_text += f"{question.get('text', '')}\n\n"
    
    options = question.get("options", {})
    for key in ["A", "B", "C", "D"]:
        val = options.get(key)
        if val:
            msg_text += f"**{key}.** {val}\n"

    # Navigation buttons (A, B, C, D)
    keyboard = [
        [
            InlineKeyboardButton("A", callback_data=f"qb_ans_{chap_idx}_{q_idx}_A"),
            InlineKeyboardButton("B", callback_data=f"qb_ans_{chap_idx}_{q_idx}_B"),
            InlineKeyboardButton("C", callback_data=f"qb_ans_{chap_idx}_{q_idx}_C"),
            InlineKeyboardButton("D", callback_data=f"qb_ans_{chap_idx}_{q_idx}_D")
        ]
    ]

    # Image Logic
    raw_img_path = question.get("image")
    if raw_img_path:
        # Extract filename (e.g. ch1_q1.jpeg) and join with absolute plugin path
        img_filename = os.path.basename(raw_img_path)
        full_img_path = os.path.join(IMAGE_BASE_DIR, img_filename)
        
        if os.path.exists(full_img_path):
            # If the current message has a photo, we edit the media to avoid flicker
            # However, Pyrogram's edit_message_media is often cleaner than delete/reply.
            # Using reply/delete here for compatibility with various Pyrogram versions.
            await callback_query.message.reply_photo(
                photo=full_img_path,
                caption=msg_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN
            )
            await callback_query.message.delete()
            return

    # Fallback to text if no image exists or is missing
    if callback_query.message.photo:
        await callback_query.message.reply_text(
            text=msg_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
        await callback_query.message.delete()
    else:
        await callback_query.message.edit_text(
            text=msg_text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )

@Bot.on_callback_query(filters.regex(r"^qb_chap_(\d+)_(\d+)$"),group=383872837)
async def qb_nav_callback(bot: Bot, callback_query: CallbackQuery):
    chap_idx, q_idx = map(int, callback_query.matches[0].groups())
    await send_qbank_question(callback_query, chap_idx, q_idx)

@Bot.on_callback_query(filters.regex(r"^qb_ans_(\d+)_(\d+)_([A-D])$"),group=37673545)
async def qb_answer_callback(bot: Bot, callback_query: CallbackQuery):
    chap_idx, q_idx, user_choice = callback_query.matches[0].groups()
    chap_idx, q_idx = int(chap_idx), int(q_idx)
    
    question = QBANK_DATA["chapters"][chap_idx]["questions"][q_idx]
    correct_ans = question.get("correct_answer", "A") 
    
    is_correct = user_choice == correct_ans
    result_icon = "✅" if is_correct else "❌"
    feedback = f"\n\n{result_icon} **Result:**\nYour Choice: {user_choice}\nCorrect Answer: **{correct_ans}**"
    
    next_btn = [[InlineKeyboardButton("Next Question ➡️", callback_data=f"qb_chap_{chap_idx}_{q_idx + 1}")]]
    
    if callback_query.message.photo:
        current_caption = callback_query.message.caption or ""
        await callback_query.message.edit_caption(
            caption=f"{current_caption}{feedback}",
            reply_markup=InlineKeyboardMarkup(next_btn),
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        current_text = callback_query.message.text or ""
        await callback_query.message.edit_text(
            text=f"{current_text}{feedback}",
            reply_markup=InlineKeyboardMarkup(next_btn),
            parse_mode=ParseMode.MARKDOWN
        )
