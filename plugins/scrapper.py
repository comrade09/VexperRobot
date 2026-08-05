import os
import re
import json
import time
import random
import asyncio
import html as html_mod
from urllib.parse import unquote

import requests

# Engine 1 (best): curl_cffi impersonates a real Chrome TLS/HTTP2 fingerprint,
# which defeats Cloudflare bot-fight 403s on datacenter IPs.
try:
    from curl_cffi import requests as cffi_requests
    _cffi_session = cffi_requests.Session(impersonate="chrome")
except Exception:
    _cffi_session = None

# Engine 2: cloudscraper solves Cloudflare JS challenges.
try:
    import cloudscraper
    _cf_scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "desktop": True},
    )
except Exception:
    _cf_scraper = None

# Optional proxy: set env var SCRAPE_PROXY, e.g. http://user:pass@host:port
PROXY = os.environ.get("SCRAPE_PROXY") or None

from pyrogram import filters
from pyrogram.types import Message
from bot import Bot  # Matches your existing bot import

BASE = "https://studyuk.online/offline"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


# ==========================================
# 1. STEALTH SCRAPER LOGIC (no browser needed)
# ==========================================

def _clean_text(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", s).strip()


def _browser_headers(referer=None):
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Upgrade-Insecure-Requests": "1",
    }
    if referer:
        headers["Referer"] = referer
    return headers


def _is_challenge(text):
    head = text[:2000].lower()
    return ("just a moment" in head
            or "cf-browser-verification" in head
            or "cf-chl" in head
            or "enable javascript and cookies" in head)


def _http_get(url, timeout=30, referer=None):
    """Try engines in order: curl_cffi -> cloudscraper -> requests."""
    headers = _browser_headers(referer)

    if _cffi_session is not None:
        try:
            return _cffi_session.get(url, headers=headers, timeout=timeout, proxies=PROXY)
        except Exception:
            pass

    if _cf_scraper is not None:
        try:
            return _cf_scraper.get(url, headers=headers, timeout=timeout, proxies=PROXY)
        except Exception:
            pass

    return requests.get(url, headers=headers, timeout=timeout, proxies=PROXY)


def _fetch(url, timeout=30, referer=None, tries=4):
    last = None
    for attempt in range(tries):
        try:
            resp = _http_get(url, timeout=timeout, referer=referer)

            if resp.status_code in (403, 429, 503):
                last = RuntimeError(f"HTTP {resp.status_code} for {url} (blocked/rate-limited)")
                time.sleep(random.uniform(3, 7) * (attempt + 1))
                continue

            if resp.status_code != 200:
                raise RuntimeError(f"HTTP {resp.status_code} for {url}")

            if _is_challenge(resp.text):
                last = RuntimeError(f"Cloudflare challenge for {url}")
                time.sleep(random.uniform(4, 9) * (attempt + 1))
                continue

            return resp.text
        except requests.exceptions.RequestException as e:
            last = e
            time.sleep(random.uniform(2, 5) * (attempt + 1))
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


def extract_video_url(onclick_str):
    if not onclick_str:
        return ""
    match = re.search(r"openPlayerPopup\(\s*'([^']+)'", onclick_str)
    if match:
        return unquote(match.group(1))
    return ""


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


def parse_teacher_page(url, batch_page_url):
    page = _fetch(url, referer=batch_page_url)
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
        lecture_date = date_m.group(1) if date_m else ""

        v_m = re.search(r"openPlayerPopup\(\s*'([^']+)'", actions)
        video_url = unquote(v_m.group(1)) if v_m else ""

        p_m = re.search(r'href="([^"]+\.pdf)"', actions)
        pdf_url = html_mod.unescape(p_m.group(1)) if p_m else ""

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


def scrape_single_batch(batch_url):
    batch_url = batch_url.strip("`'\" \t\n\r")

    batch_id_match = re.search(r"batch_id=([a-zA-Z0-9]+)", batch_url)
    batch_id = batch_id_match.group(1) if batch_id_match else "Unknown_Batch"
    clean_url = f"{BASE}/batch-details.php?batch_id={batch_id}"

    # Warm up: visit the site root first so Cloudflare issues cookies
    # before we hit the deep pages.
    try:
        _fetch("https://studyuk.online/", timeout=30)
    except Exception:
        pass

    titles = get_batch_titles()
    batch_title = titles.get(batch_id, f"Batch_{batch_id}")
    safe_batch_title = re.sub(r'[\\/*?:"<>|]', "_", batch_title)

    html = _fetch(clean_url)
    teacher_urls = parse_teacher_urls(html)
    if not teacher_urls:
        raise RuntimeError("No teacher links found (page blocked or batch has no teachers)")

    batch_data = {
        "batch_title": batch_title,
        "batch_id": batch_id,
        "batch_url": clean_url,
        "teachers": [],
    }

    errors = []
    for t_idx, teacher_url in enumerate(teacher_urls, 1):
        try:
            batch_data["teachers"].append(parse_teacher_page(teacher_url, clean_url))
        except Exception as e:
            errors.append(f"{unquote(teacher_url.split('teacher=')[-1])[:30]}: {e}")
        time.sleep(random.uniform(0.8, 2.5))

    if not batch_data["teachers"]:
        raise RuntimeError("All teacher pages failed: " + "; ".join(errors))

    output_dir = "scraped_batches"
    os.makedirs(output_dir, exist_ok=True)

    json_path = os.path.join(output_dir, f"{safe_batch_title}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(batch_data, f, indent=4, ensure_ascii=False)

    txt_path = os.path.join(output_dir, f"{safe_batch_title}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"BATCH TITLE: {batch_title}\nBATCH URL:   {clean_url}\n" + "=" * 80 + "\n\n")
        for t in batch_data["teachers"]:
            f.write(f"TEACHER: {t['teacher_name']}\nLINK:    {t['teacher_url']}\n" + "-" * 60 + "\n")
            for l in t["lectures"]:
                f.write(f"Lecture: {l['lecture_title']}\n  Date:       {l['date']}\n  Video Link: {l['video_url']}\n  PDF Link:   {l['pdf_url']}\n\n")
            f.write("\n" + "=" * 80 + "\n\n")

    if errors:
        with open(os.path.join(output_dir, f"{safe_batch_title}_skipped.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(errors))

    return txt_path, json_path, None


# ==========================================
# 2. PYROGRAM BOT HANDLER
# ==========================================

@Bot.on_message(filters.command("scrape"), group=8787)
async def handle_scrape(client: Bot, message: Message):
    if len(message.command) < 2:
        await message.reply_text("⚠️ **Usage:** `/scrape <batch_url>`")
        return

    url = message.command[1]
    status_msg = await message.reply_text("⏳ **Scraping...**\n_Fetching teachers and lectures..._")

    try:
        txt_file, json_file, debug_img = await asyncio.to_thread(scrape_single_batch, url)

        await status_msg.edit_text("✅ **Scraping Complete!** Uploading files...")
        await message.reply_document(document=txt_file, caption="📄 Extracted Text Data")
        await message.reply_document(document=json_file, caption="📜 Extracted JSON Data")

        # Cleanup files from server
        try:
            os.remove(txt_file)
            os.remove(json_file)
            skipped = txt_file.replace(".txt", "_skipped.txt")
            if os.path.exists(skipped):
                os.remove(skipped)
        except Exception:
            pass

    except Exception as e:
        await status_msg.edit_text(f"❌ **Error during scraping:**\n`{str(e)}`")
