import os
import re
import time
import traceback
from pathlib import Path

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from bot import Bot
from plugins.coaching_profiles import list_profiles, get_profile
from plugins.parser import parse_pdf
from plugins.html_gen import render_cbt_html

# ---------------------------------------------------------------------------
# PDF -> CBT plugin
#
# /cbt (or a "PDF to CBT" button wired to callback_data "cbt_menu" from your
# main /help menu, same way "help_six" opens the six() educator menu below)
# shows a coaching picker; once picked, the next PDF the user sends is
# parsed with that coaching's profile and turned into a self-contained CBT
# HTML file (timer, palette, marking scheme, scorecard) sent back to them.
#
# Group numbers 270/271 are placeholders below the "six" example's group=260
# -- change them if your bot already uses those groups elsewhere.
# ---------------------------------------------------------------------------

WORKDIR = Path("./cbt_work")
WORKDIR.mkdir(exist_ok=True)

DEFAULT_MINUTES = 180
MARK_CORRECT = 4
MARK_WRONG = -1

# chat_id -> selected coaching profile id, until changed or a PDF is processed
pending_profile = {}

# chat_id -> {"path": <local qp pdf path>, "file_name": <original name>}
# Only used for two_pdf profiles (see coaching_profiles.py), e.g. AAKASH,
# where the question paper and the answer-key/solutions booklet come in
# as two separate PDF uploads. Single-PDF profiles (Allen, generic, ...)
# never touch this dict.
pending_qp = {}


def cbt_coaching_markup():
    rows = [
        [InlineKeyboardButton(label, callback_data=f"cbtcoach_{pid}")]
        for pid, label in list_profiles()
    ]
    rows.append([InlineKeyboardButton("Back", callback_data="help_cb")])
    return InlineKeyboardMarkup(rows)


def safe_stem(name):
    stem = Path(name).stem
    stem = re.sub(r"[^A-Za-z0-9_\-]+", "_", stem).strip("_")
    return stem or "test"


def _clear_pending(chat_id):
    pending_profile.pop(chat_id, None)
    qp = pending_qp.pop(chat_id, None)
    if qp:
        try:
            os.remove(qp["path"])
        except OSError:
            pass


@Bot.on_message(filters.command("cbt"), group=2630)
async def cbt_cmd(client: Bot, message: Message):
    _clear_pending(message.chat.id)
    await message.reply_text(
        text=''' Select your coaching ''',
        reply_markup=cbt_coaching_markup(),
    )


@Bot.on_callback_query(group=1727)
async def cbt_callbacks(client: Bot, query: CallbackQuery):
    data = query.data

    if data == "cbt_menu":
        _clear_pending(query.message.chat.id)
        await query.message.edit_text(
            text=''' Select your coaching ''',
            reply_markup=cbt_coaching_markup(),
        )

    elif data.startswith("cbtcoach_"):
        pid = data.split("cbtcoach_", 1)[1]
        pending_qp.pop(query.message.chat.id, None)  # start any new coaching fresh
        pending_profile[query.message.chat.id] = pid
        profile = get_profile(pid)
        label = profile["label"]
        await query.answer(f"Selected: {label}")
        if profile.get("two_pdf"):
            prompt = (
                f"Now send me the <b>question paper</b> PDF, then the "
                f"<b>answer-key / solutions</b> PDF for the same test as a "
                f"second file (in that order)."
            )
        else:
            prompt = "Now send me the PDF as a document."
        await query.message.edit_text(
            text=f''' ✅ Coaching set to <b>{label}</b>.

{prompt} Use /cbt any time to change this. ''',
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Change coaching", callback_data="cbt_menu")]]
            ),
        )


# NOTE: if your bot already has another `filters.document` handler (e.g. one
# that auto-forwards uploads into a storage channel for the file-store
# feature), both handlers will fire on the same PDF unless one of them raises
# pyrogram.StopPropagation() -- decide whether you want the PDF to also go
# through your normal file-store flow, and add that if not.
@Bot.on_message(filters.document, group=1782)
async def cbt_handle_pdf(client: Bot, message: Message):
    doc = message.document
    if not (doc.file_name or "").lower().endswith(".pdf"):
        return

    chat_id = message.chat.id
    profile_id = pending_profile.get(chat_id)
    if not profile_id:
        await message.reply_text(
            text=''' Pick which coaching this PDF is from first ''',
            reply_markup=cbt_coaching_markup(),
        )
        return

    profile = get_profile(profile_id)
    profile_label = profile["label"]

    # ---------- two_pdf profiles (e.g. AAKASH): collect QP, then the
    # answer-key/solutions PDF, before doing any parsing ----------
    if profile.get("two_pdf"):
        if chat_id not in pending_qp:
            status = await message.reply_text(
                f"📥 Downloading question paper… (profile: {profile_label})", quote=True
            )
            try:
                qp_path = await message.download(file_name=str(WORKDIR / doc.file_name))
            except Exception as e:
                await status.edit_text(f"Couldn't download that file: {e}")
                return
            pending_qp[chat_id] = {"path": qp_path, "file_name": doc.file_name}
            await status.edit_text(
                "✅ Got the question paper.\n\n"
                "Now send me the <b>answer-key / solutions</b> PDF for this same test."
            )
            return

        # second file for this chat -> the answer-key/solutions PDF
        qp_info = pending_qp[chat_id]
        status = await message.reply_text(
            f"📥 Downloading answer key / solutions… (profile: {profile_label})", quote=True
        )
        t0 = time.time()
        try:
            sol_path = await message.download(file_name=str(WORKDIR / doc.file_name))
        except Exception as e:
            await status.edit_text(f"Couldn't download that file: {e}")
            return

        try:
            await _process_and_send(
                message, status, profile_id, profile_label,
                qp_info["path"], qp_info["file_name"],
                second_pdf_path=sol_path,
            )
        finally:
            print(f"[pdf2cbt] {qp_info['file_name']} + {doc.file_name} "
                  f"({profile_id}): {time.time()-t0:.1f}s")
            pending_qp.pop(chat_id, None)
            for p in (qp_info["path"], sol_path):
                try:
                    os.remove(p)
                except OSError:
                    pass
        return

    # ---------- single-PDF profiles (Allen, generic, ...): unchanged flow ----------
    status = await message.reply_text(
        f"📥 Downloading PDF… (profile: {profile_label})", quote=True
    )
    t0 = time.time()
    try:
        pdf_path = await message.download(file_name=str(WORKDIR / doc.file_name))
    except Exception as e:
        await status.edit_text(f"Couldn't download that file: {e}")
        return

    try:
        await _process_and_send(
            message, status, profile_id, profile_label, pdf_path, doc.file_name
        )
    finally:
        print(f"[pdf2cbt] {doc.file_name} ({profile_id}): {time.time()-t0:.1f}s")
        try:
            os.remove(pdf_path)
        except OSError:
            pass


async def _process_and_send(message, status, profile_id, profile_label,
                             pdf_path, file_name, second_pdf_path=None):
    """Shared parse -> render -> send logic for both the single-PDF and
    two_pdf flows. Any exception is caught and reported on `status`."""
    try:
        await status.edit_text(
            "🔎 Reading questions, options, figures and the answer key…\n"
            "(scanned pages, if any, are OCR'd automatically — this can take a bit longer)"
        )
        data = parse_pdf(pdf_path, profile_id, second_pdf_path=second_pdf_path)

        if data["total"] == 0:
            await status.edit_text(
                f"I couldn't find any numbered questions in this PDF using the "
                f"<b>{profile_label}</b> profile. Try /cbt and pick a different one, "
                "or send this sample here so a profile can be tuned for it."
            )
            return

        unmapped = sum(
            1 for s in data["subjects"] for q in s["questions"] if q.get("answer") is None
        )

        await status.edit_text(
            f"🛠 Building the CBT ({data['total']} questions across "
            f"{len(data['subjects'])} subject(s))…"
        )
        html_out = render_cbt_html(
            data,
            title=safe_stem(file_name).replace("_", " "),
            default_minutes=DEFAULT_MINUTES,
            mark_correct=MARK_CORRECT,
            mark_wrong=MARK_WRONG,
        )

        out_path = WORKDIR / f"{safe_stem(file_name)}_CBT.html"
        out_path.write_text(html_out, encoding="utf-8")

        subj_line = ", ".join(
            f"{s['name']}: {len(s['questions'])}" for s in data["subjects"]
        )
        caption = (
            f"✅ CBT ready ({profile_label}) — {data['total']} questions\n{subj_line}\n"
            f"Marking: +{MARK_CORRECT} / {MARK_WRONG}, default {DEFAULT_MINUTES} min "
            "(editable at start)\n\n"
            "Download the HTML file and open it in any browser (phone or laptop) "
            "to attempt it in CBT mode."
        )
        if unmapped:
            caption += (
                f"\n\n⚠️ {unmapped} question(s) had no matching entry in the "
                "answer key — they'll show as unscored (0) in the result."
            )

        await message.reply_document(str(out_path), caption=caption, quote=True)
        await status.delete()

    except Exception:
        err = traceback.format_exc(limit=3)
        await status.edit_text(
            f"Something went wrong while processing this PDF:\n<code>{err}</code>"
        )
                                   
