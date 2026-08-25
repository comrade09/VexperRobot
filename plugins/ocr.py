"""
OCR fallback for scanned/image-only PDF pages.

A PyMuPDF page with (essentially) no extractable text layer is treated as
scanned. Rather than trying to reconstruct clean text from OCR (unreliable
for equation-heavy coaching papers), this module uses OCR only to *locate*
where each question/option starts on the page (line-level bounding boxes),
then crops the actual page raster between those boundaries and embeds that
crop as a picture — so diagrams, structures and formulas on scanned pages
come through visually correct even though OCR text itself is imperfect.
"""
import io
import pytesseract
from PIL import Image
import pymupdf as fitz

MIN_TEXT_CHARS = 25   # below this, a page is considered "scanned"


def page_has_text_layer(page):
    return len(page.get_text("text").strip()) >= MIN_TEXT_CHARS


def ocr_page_markers(page, question_re, option_re, subject_names, zoom=2.5):
    """OCR the page and return line-level markers in reading order:
    [{'kind': 'subject'|'question'|'option', 'value': ..., 'y': <pdf-space y0>}]
    Content itself isn't extracted here — the caller crops the real page
    raster between marker boundaries once it knows where the *next*
    marker starts.
    """
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

    lines = {}
    for i in range(len(data["text"])):
        word = data["text"][i].strip()
        if not word:
            continue
        key = (data["block_num"][i], data["par_num"][i], data["line_num"][i])
        entry = lines.setdefault(key, {"words": [], "top": data["top"][i]})
        entry["words"].append(word)
        entry["top"] = min(entry["top"], data["top"][i])

    markers = []
    for _, info in sorted(lines.items(), key=lambda kv: kv[1]["top"]):
        text = " ".join(info["words"])
        y_pdf = info["top"] / zoom
        upper = text.strip().upper()
        if upper in subject_names:
            markers.append({"kind": "subject", "value": upper, "y": y_pdf})
            continue
        m = question_re.match(text)
        if m and m.group(1).isdigit():
            markers.append({"kind": "question", "value": int(m.group(1)), "y": y_pdf})
            continue
        m = option_re.match(text)
        if m and m.group(1).isdigit():
            n = int(m.group(1))
            if 1 <= n <= 4:
                markers.append({"kind": "option", "value": n, "y": y_pdf})
    return markers


def crop_region(doc, page_idx0, y0, page_idx1, y1, zoom=2.0, x_range=(20, 578)):
    """Render the content strictly between (page_idx0, y0) and
    (page_idx1, y1) — possibly spanning full pages in between — as one
    stitched PNG image. Returns (ext, raw_bytes)."""
    mat = fitz.Matrix(zoom, zoom)
    strips = []

    def render_clip(pidx, top, bottom):
        page = doc[pidx]
        rect = fitz.Rect(x_range[0], top, x_range[1], max(bottom, top + 1)) & page.rect
        pix = page.get_pixmap(matrix=mat, clip=rect)
        return Image.open(io.BytesIO(pix.tobytes("png")))

    if page_idx0 == page_idx1:
        strips.append(render_clip(page_idx0, y0, y1))
    else:
        strips.append(render_clip(page_idx0, y0, doc[page_idx0].rect.height))
        for pidx in range(page_idx0 + 1, page_idx1):
            strips.append(render_clip(pidx, 0, doc[pidx].rect.height))
        strips.append(render_clip(page_idx1, 0, y1))

    total_h = sum(s.height for s in strips)
    max_w = max(s.width for s in strips)
    canvas = Image.new("RGB", (max_w, total_h), "white")
    y = 0
    for s in strips:
        canvas.paste(s, (0, y))
        y += s.height
    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    return "png", buf.getvalue()
