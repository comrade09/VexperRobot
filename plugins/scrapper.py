import os
import re
import time
import asyncio
from urllib.parse import unquote
from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Project Imports
from config import OWNER_ID
from bot import Bot
from database.database import (
    get_all_batches, 
    get_batch, 
    update_batch_data
)

# Temporary memory to track admin input state
user_states = {}


# --- EMBEDDED SELENIUM SCRAPER FUNCTION ---

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


def run_selenium_scraper(batch_url: str):
    # Sanitize incoming batch_url string (strips backticks, quotes, and whitespace)
    batch_url = batch_url.strip("`'\" \t\n\r")

    driver = setup_driver()

    # Clean batch_id extraction (strictly captures alphanumeric characters)
    batch_id_match = re.search(r"batch_id=([a-zA-Z0-9]+)", batch_url)
    batch_id = batch_id_match.group(1) if batch_id_match else "Unknown"

    # Reconstruct clean batch_url to prevent navigating to malformed URLs
    if batch_id != "Unknown":
        batch_url = f"https://studyuk.online/offline/batch-details.php?batch_id={batch_id}"

    driver.get(batch_url)

    # 1. Wait for page body to fully load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except Exception:
        pass

    # 2. Extract Batch Title
    try:
        batch_title = driver.find_element(By.XPATH, "//h1 | //h2 | //title").text.strip()
        if not batch_title:
            batch_title = f"Batch_{batch_id}"
    except Exception:
        batch_title = f"Batch_{batch_id}"

    # 3. Scroll to trigger lazy loading of elements
    for _ in range(6):
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(0.5)

    # 4. DOM-based search with expanded selectors
    teacher_urls = []
    elements = driver.find_elements(
        By.XPATH, 
        "//a[contains(@href, 'teacher-detail.php')] | "
        "//*[contains(@onclick, 'teacher-detail.php')] | "
        "//div[contains(@class, 'card')]//a | "
        "//div[contains(@class, 'teacher')]//a"
    )
    
    for elem in elements:
        href = elem.get_attribute("href") or ""
        onclick = elem.get_attribute("onclick") or ""
        target = href if "teacher-detail.php" in href else onclick
        
        if target:
            match = re.search(r"teacher=([^'\"\s&`]+)", target)
            if match:
                teacher_param = match.group(1)
                t_url = f"https://studyuk.online/offline/teacher-detail.php?batch_id={batch_id}&teacher={teacher_param}"
                if t_url not in teacher_urls:
                    teacher_urls.append(t_url)

    # 5. Regex Fallback: Search direct page HTML if DOM elements were missed
    if not teacher_urls:
        page_source = driver.page_source
        matches = re.findall(r"teacher-detail\.php\?[^'\"\s>]*teacher=([^'\"\s&<>`]+)", page_source)
        for t_param in set(matches):
            t_url = f"https://studyuk.online/offline/teacher-detail.php?batch_id={batch_id}&teacher={t_param}"
            if t_url not in teacher_urls:
                teacher_urls.append(t_url)

    teachers_data = []

    # 6. Scrape each teacher detail page
    for teacher_url in teacher_urls:
        driver.get(teacher_url)
        
        try:
            WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'card') or contains(@class, 'content')]"))
            )
        except Exception:
            time.sleep(2)

        for _ in range(5):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(0.3)

        # Teacher Name
        try:
            teacher_name = driver.find_element(
                By.XPATH, "//div[contains(@class, 'teacher')]//h2 | //h1 | //h2"
            ).text.strip()
        except Exception:
            t_param = re.search(r"teacher=([^&`]+)", teacher_url)
            teacher_name = unquote(t_param.group(1)).replace("+", " ") if t_param else "Teacher"

        # Lecture Cards
        cards = driver.find_elements(
            By.XPATH, "//div[contains(@class, 'content-card')] | //div[contains(@class, 'card')]"
        )
        lectures = []

        for card in cards:
            # Title
            try:
                lecture_title = card.find_element(By.XPATH, ".//h3 | .//h4 | .//strong").text.strip()
            except Exception:
                lecture_title = "Untitled Lecture"

            # Date
            lecture_date = ""
            try:
                date_elem = card.find_element(
                    By.XPATH, ".//div[contains(@class, 'content-meta')] | .//span[contains(@class, 'date')]"
                )
                lecture_date = date_elem.text.strip()
            except Exception:
                date_match = re.search(r"([A-Z][a-z]{2}\s+\d{1,2},\s+\d{4})", card.text)
                if date_match:
                    lecture_date = date_match.group(1)

            # Video URL
            video_url = ""
            try:
                v_btn = card.find_element(By.XPATH, ".//*[contains(@onclick, 'openPlayerPopup')]")
                onclick_val = v_btn.get_attribute("onclick") or ""
                v_match = re.search(r"openPlayerPopup\('([^']+)'", onclick_val)
                if v_match:
                    video_url = unquote(v_match.group(1))
            except Exception:
                pass

            # PDF URL
            pdf_url = ""
            try:
                p_btn = card.find_element(By.XPATH, ".//a[contains(@href, '.pdf') or contains(@class, 'pdf')]")
                pdf_url = p_btn.get_attribute("href") or ""
            except Exception:
                pass

            lectures.append({
                "lecture_title": lecture_title,
                "date": lecture_date if lecture_date else "Unknown Date",
                "video_url": video_url,
                "pdf_url": pdf_url
            })

        teachers_data.append({
            "teacher_name": teacher_name,
            "teacher_url": teacher_url,
            "lectures": lectures
        })

    driver.quit()

    return batch_id, batch_title, teachers_data


# --- ADMIN COMMANDS ---

@Bot.on_message(filters.command('addnew') & filters.private & filters.user(OWNER_ID), group=8367)
async def admin_panel(bot: Bot, message: Message):
    buttons = [
        [InlineKeyboardButton("➕ Add New Batch", callback_data="admin_add_batch")],
        [InlineKeyboardButton("🔄 Manage / Update Batches", callback_data="admin_manage_batches")],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    await message.reply_text(
        "🛠 **Admin Control Panel**\nChoose an action below:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Bot.on_message(filters.private & filters.user(OWNER_ID) & filters.text, group=8312)
async def handle_admin_text(bot: Bot, message: Message):
    user_id = message.from_user.id
    state = user_states.get(user_id)

    if state == "WAITING_FOR_BATCH_URL":
        # Strip backticks or quotes if passed accidentally by admin
        url = message.text.strip("`'\" \t\n\r")
        if "batch_id=" not in url:
            await message.reply_text("❌ Invalid link! Must contain `batch_id=` parameter.")
            return

        user_states[user_id] = None
        status_msg = await message.reply_text("⏳ **Starting Scraper...**\nFetching teachers and lectures. Please wait.")

        try:
            batch_id, batch_title, teachers_data = await asyncio.to_thread(run_selenium_scraper, url)
            
            # Save scraped data to MongoDB using clean batch_url
            clean_url = f"https://studyuk.online/offline/batch-details.php?batch_id={batch_id}"
            await update_batch_data(
                batch_id=batch_id,
                batch_title=batch_title,
                batch_url=clean_url,
                teachers=teachers_data,
                last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            await status_msg.edit_text(f"✅ **Batch Successfully Saved!**\n\n📌 **Title:** `{batch_title}`\n👨‍🏫 **Teachers Scraped:** {len(teachers_data)}")
        except Exception as e:
            await status_msg.edit_text(f"❌ **Error while scraping:**\n`{e}`")


# --- USER COMMANDS & CALENDAR ---

@Bot.on_message(filters.command(['cold', 'bold']) & filters.private, group=3722)
async def user_batches(bot: Bot, message: Message):
    batches = await get_all_batches()
    if not batches:
        await message.reply_text("📁 No batches available at the moment.")
        return

    buttons = []
    for b in batches:
        buttons.append([InlineKeyboardButton(f"📚 {b['batch_title']}", callback_data=f"ubatch_{b['batch_id']}")])

    await message.reply_text("👇 **Select a Batch to view lectures:**", reply_markup=InlineKeyboardMarkup(buttons))


# --- CALLBACK QUERY HANDLER ---

@Bot.on_callback_query(group=7678)
async def cb_handler(bot: Bot, query: CallbackQuery):
    data = query.data
    user_id = query.from_user.id

    if data == "admin_add_batch":
        if user_id != OWNER_ID:
            return await query.answer("Unauthorized", show_alert=True)
        user_states[user_id] = "WAITING_FOR_BATCH_URL"
        await query.message.edit_text("🔗 **Send me the direct Batch URL:**\n\nExample: `https://studyuk.online/offline/batch-details.php?batch_id=5NDPLQ9R`")

    elif data == "admin_manage_batches":
        if user_id != OWNER_ID:
            return await query.answer("Unauthorized", show_alert=True)
        batches = await get_all_batches()
        if not batches:
            return await query.answer("No batches found in database.", show_alert=True)

        buttons = []
        for b in batches:
            buttons.append([InlineKeyboardButton(f"🔄 Update: {b['batch_title']}", callback_data=f"reupdate_{b['batch_id']}")])
        buttons.append([InlineKeyboardButton("🔙 Back", callback_data="admin_back")])

        await query.message.edit_text("⚙️ **Select a Batch to re-scrape and update:**", reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("reupdate_"):
        if user_id != OWNER_ID:
            return await query.answer("Unauthorized", show_alert=True)
        batch_id = data.split("_")[1]
        batch = await get_batch(batch_id)
        
        await query.message.edit_text(f"⏳ **Updating `{batch['batch_title']}`...**\nScraping new lectures in the background...")
        try:
            b_id, title, teachers_data = await asyncio.to_thread(run_selenium_scraper, batch['batch_url'])
            
            clean_url = f"https://studyuk.online/offline/batch-details.php?batch_id={b_id}"
            await update_batch_data(
                batch_id=b_id,
                batch_title=title,
                batch_url=clean_url,
                teachers=teachers_data,
                last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            await query.message.edit_text(f"✅ **Update Complete!**\n\n📌 **Title:** `{title}`\n👨‍🏫 **Teachers Updated:** {len(teachers_data)}")
        except Exception as e:
            await query.message.edit_text(f"❌ **Update Failed:**\n`{e}`")

    elif data.startswith("ubatch_"):
        batch_id = data.split("_")[1]
        batch = await get_batch(batch_id)
        
        if not batch:
            return await query.answer("Batch not found.", show_alert=True)

        dates = set()
        for teacher in batch.get("teachers", []):
            for lecture in teacher.get("lectures", []):
                if lecture.get("date"):
                    dates.add(lecture["date"])

        if not dates:
            return await query.answer("No dates found for this batch.", show_alert=True)

        sorted_dates = list(dates)

        buttons = []
        row = []
        for d in sorted_dates:
            row.append(InlineKeyboardButton(f"📅 {d}", callback_data=f"udate_{batch_id}_{d}"))
            if len(row) == 2:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)

        buttons.append([InlineKeyboardButton("🔙 Back to Batches", callback_data="user_back")])

        await query.message.edit_text(
            f"📖 **{batch['batch_title']}**\nSelect a date to get lectures uploaded on that day:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif data.startswith("udate_"):
        _, batch_id, selected_date = data.split("_", 2)
        batch = await get_batch(batch_id)

        found_lectures = []
        for teacher in batch.get("teachers", []):
            for lecture in teacher.get("lectures", []):
                if lecture.get("date") == selected_date:
                    found_lectures.append((teacher["teacher_name"], lecture))

        if not found_lectures:
            return await query.answer("No lectures found for this date.", show_alert=True)

        text = f"📅 **Lectures for {selected_date}**\n📌 **Batch:** {batch['batch_title']}\n"
        text += "━" * 25 + "\n\n"

        for teacher_name, lec in found_lectures:
            text += f"👨‍🏫 **Teacher:** {teacher_name}\n"
            text += f"📖 **Title:** `{lec['lecture_title']}`\n"
            if lec['video_url']:
                text += f"🎥 [Watch Video]({lec['video_url']})\n"
            if lec['pdf_url']:
                text += f"📄 [Download PDF]({lec['pdf_url']})\n"
            text += "\n"

        buttons = [[InlineKeyboardButton("🔙 Back to Calendar", callback_data=f"ubatch_{batch_id}")]]
        await query.message.edit_text(text, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "user_back":
        await user_batches(bot, query.message)

    elif data == "close":
        await query.message.delete()
