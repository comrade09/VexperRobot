import os
import re
import time
import asyncio
import html as html_mod
from urllib.parse import unquote
from datetime import datetime

import requests

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

BASE = "https://studyuk.online/offline"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}


# --- HTTP SCRAPER (primary, fast, no browser needed) ---

def _clean_text(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", s).strip()


def _fetch(url, timeout=30):
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code} for {url}")
    if "Just a moment" in resp.text[:600]:
        raise RuntimeError(f"Cloudflare challenge for {url}")
    return resp.text


def _fetch_with_retry(url, tries=3, timeout=30):
    last = None
    for i in range(tries):
        try:
            return _fetch(url, timeout=timeout)
        except Exception as e:
            last = e
            time.sleep(1.5 * (i + 1))
    raise last


def get_batch_titles():
    """Map batch_id -> real batch title from batches.php."""
    try:
        page = _fetch(f"{BASE}/batches.php")
    except Exception:
        return {}
    mapping = {}
    for card in re.finditer(r'<div class="batch-card"[^>]*>', page):
        block = card.group(0)
        bid = re.search(r'data-batch-id="([^"]+)"', block)
        bname = re.search(r'data-batch-name="([^"]+)"', block)
        if bid and bname:
            mapping[bid.group(1)] = html_mod.unescape(bname.group(1))
    return mapping


def parse_teacher_urls(batch_html):
    urls = []
    for m in re.finditer(r'href="([^"]*teacher-detail\.php[^"]*)"', batch_html):
        href = html_mod.unescape(m.group(1))
        if "teacher=" not in href or "batch_id=" not in href:
            continue
        url = href if href.startswith("http") else f"{BASE}/{href.lstrip('/')}"
        if url not in urls:
            urls.append(url)
    return urls


def parse_teacher_page(url):
    page = _fetch(url)
    page = re.sub(r"<!--.*?-->", "", page, flags=re.S)

    name_m = re.search(r'<h1 class="teacher-title">([^<]*)</h1>', page)
    teacher_name = _clean_text(name_m.group(1)) if name_m else "Teacher"

    lectures = []
    cards = re.findall(
        r'<div class="content-card">(.*?)<div class="content-actions">(.*?)</div>\s*</div>',
        page,
        re.S,
    )
    for top, actions in cards:
        title_m = re.search(r'<h3 class="content-title">(.*?)</h3>', top, re.S)
        lecture_title = _clean_text(title_m.group(1)) if title_m else "Untitled Lecture"

        date_m = re.search(r"([A-Za-z]{3}\s+\d{1,2},\s+\d{4})", top)
        lecture_date = date_m.group(1) if date_m else "Unknown Date"

        video_url = ""
        v_m = re.search(r"openPlayerPopup\(\s*'([^']+)'", actions)
        if v_m:
            video_url = unquote(v_m.group(1))

        pdf_url = ""
        p_m = re.search(r'href="([^"]+\.pdf)"', actions)
        if p_m:
            pdf_url = html_mod.unescape(p_m.group(1))

        lectures.append({
            "lecture_title": lecture_title,
            "date": lecture_date,
            "video_url": video_url,
            "pdf_url": pdf_url,
        })

    return {
        "teacher_name": teacher_name,
        "teacher_url": url,
        "lectures": lectures,
    }


# --- ADVANCED ANTI-DETECTION SELENIUM DRIVER (fallback) ---

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    # Anti-bot bypass settings
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )

    # Prefer a system-installed chromedriver (Docker: chromium/chromium-driver),
    # otherwise fall back to webdriver-manager downloading one.
    service = None
    for path in ("/usr/bin/chromedriver", "/usr/local/bin/chromedriver", "/snap/bin/chromedriver"):
        if os.path.exists(path):
            service = Service(path)
            break
    if service is None:
        service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=options)

    # Conceal webdriver presence
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver


def _selenium_scrape(batch_id, batch_url, batch_title):
    """Fallback scraper. Waits out Cloudflare and uses precise selectors."""
    driver = setup_driver()
    try:
        driver.get(batch_url)

        # Wait until the real page renders (Cloudflare challenge disappears)
        try:
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'teacher-detail.php')]"))
            )
        except Exception:
            pass

        title_elem = driver.find_elements(By.XPATH, "//h1[contains(@class, 'batch-title')] | //title")
        page_title = _clean_text(title_elem[0].text) if title_elem else ""
        if page_title and "Just a moment" not in page_title and "Attention Required" not in page_title \
                and page_title.lower() not in ("teachers", "batch details | study uk"):
            batch_title = page_title

        # Teachers: only anchors that really point to a teacher-detail page
        teacher_urls = []
        for elem in driver.find_elements(By.XPATH, "//a[contains(@href, 'teacher-detail.php')]"):
            href = elem.get_attribute("href")
            if href and "teacher=" in href and href not in teacher_urls:
                teacher_urls.append(href)

        # Strategy B: Direct page HTML regex search (catches hidden scripts/JS state objects)
        page_source = driver.page_source
        matches = re.findall(r"teacher=([A-Za-z0-9%+\-\.]+)", page_source)
        for t_param in set(matches):
            if len(t_param) > 1 and t_param.lower() not in ["detail.php", "detail", "index", "php"]:
                t_url = f"{BASE}/teacher-detail.php?batch_id={batch_id}&teacher={t_param}"
                if t_url not in teacher_urls:
                    teacher_urls.append(t_url)

        teachers_data = []
        for teacher_url in teacher_urls:
            driver.get(teacher_url)
            time.sleep(2)

            for _ in range(4):
                driver.execute_script("window.scrollBy(0, 800);")
                time.sleep(0.4)

            # Teacher Name
            teacher_name = ""
            try:
                name_elem = driver.find_element(By.XPATH, "//h1[contains(@class, 'teacher-title')]")
                teacher_name = name_elem.text.strip()
            except Exception:
                pass

            if not teacher_name:
                t_param = re.search(r"teacher=([^&`]+)", teacher_url)
                teacher_name = unquote(t_param.group(1)).replace("+", " ") if t_param else "Teacher"

            # Lectures
            cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'content-card')]")
            lectures = []
            for card in cards:
                card_text = card.text.strip()
                if not card_text:
                    continue

                lecture_title = "Untitled Lecture"
                try:
                    title_sub = card.find_element(By.XPATH, ".//h3[contains(@class, 'content-title')]")
                    lecture_title = title_sub.text.strip()
                except Exception:
                    lines = [line.strip() for line in card_text.split("\n") if line.strip()]
                    if lines:
                        lecture_title = lines[0]

                lecture_date = "Unknown Date"
                date_match = re.search(r"([A-Za-z]{3}\s+\d{1,2},\s+\d{4})", card_text)
                if date_match:
                    lecture_date = date_match.group(1)

                video_url = ""
                try:
                    v_elem = card.find_element(By.XPATH, ".//*[contains(@onclick, 'openPlayerPopup')]")
                    onclick_val = v_elem.get_attribute("onclick") or ""
                    v_match = re.search(r"openPlayerPopup\(\s*'([^']+)'", onclick_val)
                    if v_match:
                        video_url = unquote(v_match.group(1))
                except Exception:
                    pass

                pdf_url = ""
                try:
                    p_elem = card.find_element(By.XPATH, ".//a[contains(@href, '.pdf')]")
                    pdf_url = p_elem.get_attribute("href") or ""
                except Exception:
                    pass

                if video_url or pdf_url or len(lecture_title) > 3:
                    lectures.append({
                        "lecture_title": lecture_title,
                        "date": lecture_date,
                        "video_url": video_url,
                        "pdf_url": pdf_url
                    })

            teachers_data.append({
                "teacher_name": teacher_name,
                "teacher_url": teacher_url,
                "lectures": lectures
            })
        return teachers_data
    finally:
        driver.quit()


# --- MAIN SCRAPER (requests first, Selenium fallback) ---

def run_selenium_scraper(batch_url: str):
    batch_url = batch_url.strip("`'\" \t\n\r")

    batch_id_match = re.search(r"batch_id=([a-zA-Z0-9]+)", batch_url)
    batch_id = batch_id_match.group(1) if batch_id_match else "Unknown"

    if batch_id != "Unknown":
        clean_url = f"{BASE}/batch-details.php?batch_id={batch_id}"
    else:
        clean_url = batch_url

    batch_title = f"Batch_{batch_id}"
    errors = []

    # Try the fast HTTP scraper first
    try:
        titles = get_batch_titles()
        if batch_id in titles:
            batch_title = titles[batch_id]

        html = _fetch_with_retry(clean_url)
        if "teacher-card" not in html and "teacher-detail.php" not in html:
            raise RuntimeError("Page not fully loaded (challenge or block)")

        teacher_urls = parse_teacher_urls(html)
        if not teacher_urls:
            raise RuntimeError("No teacher links found on batch page")

        teachers_data = []
        for teacher_url in teacher_urls:
            try:
                teachers_data.append(parse_teacher_page(teacher_url))
            except Exception as e:
                errors.append(f"teacher {teacher_url.split('teacher=')[-1][:30]}: {e}")
            time.sleep(0.8)

        if not teachers_data:
            raise RuntimeError("All teacher pages failed: " + "; ".join(errors))

        return batch_id, batch_title, teachers_data
    except Exception as e:
        errors.append(f"HTTP path: {e}")

    # Selenium fallback
    try:
        teachers_data = _selenium_scrape(batch_id, clean_url, batch_title)
        if teachers_data:
            return batch_id, batch_title, teachers_data
        errors.append("Selenium path: returned no data")
    except Exception as e:
        errors.append(f"Selenium path: {e}")

    raise RuntimeError(" | ".join(errors))


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
        url = message.text.strip("`'\" \t\n\r")
        if "batch_id=" not in url:
            await message.reply_text("❌ Invalid link! Must contain `batch_id=` parameter.")
            return

        user_states[user_id] = None
        status_msg = await message.reply_text("⏳ **Starting Scraper...**\nFetching teachers and lectures. Please wait.")

        try:
            batch_id, batch_title, teachers_data = await asyncio.to_thread(run_selenium_scraper, url)

            clean_url = f"{BASE}/batch-details.php?batch_id={batch_id}"
            await update_batch_data(
                batch_id=batch_id,
                batch_title=batch_title,
                batch_url=clean_url,
                teachers=teachers_data,
                last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

            await status_msg.edit_text(
                f"✅ **Batch Successfully Saved!**\n\n"
                f"📌 **Title:** `{batch_title}`\n"
                f"👨‍🏫 **Teachers Scraped:** {len(teachers_data)}"
            )
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

            clean_url = f"{BASE}/batch-details.php?batch_id={b_id}"
            await update_batch_data(
                batch_id=b_id,
                batch_title=title,
                batch_url=clean_url,
                teachers=teachers_data,
                last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )

            await query.message.edit_text(
                f"✅ **Update Complete!**\n\n"
                f"📌 **Title:** `{title}`\n"
                f"👨‍🏫 **Teachers Updated:** {len(teachers_data)}"
            )
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
