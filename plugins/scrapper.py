import os
import re
import time
import base64
import asyncio
from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message
from bot import Bot  # Uses your already running Bot instance

# --- SELENIUM IMPORTS ---
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==========================================
# 1. SYNCHRONOUS SELENIUM FUNCTIONS
# ==========================================
def setup_driver():
    options = webdriver.ChromeOptions()
    
    # Explicitly point to the Chromium binary installed by Docker
    options.binary_location = "/usr/bin/chromium"
    
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    prefs = {
        "download_restrictions": 3,
        "download.prompt_for_download": True,
        "plugins.always_open_pdf_externally": False
    }
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    # Point directly to the Chromium driver
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    
    return driver

def dismiss_telegram_popup(driver):
    try:
        wait = WebDriverWait(driver, 3)
        close_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#tgPopup button, #tgPopup .close, #tgPopup svg, .tg-popup svg"))
        )
        close_btn.click()
    except Exception:
        try:
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        except Exception:
            pass

def scrape_lectures_and_pdfs(batch_name, subject_name):
    driver = setup_driver()
    url = "https://uc-web.uc27.workers.dev/"
    extracted_data = []

    try:
        print(f"[Scraper] Navigating to {url}...")
        driver.get(url)
        wait = WebDriverWait(driver, 20)

        time.sleep(2)
        dismiss_telegram_popup(driver)
        
        print(f"[Scraper] Searching for batch: {batch_name}")
        batch_xpath = f"//a[contains(., '{batch_name}')] | //h3[contains(., '{batch_name}')] | //div[contains(text(), '{batch_name}')]"
        batch_card = wait.until(EC.element_to_be_clickable((By.XPATH, batch_xpath)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", batch_card)
        time.sleep(0.5)
        batch_card.click()
        print(f"[Scraper] Successfully clicked batch!")

        time.sleep(2)
        dismiss_telegram_popup(driver)
        
        print(f"[Scraper] Searching for subject: {subject_name}")
        subject_xpath = f"//*[text()='{subject_name}' or contains(text(), '{subject_name}')]"
        subject_element = wait.until(EC.element_to_be_clickable((By.XPATH, subject_xpath)))
        
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", subject_element)
        time.sleep(1.5) 
        driver.execute_script("arguments[0].click();", subject_element)
        print(f"[Scraper] Successfully clicked subject!")

        time.sleep(3) 

        wait.until(EC.presence_of_all_elements_located((By.XPATH, "//button[contains(., 'Watch')]")))
        total_lectures = len(driver.find_elements(By.XPATH, "//button[contains(., 'Watch')]"))
        print(f"[Scraper] Found {total_lectures} lecture(s). Extracting...")

        for index in range(total_lectures):
            pdf_info = "No PDF Available"
            
            try:
                pdf_buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'btn-pdf')]")
                if index < len(pdf_buttons):
                    pdf_btn = pdf_buttons[index]
                    onclick_text = pdf_btn.get_attribute("onclick")
                    
                    if onclick_text and "dlPdf" in onclick_text:
                        match = re.search(r"dlPdf\('([^']*)',\s*'([^']*)'\)", onclick_text)
                        if match:
                            raw_pdf_id = match.group(1)
                            pdf_filename = match.group(2)
                            try:
                                real_pdf_id = base64.b64decode(raw_pdf_id).decode('utf-8')
                                pdf_info = f"https://player.uacdn.net/slides_pdf/{real_pdf_id}/{pdf_filename}"
                            except Exception:
                                pdf_info = f"https://player.uacdn.net/slides_pdf/{raw_pdf_id}/{pdf_filename}"
            except Exception:
                pdf_info = "Error capturing PDF"

            video_src = ""
            try:
                watch_buttons = driver.find_elements(By.XPATH, "//button[contains(., 'Watch')]")
                current_button = watch_buttons[index]

                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", current_button)
                time.sleep(1) 
                driver.execute_script("arguments[0].click();", current_button)

                video_element = wait.until(EC.presence_of_element_located((By.ID, "videoPlayer")))

                for _ in range(25): 
                    video_src = video_element.get_attribute("src")
                    if video_src and "uamedia.uacdn.net" in video_src:
                        break
                    time.sleep(0.5)
            except Exception:
                video_src = "Error loading video player"

            extracted_data.append({
                "lecture": index + 1,
                "video": video_src,
                "pdf": pdf_info
            })

            try:
                close_btn = driver.find_element(By.XPATH, "//div[@id='videoModal']//button | //div[@id='videoModal']//*[name()='svg'] | //div[contains(@class, 'modal-head')]/div")
                driver.execute_script("arguments[0].click();", close_btn)
            except Exception:
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            
            time.sleep(1.5) 

    except Exception as e:
        print(f"Scraper error: {e}")
    finally:
        driver.quit()

    return extracted_data

# ==========================================
# 2. ASYNC PYROGRAM HANDLER
# ==========================================
@Bot.on_message(filters.command("scrape"), group=25198)
async def handle_scrape_command(client: Bot, message: Message):
    command_args = message.text.replace('/scrape', '').strip()
    
    if '|' not in command_args:
        await message.reply_text(
            "❌ **Invalid format.**\n\nUse:\n`/scrape Batch Name | Subject Name`\n\nExample:\n`/scrape Kota NEET UG 2027 Master Pro 1 | Botany`",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    batch_name, subject_name = [x.strip() for x in command_args.split('|', 1)]
    
    status_msg = await message.reply_text(
        f"⏳ **Scraper Started!**\n\n**Batch:** `{batch_name}`\n**Subject:** `{subject_name}`\n\nPlease wait while links are being extracted...",
        parse_mode=ParseMode.MARKDOWN
    )

    try:
        data = await asyncio.to_thread(scrape_lectures_and_pdfs, batch_name, subject_name)
        
        if data:
            safe_subject_name = subject_name.replace(" ", "_").lower()
            filename = f"{safe_subject_name}_full_data.txt"

            with open(filename, "w", encoding="utf-8") as file:
                for item in data:
                    file.write(f"Lecture {item['lecture']}:\n")
                    file.write(f"Video URL: {item['video']}\n")
                    file.write(f"PDF URL:   {item['pdf']}\n")
                    file.write("-" * 50 + "\n")

            await message.reply_document(
                document=filename,
                caption=f"✅ Scraped **{len(data)}** lectures for **{subject_name}**!",
                parse_mode=ParseMode.MARKDOWN
            )
            
            if os.path.exists(filename):
                os.remove(filename)
                
            await status_msg.delete()

        else:
            await status_msg.edit_text("❌ Scraper finished, but no lectures were found. Please check the batch and subject names.")

    except Exception as e:
        await status_msg.edit_text(f"❌ An error occurred:\n`{str(e)}`", parse_mode=ParseMode.MARKDOWN)
