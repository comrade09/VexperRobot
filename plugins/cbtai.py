import os
import re
import json
import html
import base64
import asyncio
import time
from pathlib import Path

import fitz  # PyMuPDF
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from google import genai

# ============================================================
# CONFIGURATION & SETUP
# ============================================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
client_ai = genai.Client(api_key=GEMINI_API_KEY)

# In-memory dictionary for user state management
# Format: { user_id: {"state": str, "q_pdf": str, "a_pdf": str} }
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

# ============================================================
# HTML GENERATOR
# ============================================================
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

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title_safe} — CBT</title>
<style>
:root {{
    --nav:#0f172a; --nav2:#1e293b; --accent:#3b82f6; --green:#10b981;
    --purple:#8b5cf6; --red:#ef4444; --grey:#64748b; --bg:#f8fafc;
}}
* {{ box-sizing:border-box; font-family: 'Segoe UI', system-ui, sans-serif; }}
body {{ margin:0; background:var(--bg); color:#1e293b; }}

/* HEADER */
header {{ background:var(--nav); color:white; padding:12px 20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; position:sticky; top:0; z-index:50; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
.title-box {{ display: flex; flex-direction: column; }}
.title {{ font-weight:700; font-size:16px; letter-spacing: 0.5px; }}
.credits {{ font-size: 11px; color: #94a3b8; margin-top: 3px; font-weight: 500; }}
.head-join-btn {{ background: #0ea5e9; color: white; text-decoration: none; padding: 8px 16px; border-radius: 6px; font-size: 13px; font-weight: 600; margin-right: auto; margin-left: 20px; transition: all 0.2s; }}
.head-join-btn:hover {{ background: #0284c7; transform: translateY(-1px); }}
#timer {{ background:#f1f5f9; color:var(--nav); font-weight:700; padding:8px 16px; border-radius:6px; font-size:16px; letter-spacing:1px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.05); }}
#timer.low {{ background:var(--red); color:white; }}

/* TABS & LAYOUT */
.subject-tabs {{ display:flex; gap:4px; background:var(--nav2); padding:8px 12px 0; overflow-x:auto; }}
.subject-tabs button {{ background:transparent; border:none; color:#cbd5e1; padding:10px 18px; border-radius:8px 8px 0 0; cursor:pointer; font-size:14px; font-weight: 600; white-space:nowrap; transition: all 0.2s; }}
.subject-tabs button:hover {{ color: white; }}
.subject-tabs button.active {{ background:var(--bg); color:var(--nav); }}
.layout {{ display:flex; align-items:flex-start; max-width: 1400px; margin: 0 auto; }}
main {{ flex:1; min-width:0; padding:24px; padding-bottom:100px; }}
aside {{ width:300px; flex-shrink:0; background:white; border-left:1px solid #e2e8f0; padding:20px; max-height:calc(100vh - 100px); overflow-y:auto; position:sticky; top:90px; }}
@media(max-width:820px) {{ .layout {{ flex-direction:column; }} aside {{ width:100%; position:static; max-height:none; order:2; border-left: none; border-top: 1px solid #e2e8f0; }} main {{ order:1; padding: 16px; }} }}

/* CARDS & UI */
.qcard {{ background:white; border-radius:12px; padding:24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03); border: 1px solid #f1f5f9; }}
.qhead {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:16px; padding-bottom: 12px; border-bottom: 2px dashed #f1f5f9; }}
.qhead b {{ font-size:18px; color:var(--nav); }}
.qstem {{ font-size:16px; line-height:1.7; margin-bottom:24px; color: #334155; }}
.figure-details {{ background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #3b82f6; border-radius: 8px; padding: 16px; margin-top: 20px; margin-bottom: 20px; }}
.figure-details summary {{ font-weight: 600; color: #1e293b; cursor: pointer; font-size: 15px; outline: none; }}
.figure-details img {{ max-width: 100%; height: auto; margin-top: 16px; border: 1px solid #cbd5e1; border-radius: 6px; }}
.opt {{ display:flex; align-items:flex-start; gap:12px; border:2px solid #e2e8f0; border-radius:10px; padding:14px 16px; margin-bottom:12px; cursor:pointer; transition: all 0.2s; }}
.opt:hover {{ border-color:#cbd5e1; background: #f8fafc; }}
.opt.selected {{ border-color:var(--accent); background:#eff6ff; }}
.opt input {{ margin-top:5px; transform: scale(1.2); }}
.optbody {{ font-size:15px; line-height:1.6; }}
.btnrow {{ display:flex; flex-wrap:wrap; gap:10px; margin-top:24px; }}
button.act {{ border:none; border-radius:8px; padding:12px 20px; font-size:14px; cursor:pointer; font-weight:600; transition: all 0.2s; }}
button.act:hover {{ opacity: 0.9; transform: translateY(-1px); }}
.b-mark {{ background:var(--purple); color:white; }}
.b-clear {{ background:var(--grey); color:white; }}
.b-prev {{ background:#e2e8f0; color:#334155; }}
.b-save {{ background:var(--green); color:white; }}
.b-submit {{ background:var(--red); color:white; }}
.footerbar {{ position:fixed; bottom:0; left:0; right:0; background:white; border-top:1px solid #e2e8f0; padding:16px 24px; display:flex; justify-content:space-between; z-index:40; box-shadow: 0 -4px 6px -1px rgba(0,0,0,0.05); }}
.footerbar .right {{ display:flex; gap:10px; }}

/* PALETTE */
.legend {{ display:flex; flex-wrap:wrap; gap:12px; font-size:12px; font-weight: 500; margin-bottom:20px; color: #475569; }}
.legend span {{ display:flex; align-items:center; gap:6px; }}
.dot {{ width:14px; height:14px; border-radius:4px; display:inline-block; }}
.pal-grid {{ display:grid; grid-template-columns: repeat(5,1fr); gap:8px; }}
.pal-grid button {{ border:none; border-radius:6px; height:38px; font-size:13px; font-weight:700; cursor:pointer; color:white; background:#cbd5e1; transition: all 0.1s; }}
.pal-grid button:hover {{ transform: scale(1.05); }}
.st-notvisited {{ background:#cbd5e1 !important; color: #475569 !important; }}
.st-notanswered {{ background:var(--red) !important; }}
.st-answered {{ background:var(--green) !important; }}
.st-marked {{ background:var(--purple) !important; }}
.st-markedans {{ background:var(--purple) !important; box-shadow: inset 0 0 0 3px var(--green); }}
.current {{ outline:3px solid #f59e0b; outline-offset: 2px; }}

/* SCREENS */
#startScreen, #resultScreen {{ max-width:600px; margin:60px auto; background:white; border-radius:16px; padding:40px 32px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05); text-align: center; border: 1px solid #f1f5f9; }}
#startScreen h2, #resultScreen h2 {{ color:var(--nav); margin: 0 0 8px 0; font-size: 24px; }}
#startScreen button, #resultScreen button {{ margin-top:30px; background:var(--nav); color:white; border:none; padding:14px 32px; border-radius:8px; font-size:16px; cursor:pointer; font-weight:700; width: 100%; transition: all 0.2s; }}
#startScreen button:hover, #resultScreen button:hover {{ background: #334155; transform: translateY(-2px); }}
.score-grid {{ display:grid; grid-template-columns: repeat(2,1fr); gap:16px; margin:24px 0; }}
.score-box {{ background:#f8fafc; border: 1px solid #e2e8f0; border-radius:12px; padding:20px; text-align:center; }}
.score-box b {{ display:block; font-size:28px; color:var(--nav); margin-bottom: 4px; }}
.score-box span {{ font-size:13px; color:#64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }}
.hide {{ display:none !important; }}

/* TELEGRAM POPUP */
.tg-overlay {{ position:fixed; inset:0; background:rgba(15, 23, 42, 0.75); display:flex; align-items:center; justify-content:center; z-index:99999; backdrop-filter: blur(4px); }}
.tg-popup {{ width:90%; max-width:380px; background:white; border-radius:20px; padding:32px 24px; text-align:center; position:relative; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.25); animation:tgPop 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; }}
@keyframes tgPop {{ from {{ transform:scale(0.8) translateY(20px); opacity:0; }} to {{ transform:scale(1) translateY(0); opacity:1; }} }}
.tg-close {{ position:absolute; right:16px; top:12px; border:none; background:transparent; font-size:28px; color:#94a3b8; cursor:pointer; line-height:1; transition: color 0.2s; }}
.tg-close:hover {{ color:#0f172a; }}
.tg-icon {{ font-size:48px; margin-bottom:12px; line-height: 1; }}
.tg-title {{ margin:0 0 12px; color:var(--nav); font-size:20px; font-weight:800; }}
.tg-text {{ margin:0 0 24px; color:#64748b; font-size:15px; line-height:1.6; }}
.tg-join {{ display:inline-block; background:#0ea5e9; color:white !important; text-decoration:none; padding:12px 32px; border-radius:10px; font-size:15px; font-weight:700; transition: all 0.2s; box-shadow: 0 4px 6px -1px rgba(14, 165, 233, 0.3); }}
.tg-join:hover {{ background:#0284c7; transform: translateY(-2px); box-shadow: 0 6px 8px -1px rgba(14, 165, 233, 0.4); }}
</style>
</head>
<body>

<!-- TELEGRAM POPUP -->
<div id="telegramPopup" class="tg-overlay">
    <div class="tg-popup">
        <button class="tg-close" onclick="closeTelegramPopup()" aria-label="Close">×</button>
        <div class="tg-icon">🚀</div>
        <h3 class="tg-title">Join Voltaic Network</h3>
        <p class="tg-text">Level up your prep. Get free NEET tests, latest study resources, and updates straight to your Telegram.</p>
        <a href="https://t.me/voltaic_network" target="_blank" class="tg-join">Join Channel</a>
    </div>
</div>

<!-- START SCREEN -->
<div id="startScreen">
    <div style="font-size: 40px; margin-bottom: 16px;">📝</div>
    <h2>{title_safe}</h2>
    <p class="credits">✨ Built & Extracted by @a3xarva</p>
    
    <div style="background: #f8fafc; border-radius: 8px; padding: 16px; margin: 24px 0; text-align: left; border: 1px solid #e2e8f0;">
        <div style="margin-bottom: 8px;">📊 <strong>Questions:</strong> {len(questions)} (NEET-style CBT)</div>
        <div style="margin-bottom: 8px;">⏱️ <strong>Duration:</strong> 180 minutes</div>
        <div>🎯 <strong>Marking:</strong> +4 Correct | −1 Incorrect | 0 Skipped</div>
    </div>
    
    <button onclick="startTest()">Start Test Now</button>
</div>

<!-- TEST SCREEN -->
<div id="testScreen" class="hide">
<header>
    <div class="title-box">
        <div class="title">{title_safe}</div>
        <div class="credits">✨ Extracted by @a3xarva</div>
    </div>
    <a href="https://t.me/voltaic_network" target="_blank" class="head-join-btn">📢 Join Voltaic Network</a>
    <div id="timer">03:00:00</div>
    <button class="act b-submit" onclick="confirmSubmit()">Submit Test</button>
</header>
<div class="subject-tabs" id="subjectTabs"></div>
<div class="layout">
<main>
<div class="qcard">
<div class="qhead">
    <b id="qLabel"></b>
    <span id="qMeta" style="font-size:13px; font-weight: 600; color:#64748b; background: #f1f5f9; padding: 4px 10px; border-radius: 6px;"></span>
</div>
<div class="qstem" id="qStem"></div>
<div id="qOptions"></div>
<div class="btnrow">
    <button class="act b-mark" onclick="markReview()">Mark for Review & Next</button>
    <button class="act b-clear" onclick="clearResponse()">Clear Response</button>
</div>
</div>
</main>
<aside>
<div class="legend">
    <span><i class="dot st-notvisited"></i> Not Visited</span>
    <span><i class="dot st-notanswered"></i> Not Answered</span>
    <span><i class="dot st-answered"></i> Answered</span>
    <span><i class="dot st-marked"></i> Marked</span>
    <span><i class="dot st-markedans"></i> Marked & Answered</span>
</div>
<div class="pal-grid" id="palette"></div>
</aside>
</div>
<div class="footerbar">
    <button class="act b-prev" onclick="goPrev()">← Previous</button>
    <div class="right">
        <button class="act b-save" onclick="goNext()">Save & Next →</button>
    </div>
</div>
</div>

<!-- RESULT SCREEN -->
<div id="resultScreen" class="hide"></div>

<script>
/* DATA INJECTION */
const questions = {questions_json};
const answerKey = {answer_json};
const pageImages = {page_images_json};

let current = 0; let started = false; let remaining = 180 * 60;
let timerInterval = null; let popupInterval = null;

let answers = Array(questions.length).fill(null);
let marked = Array(questions.length).fill(false);
let visited = Array(questions.length).fill(false);

/* TELEGRAM POPUP LOGIC */
function showTelegramPopup() {{
    const popup = document.getElementById("telegramPopup");
    if (popup) popup.style.display = "flex";
}}
function closeTelegramPopup() {{
    const popup = document.getElementById("telegramPopup");
    if (popup) popup.style.display = "none";
}}
showTelegramPopup();
popupInterval = setInterval(showTelegramPopup, 300000);

/* TEST ENGINE LOGIC */
function subjects() {{ return [...new Set(questions.map(q => q.subject))]; }}

function startTest() {{
    document.getElementById("startScreen").classList.add("hide");
    document.getElementById("testScreen").classList.remove("hide");
    started = true; buildTabs(); buildPalette(); showQuestion(0);
    timerInterval = setInterval(updateTimer, 1000);
}}

function updateTimer() {{
    if (remaining <= 0) {{ clearInterval(timerInterval); submitTest(); return; }}
    remaining--;
    const h = Math.floor(remaining / 3600);
    const m = Math.floor((remaining % 3600) / 60);
    const s = remaining % 60;
    const timer = document.getElementById("timer");
    timer.textContent = String(h).padStart(2,"0") + ":" + String(m).padStart(2,"0") + ":" + String(s).padStart(2,"0");
    if (remaining <= 600) timer.classList.add("low");
}}

function buildTabs() {{
    const container = document.getElementById("subjectTabs");
    container.innerHTML = "";
    subjects().forEach(subject => {{
        const button = document.createElement("button");
        button.textContent = subject;
        button.onclick = () => {{
            const index = questions.findIndex(q => q.subject === subject);
            if(index >= 0) showQuestion(index);
        }};
        container.appendChild(button);
    }});
}}

function buildPalette() {{
    const palette = document.getElementById("palette");
    palette.innerHTML = "";
    questions.forEach((q,i) => {{
        const button = document.createElement("button");
        button.textContent = q.global_no;
        button.id = "pal_" + i;
        button.onclick = () => showQuestion(i);
        palette.appendChild(button);
    }});
    updatePalette();
}}

function updatePalette() {{
    questions.forEach((q,i) => {{
        const b = document.getElementById("pal_" + i);
        if(!b) return;
        b.className = "";
        if(marked[i] && answers[i] !== null) b.classList.add("st-markedans");
        else if(marked[i]) b.classList.add("st-marked");
        else if(answers[i] !== null) b.classList.add("st-answered");
        else if(visited[i]) b.classList.add("st-notanswered");
        else b.classList.add("st-notvisited");
        if(i === current) b.classList.add("current");
    }});
}}

function showQuestion(index) {{
    if(index < 0 || index >= questions.length) return;
    current = index; visited[index] = true;
    const q = questions[index]; const pageStr = String(q.page);

    document.getElementById("qLabel").textContent = "Question " + q.global_no;
    document.getElementById("qMeta").textContent = q.subject + " • " + (index + 1) + " / " + questions.length;

    let stem = q.question;
    stem = stem.replace(/\[FIGURE\]/gi, '<b style="color:#ef4444;">[See Diagram Below]</b>');
    stem = stem.replace(/\[FIGURE ON PAGE [^\]]+\]/gi, '<b style="color:#ef4444;">[See Diagram Below]</b>');
    let htmlContent = "<p>" + stem.replace(/\\n/g, "<br>") + "</p>";

    const needsImage = (q.question.toUpperCase().includes("[FIGURE") || q.options.join("").toUpperCase().includes("[FIGURE") || q.question.toUpperCase().includes("[IMAGE"));
    if (needsImage && pageImages[pageStr]) {{
        htmlContent += `
        <details class="figure-details" open>
            <summary>🖼️ Click to View Source Page for Diagram</summary>
            <img src="${{pageImages[pageStr]}}" alt="Source Page Image">
        </details>`;
    }}
    document.getElementById("qStem").innerHTML = htmlContent;

    const options = document.getElementById("qOptions");
    options.innerHTML = "";
    q.options.forEach((option,i) => {{
        const label = document.createElement("label");
        label.className = "opt";
        const input = document.createElement("input");
        input.type = "radio"; input.name = "question"; input.value = i;
        if(answers[index] === i) input.checked = true;

        input.onchange = () => {{
            answers[index] = i; updatePalette();
            document.querySelectorAll(".opt").forEach(x => x.classList.remove("selected"));
            label.classList.add("selected");
        }};

        let optText = option.replace(/\[FIGURE\]/gi, '<b style="color:#ef4444;">[See Diagram Above]</b>');
        const body = document.createElement("div");
        body.className = "optbody";
        body.innerHTML = "<b>" + String.fromCharCode(65+i) + ")</b> " + optText;

        label.appendChild(input); label.appendChild(body); options.appendChild(label);
        if(answers[index] === i) label.classList.add("selected");
    }});
    
    // Update active tab style
    document.querySelectorAll(".subject-tabs button").forEach(btn => {{
        if(btn.textContent === q.subject) btn.classList.add("active");
        else btn.classList.remove("active");
    }});

    updatePalette(); window.scrollTo({{ top:0, behavior:"smooth" }});
}}

function goNext() {{ if(current < questions.length - 1) showQuestion(current + 1); else confirmSubmit(); }}
function goPrev() {{ if(current > 0) showQuestion(current - 1); }}
function clearResponse() {{ answers[current] = null; showQuestion(current); }}
function markReview() {{ marked[current] = true; if(current < questions.length - 1) showQuestion(current + 1); else updatePalette(); }}

function confirmSubmit() {{
    const unanswered = answers.filter(x => x === null).length;
    if(confirm("Submit test now?\\n\\nUnattempted: " + unanswered)) submitTest();
}}

function submitTest() {{
    if(timerInterval) clearInterval(timerInterval);
    let correct = 0, wrong = 0, skipped = 0;
    questions.forEach((q,i) => {{
        if(answers[i] === null) {{ skipped++; return; }}
        const actual = answerKey[q.global_no];
        if(actual === undefined) return;
        if(answers[i] + 1 === actual) correct++; else wrong++;
    }});
    const hasKey = Object.keys(answerKey).length > 0;
    const attempted = questions.length - skipped;
    const score = hasKey ? (correct * 4 - wrong) : null;

    document.getElementById("testScreen").classList.add("hide");
    const result = document.getElementById("resultScreen");
    result.classList.remove("hide");

    let scoreHTML = hasKey ? `
        <div class="score-grid">
            <div class="score-box" style="background: #eff6ff; border-color: #bfdbfe;">
                <b style="color: #1d4ed8;">${{score}}</b><span style="color: #3b82f6;">Final Score</span>
            </div>
            <div class="score-box"><b>${{correct}}</b><span>Correct</span></div>
            <div class="score-box"><b>${{wrong}}</b><span>Incorrect</span></div>
            <div class="score-box"><b>${{skipped}}</b><span>Skipped</span></div>
        </div>
    ` : `
        <div class="score-grid">
            <div class="score-box"><b>${{attempted}}</b><span>Attempted</span></div>
            <div class="score-box"><b>${{skipped}}</b><span>Unattempted</span></div>
        </div>
        <p style="color: #64748b; font-size: 14px; margin-bottom: 20px;">No answer key was supplied, so an actual NEET score could not be calculated.</p>
    `;

    result.innerHTML = `
        <div style="font-size: 48px; margin-bottom: 16px;">🏆</div>
        <h2>Test Submitted</h2>
        ${{scoreHTML}}
        <button onclick="location.reload()">Re-attempt Test</button>
    `;
}}
</script>
</body>
</html>
"""

# ============================================================
# BOT HANDLERS & PROGRESS
# ============================================================
@Client.on_message(filters.command("cbtai") & filters.private,group=66446)
async def start_cbt_process(client, message):
    USER_STATES[message.from_user.id] = {"state": "WAITING_FOR_Q_PDF"}
    await message.reply_text("📚 **CBT AI Converter**\n\nPlease upload the **Question PDF** (any coaching material).")

@Client.on_message(filters.document & filters.private,group=64532)
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

@Client.on_callback_query(filters.regex(r"^cbt_"),group=4223)
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


async def progress_updater(client, chat_id, msg_id, status_tracker):
    """Updates the message with the current progress every 5 seconds."""
    start_time = time.time()
    while status_tracker.get("is_running"):
        await asyncio.sleep(5)
        if not status_tracker.get("is_running"):
            break
        elapsed = int(time.time() - start_time)
        text = (f"⚙️ **CBT Transformation in Progress**\n\n"
                f"📌 **Status:** {status_tracker.get('status', 'Working...')}\n"
                f"⏱️ **Time Elapsed:** {elapsed}s\n"
                f"⏳ **Estimated Time:** 1 - 3 mins\n\n"
                f"*(Updates automatically every 5s)*")
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
        # 1. Extract Questions
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
        
        # Build the final success caption
        final_caption = (
            f"✅ **CBT Created Successfully!**\n\n"
            f"📄 **Test:** {title}\n"
            f"✨ **Extracted by:** @a3xarva\n"
            f"📢 **Channel:** [Voltaic Network](https://t.me/voltaic_network)\n\n"
            f"🌐 Open this HTML file in any browser (Chrome/Safari) to attempt the test."
        )

        await client.edit_message_text(chat_id, msg.id, "✅ **CBT Created Successfully!** Uploading file...")
        await client.send_document(chat_id, document=str(output_file), caption=final_caption)

    except Exception as e:
        status_tracker["is_running"] = False
        await updater_task
        await client.edit_message_text(chat_id, msg.id, f"❌ **Error during conversion:**\n`{str(e)}`")
    
    finally:
        # Cleanup downloaded files to save server space
        if q_pdf and os.path.exists(q_pdf): os.remove(q_pdf)
        if a_pdf and a_pdf != q_pdf and os.path.exists(a_pdf): os.remove(a_pdf)
