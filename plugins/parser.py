"""
pdf2cbt.parser
Parses a coaching-style MCQ test PDF (question section + a subject-wise
answer-key section) into a structured dict, preserving figures/diagrams/
chemical-structures/formula-images exactly as they appear.

Two content sources, selected per page automatically:
  - NATIVE pages (PDF has a real text layer): walked block-by-block in
    reading order. Text blocks matching the profile's question/option
    regex start a new question/option; anything else (text or embedded
    raster image) between two such markers is attached to whichever
    question/option is currently "open".
  - SCANNED pages (no usable text layer): OCR is used only to *locate*
    where each question/option starts; the actual page raster between
    two consecutive marker positions is cropped and embedded as a
    picture, so diagrams/structures/formulas on scanned pages still
    come through correctly even though OCR text itself is unreliable
    for equation-heavy content.

A "coaching profile" (see coaching_profiles.py) supplies the regexes,
subject-header set, and answer-key heading/parsing mode, so the same
engine supports multiple coaching brands' PDF layouts.

Image handling notes:
  - Any raster figure/diagram is captured by taking a live screenshot of
    that block's bounding box directly from the rendered page, rather
    than extracting the raw embedded image stream. This sidesteps a
    whole class of rendering bugs (CMYK-encoded JPEGs, transparent
    backgrounds compositing to black, odd color spaces) because the
    screenshot is always a clean, correctly-colored RGB render of
    whatever is actually visible on the page.
  - Some coaching PDFs set formulas (fractions, roots, special symbols)
    with math fonts whose glyphs don't map to real Unicode text. When
    that happens, PyMuPDF's text extraction returns garbled characters
    (private-use-area codepoints / replacement chars) instead of the
    formula. Such text blocks are detected and, instead of showing the
    garbled text, are captured as an image screenshot of that block's
    bounding box too -- so unparseable formulas render correctly as a
    picture instead of gibberish or a blank/black gap.
"""
import re
import io
import base64
import pymupdf as fitz
from PIL import Image

from plugins.coaching_profiles import get_profile
import plugins.ocr as ocrmod


def _esc(text):
    return (text.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


# ---------------------------------------------------------------------------
# Garbled-text detection: math-font glyphs that don't decode to real text
# show up as private-use-area codepoints (U+E000-U+F8FF) or the Unicode
# replacement character (U+FFFD). If more than a small fraction of a text
# block's characters fall in that range, treat the block as unparseable
# and render it as an image instead.
# ---------------------------------------------------------------------------
_GARBLED_RE = re.compile(r"[\uE000-\uF8FF\uFFFD]")
_GARBLED_RATIO_THRESHOLD = 0.15
_GARBLED_MIN_HITS = 2  # ignore a single stray glyph (e.g. one bullet/symbol)


def _looks_garbled(txt):
    if not txt:
        return False
    hits = len(_GARBLED_RE.findall(txt))
    if hits < _GARBLED_MIN_HITS:
        return False
    return (hits / max(len(txt), 1)) > _GARBLED_RATIO_THRESHOLD


# ---------------------------------------------------------------------------
# Rendering embedded/garbled content as a clean screenshot of the page
# region, instead of trusting raw extracted image bytes or broken text.
# ---------------------------------------------------------------------------
def _render_bbox(page, bbox, zoom=2.0, pad=2):
    """Render the given bbox (page-space rect) as a PNG screenshot of the
    live page. Always produces a clean, correctly-colored RGB image on a
    white background -- no CMYK/alpha/color-space issues, since this is
    a fresh render rather than extracted raw image bytes."""
    rect = fitz.Rect(bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad)
    rect = rect & page.rect
    if rect.is_empty or rect.width <= 0 or rect.height <= 0:
        rect = page.rect
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, clip=rect)
    return "png", pix.tobytes("png")


def _normalize_image(ext, raw):
    """Fallback normalizer for image bytes that didn't come from a live
    page render (e.g. OCR-path crops that already went through
    ocrmod.crop_region, or any other raw bytes handed in directly).
    Forces CMYK/odd color spaces to RGB and composites any transparency
    onto white instead of letting it collapse to black."""
    try:
        pix = fitz.Pixmap(raw)
        if pix.colorspace is None or pix.colorspace.n not in (1, 3):
            pix = fitz.Pixmap(fitz.csRGB, pix)
        png_bytes = pix.tobytes("png")

        img = Image.open(io.BytesIO(png_bytes))
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            img = img.convert("RGBA")
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[-1])
            img = bg
        else:
            img = img.convert("RGB")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return "png", buf.getvalue()
    except Exception:
        return ext, raw


def _img_tag(ext, raw):
    b64 = base64.b64encode(raw).decode("ascii")
    return f'<img class="qimg" src="data:image/{ext};base64,{b64}">'


def _flush_text_run(buf):
    """Each buffered item is one original PDF text block: wrapped lines
    *within* a block are joined with a space (same sentence), separate
    blocks are joined with <br> (usually distinct lines/rows — important
    for match-the-column style questions)."""
    lines = []
    for x in buf:
        x = x.strip()
        if not x:
            continue
        lines.append(" ".join(part.strip() for part in x.split("\n") if part.strip()))
    buf.clear()
    if not lines:
        return ""
    return "<p>" + "<br>".join(_esc(l) for l in lines) + "</p>"


def _blocks_to_html(items):
    """items: list of ('text', str) | ('image', (ext, bytes))"""
    out = []
    textbuf = []
    for kind, payload in items:
        if kind == "text":
            textbuf.append(payload)
        else:
            out.append(_flush_text_run(textbuf))
            ext, raw = payload
            out.append(_img_tag(ext, raw))
    out.append(_flush_text_run(textbuf))
    return "".join(x for x in out if x)


def _find_section_page(doc, heading, start=0):
    for i in range(start, len(doc)):
        if heading.upper() in doc[i].get_text("text").upper():
            return i
    return None


def parse_pdf(pdf_path, profile_id="generic", second_pdf_path=None):
    """second_pdf_path: only used by two_pdf profiles (see
    coaching_profiles.py) -- e.g. AAKASH, where the question paper and
    the answer-key/solutions booklet are separate files. When given, its
    pages are appended to pdf_path's document and the answer-key section
    is taken to start exactly where pdf_path's pages end, instead of
    being located via profile["answer_key_heading"]. Single-PDF profiles
    (Allen, generic, ...) never pass this and are completely unaffected."""
    profile = get_profile(profile_id)
    subject_names = profile["subject_names"]
    question_re = profile["question_re"]
    option_re = profile["option_re"]

    doc = fitz.open(pdf_path)

    qp_page_count = None
    if second_pdf_path:
        qp_page_count = len(doc)
        doc2 = fitz.open(second_pdf_path)
        doc.insert_pdf(doc2)
        doc2.close()

    if qp_page_count is not None:
        # two_pdf profile: boundary is known exactly, no heading to search for.
        ak_page_idx = qp_page_count
    else:
        ak_page_idx = _find_section_page(doc, profile["answer_key_heading"])
        if ak_page_idx is None:
            ak_page_idx = len(doc)

    # ---------- figure out which question-section pages are scanned ----------
    scanned = {p: not ocrmod.page_has_text_layer(doc[p]) for p in range(ak_page_idx)}
    ocr_markers = {
        p: ocrmod.ocr_page_markers(doc[p], question_re, option_re, subject_names)
        for p in range(ak_page_idx) if scanned[p]
    }

    # ---------- shared state machine (used by both native & OCR walks) ----------
    subjects = []
    cur_subject = None
    cur_question = None
    cur_slot = None

    def new_subject(name):
        nonlocal cur_subject, cur_question, cur_slot
        cur_subject = {"name": name, "questions": []}
        subjects.append(cur_subject)
        cur_question = None
        cur_slot = None

    def new_question(local_no):
        nonlocal cur_question, cur_slot
        cur_question = {"local_no": local_no, "stem": [], "options": {}}
        cur_subject["questions"].append(cur_question)
        cur_slot = cur_question["stem"]

    def new_option(n):
        nonlocal cur_slot
        cur_question["options"][n] = []
        cur_slot = cur_question["options"][n]

    def expected_next_q():
        if cur_subject is None or not cur_subject["questions"]:
            return 1
        return cur_subject["questions"][-1]["local_no"] + 1

    def expected_next_o():
        existing = cur_question["options"]
        return 1 if not existing else max(existing) + 1

    # ---------- walk pages in order ----------
    for pno in range(ak_page_idx):
        page = doc[pno]

        if not scanned[pno]:
            d = page.get_text("dict")
            for b in d["blocks"]:
                if b["type"] == 0:
                    txt = "\n".join(
                        "".join(s["text"] for s in line["spans"])
                        for line in b["lines"]
                    ).strip()
                    if not txt:
                        continue
                    oneline = " ".join(txt.split())

                    if oneline.upper() in subject_names:
                        new_subject(oneline.upper())
                        continue
                    if cur_subject is None:
                        continue  # header/junk before the first subject

                    # Formula rendered with a math font whose glyphs don't
                    # decode to real text -> screenshot this block instead
                    # of emitting garbled characters.
                    if _looks_garbled(txt):
                        if cur_slot is not None:
                            ext, raw = _render_bbox(page, b["bbox"])
                            cur_slot.append(("image", (ext, raw)))
                        continue

                    m = question_re.match(txt)
                    if m and m.group(1).isdigit() and int(m.group(1)) == expected_next_q():
                        new_question(int(m.group(1)))
                        rest = m.group(2).strip() if m.lastindex and m.lastindex >= 2 else ""
                        if rest:
                            if _looks_garbled(rest):
                                ext, raw = _render_bbox(page, b["bbox"])
                                cur_slot.append(("image", (ext, raw)))
                            else:
                                cur_slot.append(("text", rest))
                        continue

                    if cur_question is not None:
                        mo = option_re.match(txt)
                        if mo and mo.group(1).isdigit():
                            n = int(mo.group(1))
                            if 1 <= n <= 4 and n == expected_next_o():
                                new_option(n)
                                rest = mo.group(2).strip() if mo.lastindex and mo.lastindex >= 2 else ""
                                if rest:
                                    if _looks_garbled(rest):
                                        ext, raw = _render_bbox(page, b["bbox"])
                                        cur_slot.append(("image", (ext, raw)))
                                    else:
                                        cur_slot.append(("text", rest))
                                continue

                    if cur_slot is not None:
                        cur_slot.append(("text", txt))

                else:  # image block -> screenshot its bbox from the live
                    # page instead of trusting the raw embedded stream
                    # (avoids CMYK/alpha color issues entirely).
                    if cur_slot is None:
                        continue
                    ext, raw = _render_bbox(page, b["bbox"])
                    cur_slot.append(("image", (ext, raw)))

        else:
            markers = ocr_markers.get(pno, [])
            for idx, mk in enumerate(markers):
                if idx + 1 < len(markers):
                    end_page, end_y = pno, markers[idx + 1]["y"]
                else:
                    nxt = pno + 1
                    if nxt < ak_page_idx and scanned.get(nxt) and ocr_markers.get(nxt):
                        end_page, end_y = nxt, ocr_markers[nxt][0]["y"]
                    elif nxt < ak_page_idx and scanned.get(nxt):
                        end_page, end_y = nxt, doc[nxt].rect.height
                    else:
                        end_page, end_y = pno, doc[pno].rect.height

                if mk["kind"] == "subject":
                    new_subject(mk["value"])
                    continue
                if cur_subject is None:
                    continue

                if mk["kind"] == "question" and mk["value"] == expected_next_q():
                    ext, raw = ocrmod.crop_region(doc, pno, mk["y"], end_page, end_y)
                    new_question(mk["value"])
                    cur_slot.append(("image", (ext, raw)))
                    continue

                if mk["kind"] == "option" and cur_question is not None and mk["value"] == expected_next_o():
                    ext, raw = ocrmod.crop_region(doc, pno, mk["y"], end_page, end_y)
                    new_option(mk["value"])
                    cur_slot.append(("image", (ext, raw)))
                    continue

                # sequence mismatch (OCR noise) -> treat as extra content
                # for whichever slot is currently open, if any
                if cur_slot is not None:
                    ext, raw = ocrmod.crop_region(doc, pno, mk["y"], end_page, end_y)
                    cur_slot.append(("image", (ext, raw)))

    # ---------- render each question's stem/options to HTML ----------
    global_no = 0
    for subj in subjects:
        for q in subj["questions"]:
            global_no += 1
            q["global_no"] = global_no
            q["stem_html"] = _blocks_to_html(q["stem"])
            opts_html = []
            for n in (1, 2, 3, 4):
                items = q["options"].get(n, [])
                opts_html.append(_blocks_to_html(items) or "&nbsp;")
            q["options_html"] = opts_html
            del q["stem"], q["options"]

    # drop any subject that ended up with zero questions (e.g. a stray
    # header match with nothing following before the answer key)
    subjects = [s for s in subjects if s["questions"]]

    # ---------- answer key ----------
    ak_end_idx = None
    if profile.get("solutions_heading"):
        ak_end_idx = _find_section_page(doc, profile["solutions_heading"], start=ak_page_idx)
    ak_text = ""
    for pno in range(ak_page_idx, (ak_end_idx if ak_end_idx else len(doc))):
        ak_text += doc[pno].get_text("text")

    all_questions = [q for s in subjects for q in s["questions"]]
    best_map, best_coverage = {}, -1
    _AK_PARSERS = {
        "qa_table": _parse_qa_table,
        "inline_list": _parse_inline_list,
        "grid_list": _parse_grid_list,
    }
    for mode in profile.get("answer_key_modes", ["qa_table"]):
        m = _AK_PARSERS.get(mode, _parse_qa_table)(ak_text)
        cov = sum(1 for q in all_questions if q["global_no"] in m)
        if cov > best_coverage:
            best_map, best_coverage = m, cov

    for q in all_questions:
        q["answer"] = best_map.get(q["global_no"])

    doc.close()
    return {"subjects": subjects, "total": global_no}


def _parse_qa_table(ak_text):
    """'Q. 1 2 3 ... \\n A. 3 3 1 ...' repeating rows, global numbering."""
    answer_map = {}
    tokens = ak_text.split()
    i = 0
    pending_qnos = None
    while i < len(tokens):
        tok = tokens[i]
        if tok == "Q.":
            nums = []
            i += 1
            while i < len(tokens) and tokens[i] != "A.":
                if tokens[i].isdigit():
                    nums.append(int(tokens[i]))
                i += 1
            pending_qnos = nums
        elif tok == "A." and pending_qnos:
            i += 1
            ans = []
            while i < len(tokens) and len(ans) < len(pending_qnos) and tokens[i].isdigit() and len(tokens[i]) == 1:
                ans.append(int(tokens[i]))
                i += 1
            for qn, a in zip(pending_qnos, ans):
                answer_map[qn] = a
            pending_qnos = None
            continue
        else:
            i += 1
    return answer_map


_INLINE_RE = re.compile(r"\b(\d{1,3})\s*[\.\)]\s*\(?\s*([1-4])\s*\)?")


def _parse_inline_list(ak_text):
    """'1. (3)  2. (1)  3) 4 ...' style — <num> <sep> <ans 1-4>, anywhere
    in the section, in order."""
    answer_map = {}
    last_n = 0
    for m in _INLINE_RE.finditer(ak_text):
        n, a = int(m.group(1)), int(m.group(2))
        # basic sanity: question numbers should increase (rejects noise
        # like stray "12.5" or unrelated numbers-with-punctuation)
        if n == last_n + 1:
            answer_map[n] = a
            last_n = n
    return answer_map


def _parse_grid_list(ak_text):
    """Same '<num>. (<ans>)' matching as inline_list, but WITHOUT the
    strict "next number must be previous+1" gate. Needed for answer-key
    pages laid out as several side-by-side columns per row (e.g. AAKASH:
    "1.  (1)      24.  (2)" on one line, "2.  (2)      25.  (4)" on the
    next ...), where plain text extraction interleaves the columns
    row-major and inline_list's adjacency check would reject every
    second-column entry as noise. First match seen for a given number
    wins (later duplicate/garbled hits are ignored)."""
    answer_map = {}
    for m in _INLINE_RE.finditer(ak_text):
        n, a = int(m.group(1)), int(m.group(2))
        if n not in answer_map:
            answer_map[n] = a
    return answer_map


if __name__ == "__main__":
    import sys
    profile_id = sys.argv[2] if len(sys.argv) > 2 else "generic"
    data = parse_pdf(sys.argv[1], profile_id)
    for s in data["subjects"]:
        print(s["name"], len(s["questions"]))
        for q in s["questions"][:2]:
            print("  Q", q["global_no"], q["local_no"], "ans=", q.get("answer"))
            print("   stem:", q["stem_html"][:120])
    print("TOTAL:", data["total"])
