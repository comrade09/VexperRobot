import os
import re
import json
import time
import asyncio
from urllib.parse import unquote
from pyrogram import filters
from pyrogram.types import Message
from bot import Bot  # Matches your existing bot import

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- Scraper Logic ---

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") # Headless is required for background bot servers
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

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

    batch_id_match = re.search(r"batch_id=([a-zA-Z0-9_%-]+)", batch_url)
    batch_id = batch_id_match.group(1) if batch_id_match else "Unknown_Batch"

    driver.get(batch_url)
    time.sleep(3)

    try:
        batch_title = driver.find_element(By.XPATH, "//h1 | //h2 | //title").text.strip()
    except Exception:
        batch_title = f"Batch_{batch_id}"
        
    safe_batch_title = re.sub(r'[\\/*?:"<>|]', "_", batch_title)

    for _ in range(6):
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(0.5)

    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)

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
            time.sleep(2)

        for _ in range(6):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(0.4)

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

            video_url, pdf_url = "", ""
            try:
                v_btn = card.find_element(By.XPATH, ".//button[contains(@class, 'video-btn')]")
                video_url = extract_video_url(v_btn.get_attribute("onclick"))
            except Exception:
                pass

            try:
                p_btn = card.find_element(By.XPATH, ".//a[contains(@class, 'pdf-btn')]")
                pdf_url = p_btn.get_attribute("href") or ""
            except Exception:
                pass

            lectures.append({"lecture_title": lecture_title, "date": lecture_date, "video_url": video_url, "pdf_url": pdf_url})

        batch_data["teachers"].append({"teacher_name": teacher_name, "teacher_url": teacher_url, "lectures": lectures})

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
    
    return txt_path, json_path

# --- Bot Handler ---

@Bot.on_message(filters.command("scrape"),group=8838)
async def handle_scrape(client: Bot, message: Message):
    if len(message.command) < 2:
        await message.reply_text("⚠️ **Usage:** `/scrape <batch_url>`")
        return
        
    url = message.command[1]
    
    status_msg = await message.reply_text("⏳ **Starting Scraper...**\n_Please wait, this might take a few minutes as it parses the pages._")
    
    try:
        # Run the synchronous scraper function in a thread to keep the bot responsive
        txt_file, json_file = await asyncio.to_thread(scrape_single_batch, url)
        
        await status_msg.edit_text("✅ **Scraping Complete!** Uploading files...")
        
        # Upload the scraped documents back to the chat
        await message.reply_document(document=txt_file, caption="📄 Extracted Text Data")
        await message.reply_document(document=json_file, caption="📜 Extracted JSON Data")
        
        # Optionally, clean up the files from your server after sending
        # os.remove(txt_file)
        # os.remove(json_file)
        
    except Exception as e:
        await status_msg.edit_text(f"❌ **Error during scraping:**\n`{str(e)}`")
