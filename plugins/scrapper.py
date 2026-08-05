import os
import re
import json
import time
import random
import asyncio
from urllib.parse import unquote

from pyrogram import filters
from pyrogram.types import Message
from bot import Bot  # Matches your existing bot import

# Selenium / Undetected-ChromeDriver for Koyeb
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ==========================================
# 1. STEALTH SCRAPER LOGIC
# ==========================================
def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new") 
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-setuid-sandbox")
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # use_subprocess=True is required for Docker environments running as root
    driver = uc.Chrome(options=options, version_main=None, use_subprocess=True) 
    return driver

def random_sleep(min_sec=1.0, max_sec=3.0):
    time.sleep(random.uniform(min_sec, max_sec))

def human_scroll(driver, max_scrolls=6):
    for _ in range(max_scrolls):
        scroll_amount = random.randint(400, 900)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        random_sleep(0.3, 0.8)
    driver.execute_script("window.scrollTo({ top: 0, behavior: 'smooth' });")
    random_sleep(1.0, 2.0)

def extract_video_url(onclick_str):
    if not onclick_str:
        return ""
    match = re.search(r"openPlayerPopup\('([^']+)'", onclick_str)
    if match:
        return unquote(match.group(1))
    return ""

def scrape_single_batch(batch_url):
    driver = setup_driver()
    output_dir = "scraped_batches"
    os.makedirs(output_dir, exist_ok=True)
    screenshot_path = os.path.join(output_dir, "debug_screenshot.png")

    batch_id_match = re.search(r"batch_id=([a-zA-Z0-9_%-]+)", batch_url)
    batch_id = batch_id_match.group(1) if batch_id_match else "Unknown_Batch"

    driver.get(batch_url)
    random_sleep(6.0, 10.0) # Wait out Cloudflare

    try:
        batch_title = driver.find_element(By.XPATH, "//h1 | //h2 | //title").text.strip()
    except Exception:
        batch_title = f"Batch_{batch_id}"
        
    safe_batch_title = re.sub(r'[\\/*?:"<>|]', "_", batch_title)
    human_scroll(driver)

    teacher_elements = driver.find_elements(By.XPATH, "//a[contains(@href, 'teacher-detail.php')] | //*[contains(@onclick, 'teacher-detail.php')]")
    teacher_urls = []
    
    for elem in teacher_elements:
        href = elem.get_attribute("href") or ""
        onclick = elem.get_attribute("onclick") or ""
        target = href if "teacher-detail.php" in href else onclick
        if target:
            match = re.search(r"teacher-detail\.php\?batch_id=[^'\"\s&]+&teacher=([^'\"\s&]+)", target)
            if match:
                t_url = f"https://studyuk.online/offline/teacher-detail.php?batch_id={batch_id}&teacher={match.group(1)}"
                if t_url not in teacher_urls:
                    teacher_urls.append(t_url)

    if not teacher_urls:
        matches = re.findall(r"teacher-detail\.php\?batch_id=[^'\"\s<>]+&teacher=([^'\"\s<>]+)", driver.page_source)
        for teacher_param in matches:
            t_url = f"https://studyuk.online/offline/teacher-detail.php?batch_id={batch_id}&teacher={teacher_param}"
            if t_url not in teacher_urls:
                teacher_urls.append(t_url)

    # Failed to bypass Cloudflare / login wall
    if not teacher_urls:
        driver.save_screenshot(screenshot_path)
        driver.quit()
        return None, None, screenshot_path

    batch_data = {
        "batch_title": batch_title,
        "batch_id": batch_id,
        "batch_url": batch_url,
        "teachers": []
    }

    for t_idx, teacher_url in enumerate(teacher_urls, 1):
        driver.get(teacher_url)
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "content-card")))
        except Exception:
            random_sleep(2.0, 4.0)

        human_scroll(driver)

        try:
            teacher_name = driver.find_element(By.XPATH, "//div[contains(@class, 'teacher-header')] | //h2 | //h1").text.strip()
        except Exception:
            t_param = re.search(r"teacher=([^&]+)", teacher_url)
            teacher_name = unquote(t_param.group(1)).replace("+", " ") if t_param else f"Teacher_{t_idx}"

        cards = driver.find_elements(By.CLASS_NAME, "content-card")
        lectures = []

        for card in cards:
            try:
                lecture_title = card.find_element(By.XPATH, ".//h3").text.strip()
            except Exception:
                lecture_title = "Untitled Lecture"

            lecture_date = ""
            try:
                date_elem = card.find_element(By.XPATH, ".//div[contains(@class, 'content-meta')] | .//span[contains(@class, 'date')]")
                lecture_date = date_elem.text.strip()
            except Exception:
                date_match = re.search(r"([A-Z][a-z]{2}\s+\d{1,2},\s+\d{4})", card.text)
                if date_match:
                    lecture_date = date_match.group(1)

            video_url = extract_video_url(card.find_element(By.XPATH, ".//button[contains(@class, 'video-btn')]").get_attribute("onclick")) if card.find_elements(By.XPATH, ".//button[contains(@class, 'video-btn')]") else ""
            pdf_url = card.find_element(By.XPATH, ".//a[contains(@class, 'pdf-btn')]").get_attribute("href") if card.find_elements(By.XPATH, ".//a[contains(@class, 'pdf-btn')]") else ""

            lectures.append({"lecture_title": lecture_title, "date": lecture_date, "video_url": video_url, "pdf_url": pdf_url})

        batch_data["teachers"].append({"teacher_name": teacher_name, "teacher_url": teacher_url, "lectures": lectures})
        random_sleep(1.0, 2.0)

    json_path = os.path.join(output_dir, f"{safe_batch_title}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(batch_data, f, indent=4, ensure_ascii=False)

    txt_path = os.path.join(output_dir, f"{safe_batch_title}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"BATCH TITLE: {batch_title}\nBATCH URL:   {batch_url}\n" + "=" * 80 + "\n\n")
        for t in batch_data["teachers"]:
            f.write(f"TEACHER: {t['teacher_name']}\nLINK:    {t['teacher_url']}\n" + "-" * 60 + "\n")
            for l in t["lectures"]:
                f.write(f"Lecture: {l['lecture_title']}\n  Date:       {l['date']}\n  Video Link: {l['video_url']}\n  PDF Link:   {l['pdf_url']}\n\n")
            f.write("\n" + "=" * 80 + "\n\n")

    driver.quit()
    return txt_path, json_path, None


# ==========================================
# 2. PYROGRAM BOT HANDLER
# ==========================================

@Bot.on_message(filters.command("scrape"),group=8787)
async def handle_scrape(client: Bot, message: Message):
    if len(message.command) < 2:
        await message.reply_text("⚠️ **Usage:** `/scrape <batch_url>`")
        return
        
    url = message.command[1]
    status_msg = await message.reply_text("⏳ **Scraping...**\n_Navigating Cloudflare checks (this takes ~10-15 seconds)..._")
    
    try:
        txt_file, json_file, debug_img = await asyncio.to_thread(scrape_single_batch, url)
        
        if debug_img:
            await status_msg.edit_text("❌ **Anti-Bot Blocked the Request.**\nThe site refused to let the bot in. Here is a screenshot of what the bot saw:")
            await message.reply_photo(photo=debug_img, caption="What the bot sees inside Koyeb.")
            return

        await status_msg.edit_text("✅ **Scraping Complete!** Uploading files...")
        await message.reply_document(document=txt_file, caption="📄 Extracted Text Data")
        await message.reply_document(document=json_file, caption="📜 Extracted JSON Data")
        
        # Cleanup files from server
        try:
            os.remove(txt_file)
            os.remove(json_file)
        except Exception:
            pass
            
    except Exception as e:
        await status_msg.edit_text(f"❌ **Error during scraping:**\n`{str(e)}`")
