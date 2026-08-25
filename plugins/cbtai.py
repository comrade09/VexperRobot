import os
import re
import json
import html
import base64
import asyncio
import time
from pathlib import Path
from bot import Bot
import fitz  # PyMuPDF
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from google import genai

# ============================================================
# CONFIGURATION & SETUP
# ============================================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
client_ai = genai.Client(api_key=GEMINI_API_KEY)

# Simple in-memory dictionary for user state management
# Format: { user_id: {"state": str, "q_pdf": str, "a_pdf": str, "msg_id": int} }
USER_STATES = {}

OUT_DIR = Path("cbt_output")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# PROMPTS
# ============================================================
EXTRACTION_PROMPT = r"""
You are converting a NEET / medical entrance examination PDF into structured CBT data.
Read the ENTIRE uploaded PDF carefully.
Extract EVERY question. Do NOT solve the questions. Do NOT change the wording.
For every question return:
{
  "global_no": integer,
  "subject": "PHYSICS" | "CHEMISTRY" | "BIOLOGY",
  "question": "question text",
  "options": ["option 1", "option 2", "option 3", "option 4"],
  "page": integer
}
IMPORTANT:
1. Extract ALL questions. Every question must have exactly four options.
2. If a diagram, circuit, organic structure, or complex image is required in the question OR options, insert EXACTLY: [FIGURE]
3. Assign the correct subject. The "page" field must contain the page number where the question is found.
4. Return ONLY valid JSON.
Return:
{
  "test_title": "...",
  "questions": [...]
}
"""

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def clean_json_response(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()

def normalize_subject(subject):
    subject = str(subject).upper().strip()
    if "PHYS" in subject: return "PHYSICS"
    if "CHEM" in subject: return "CHEMISTRY"
    if "BIO" in subject: return "BIOLOGY"
    return subject

def extract_questions_sync(pdf_path):
    uploaded_file = client_ai.files.upload(file=pdf_path)
    response = client_ai.models.generate_content(
        model="gemini-3.6-flash",
        contents=[uploaded_file, EXTRACTION_PROMPT]
    )
    raw = clean_json_response(response.text)
    try:
        data = json.loads(raw)
    except Exception:
        repair_prompt = f"Repair the following into valid JSON. Do not change the question content. Return ONLY valid JSON.\n\n{raw}"
        repair_response = client_ai.models.generate_content(
            model="gemini-3.6-flash",
            contents=repair_prompt
        )
        data = json.loads(clean_json_response(repair_response.text))
    return data

def extract_answer_key_sync(key_path):
    if not key_path:
        return {}
    uploaded_key = client_ai.files.upload(file=key_path)
    prompt = r"""Read this answer key carefully. Return ONLY valid JSON:
{"answers": {"1": 2, "2": 4, "3": 1}}
Rules: Question number is key. Value is 1 for A, 2 for B, 3 for C, 4 for D. Extract ALL available answers. Do not solve."""
    response = client_ai.models.generate_content(model="gemini-3.6-flash", contents=[uploaded_key, prompt])
    raw = clean_json_response(response.text)
    try:
        data = json.loads(raw)
    except Exception:
        repair_prompt = f"Convert this into valid JSON. Return only: {{\"answers\": {{\"question_number\": option_number}}}}\n\n{raw}"
        response2 = client_ai.models.generate_content(model="gemini-3.6-flash", contents=repair_prompt)
        data = json.loads(clean_json_response(response2.text))
    
    answers = {}
    for number, answer in data.get("answers", {}).items():
        try: answers[int(number)] = int(answer)
        except: pass
    return answers

def validate_questions(data):
    if "questions" not in data: return []
    output_questions = []
    for q in data["questions"]:
        try: number = int(q["global_no"])
        except: continue
        subject = normalize_subject(q.get("subject", ""))
        question = str(q.get("question", "")).strip()
        options = q.get("options", [])
        if not isinstance(options, list): continue
        while len(options) < 4: options.append("[OPTION UNREADABLE]")
        options = options[:4]
        output_questions.append({
            "global_no": number, "subject": subject, "question": question, 
            "options": [str(x) for x in options], "page": q.get("page", None)
        })
    output_questions.sort(key=lambda x: x["global_no"])
    return output_questions

# (Include your full HTML generator string here. Trimmed for brevity but use the exact one from previous fixes)
def generate_cbt_html(title, questions, answer_key, pdf_path):
    page_b64_map = {}
    try:
        doc = fitz.open(pdf_path)
        for q in questions:
            text_to_check = str(q.get('question', '')).upper() + " " + str(q.get('options', [])).upper()
            if "[FIGURE" in text_to_check or "[IMAGE" in text_to_check:
                page_num = q.get('page')
                if page_num:
                    try:
                        page_index = int(page_num) - 1
                        page_key = str(page_num)
                        if page_key not in page_b64_map and 0 <= page_index < len(doc):
                            page = doc[page_index]
                            pix = page.get_pixmap(dpi=150)
                            b64 = base64.b64encode(pix.tobytes("png")).decode("utf-8")
                            page_b64_map[page_key] = f"data:image/png;base64,{b64}"
                    except: continue
        doc.close()
    except: pass

    questions_json = json.dumps(questions, ensure_ascii=False)
    answer_json = json.dumps(answer_key, ensure_ascii=False)
    page_images_json = json.dumps(page_b64_map, ensure_ascii=False)
    title_safe = html.escape(title)

    # Simplified HTML string for this script (Merge your full HTML template here)
    return f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>{title_safe} — CBT</title></head>
    <body><h2>{title_safe}</h2>
    <script>
    const questions = {questions_json};
    const answerKey = {answer_json};
    const pageImages = {page_images_json};
    console.log("CBT Loaded with " + questions.length + " questions.");
    </script>
    <!-- PASTE THE FULL HTML/CSS/JS FROM THE COLAB SCRIPT HERE -->
    </body></html>"""

# ============================================================
# BOT HANDLERS
# ============================================================

@Client.on_message(filters.command("cbtai") & filters.private,group=9894)
async def start_cbt_process(client, message):
    USER_STATES[message.from_user.id] = {"state": "WAITING_FOR_Q_PDF"}
    await message.reply_text("📚 **CBT AI Converter**\n\nPlease upload the **Question PDF** (any coaching material).")

@Client.on_message(filters.document & filters.private,group=8833)
async def handle_document(client, message):
    user_id = message.from_user.id
    state_info = USER_STATES.get(user_id)

    if not state_info:
        return

    if not message.document.file_name.lower().endswith(".pdf"):
        await message.reply_text("⚠️ Please upload a valid PDF file.")
        return

    current_state = state_info.get("state")

    if current_state == "WAITING_FOR_Q_PDF":
        msg = await message.reply_text("📥 Downloading Question PDF...")
        file_path = await message.download()
        USER_STATES[user_id]["q_pdf"] = file_path
        
        # Ask about answers
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Yes, Answers are in this PDF", callback_data="cbt_combined")],
            [InlineKeyboardButton("📄 No, I will upload a separate Key", callback_data="cbt_separate")],
            [InlineKeyboardButton("⏭️ Skip Answer Key", callback_data="cbt_skip")]
        ])
        await msg.edit_text("PDF Saved! Does this PDF also contain the **Solutions / Answer Key**?", reply_markup=keyboard)

    elif current_state == "WAITING_FOR_A_PDF":
        msg = await message.reply_text("📥 Downloading Answer Key PDF...")
        file_path = await message.download()
        USER_STATES[user_id]["a_pdf"] = file_path
        await msg.edit_text("✅ Answer Key saved.")
        await start_conversion(client, message.chat.id, user_id)

@Client.on_callback_query(filters.regex(r"^cbt_"),group=83889)
async def handle_callback(client, callback_query):
    user_id = callback_query.from_user.id
    data = callback_query.data
    
    if user_id not in USER_STATES:
        await callback_query.answer("Session expired. Send /cbtai again.", show_alert=True)
        return

    if data == "cbt_combined":
        USER_STATES[user_id]["a_pdf"] = USER_STATES[user_id]["q_pdf"]
        await callback_query.message.edit_text("✅ Will extract answers from the same PDF.")
        await start_conversion(client, callback_query.message.chat.id, user_id)
        
    elif data == "cbt_separate":
        USER_STATES[user_id]["state"] = "WAITING_FOR_A_PDF"
        await callback_query.message.edit_text("Please upload the **Answer Key PDF** now.")
        
    elif data == "cbt_skip":
        USER_STATES[user_id]["a_pdf"] = None
        await callback_query.message.edit_text("✅ Skipping Answer Key.")
        await start_conversion(client, callback_query.message.chat.id, user_id)

# ============================================================
# PROGRESS UPDATER & PROCESSING CORE
# ============================================================
async def progress_updater(client, chat_id, msg_id, status_tracker):
    start_time = time.time()
    while status_tracker.get("is_running"):
        await asyncio.sleep(5)
        if not status_tracker.get("is_running"):
            break
        elapsed = int(time.time() - start_time)
        text = f"⚙️ **Processing CBT Transformation**\n\n" \
               f"📌 **Status:** {status_tracker.get('status', 'Working...')}\n" \
               f"⏱️ **Time Elapsed:** {elapsed} seconds\n" \
               f"⏳ **Estimated Time:** 1 to 3 minutes\n\n" \
               f"*(Updates every 5 seconds...)*"
        try:
            await client.edit_message_text(chat_id, msg_id, text)
        except Exception:
            pass # Ignore telegram flood waits or message not modified errors

async def start_conversion(client, chat_id, user_id):
    state_info = USER_STATES.pop(user_id, None)
    if not state_info: return
    
    q_pdf = state_info.get("q_pdf")
    a_pdf = state_info.get("a_pdf")
    
    msg = await client.send_message(chat_id, "⚙️ **Processing CBT Transformation**\n\nStarting...")
    
    status_tracker = {"is_running": True, "status": "Reading PDF & Contacting Gemini AI..."}
    updater_task = asyncio.create_task(progress_updater(client, chat_id, msg.id, status_tracker))
    
    try:
        # 1. Extract Questions (Run in background thread to avoid blocking bot)
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(None, extract_questions_sync, q_pdf)
        
        status_tracker["status"] = "Validating extracted questions & formatting diagrams..."
        questions = validate_questions(data)
        
        if not questions:
            raise ValueError("No valid questions found.")

        # 2. Extract Answers
        answer_key = {}
        if a_pdf:
            status_tracker["status"] = "Extracting Answer Key..."
            answer_key = await loop.run_in_executor(None, extract_answer_key_sync, a_pdf)

        # 3. Build HTML
        status_tracker["status"] = "Rendering diagrams and generating final HTML..."
        title = data.get("test_title", "Custom_NEET_Test")
        html_content = await loop.run_in_executor(None, generate_cbt_html, title, questions, answer_key, q_pdf)

        output_file = OUT_DIR / f"{title.replace(' ', '_')}_CBT.html"
        output_file.write_text(html_content, encoding="utf-8")

        # Stop updater
        status_tracker["is_running"] = False
        await updater_task
        
        await client.edit_message_text(chat_id, msg.id, "✅ **CBT Created Successfully!** Uploading file...")
        await client.send_document(chat_id, document=str(output_file), caption=f"Here is your attemptable CBT for **{title}**.\n\nOpen this HTML file in any browser (Chrome/Safari) to attempt the test.")

    except Exception as e:
        status_tracker["is_running"] = False
        await updater_task
        await client.edit_message_text(chat_id, msg.id, f"❌ **Error during conversion:**\n`{str(e)}`")
    
    finally:
        # Cleanup downloaded files to save server space
        if q_pdf and os.path.exists(q_pdf): os.remove(q_pdf)
        if a_pdf and a_pdf != q_pdf and os.path.exists(a_pdf): os.remove(a_pdf)
