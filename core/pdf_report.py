# core/pdf_report.py

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from PIL import Image

# ---------------------------------------------------------------------------
# FONT SETUP (uses DejaVuSans so all stars, half-stars, chips render correctly)
# ---------------------------------------------------------------------------
FONT_NAME = "DejaVuSans"
if FONT_NAME not in pdfmetrics.getRegisteredFontNames():
    try:
        pdfmetrics.registerFont(TTFont(FONT_NAME, "DejaVuSans.ttf"))
    except:
        pass  # fallback to default


# ---------------------------------------------------------------------------
# HELPER: Draw chip-style keyword tags
# ---------------------------------------------------------------------------
def _draw_chip_safe(c: canvas.Canvas, x: float, y: float, text: str):
    """
    Draws a rounded chip with blue-ish background.
    Returns width occupied so next chip knows where to start.
    """
    pad_x = 2.5 * mm
    pad_y = 1.5 * mm

    c.setFont(FONT_NAME, 9)

    width = c.stringWidth(text, FONT_NAME, 9)
    box_w = width + pad_x * 2
    box_h = 6 * mm

    # Background
    c.setFillColor(colors.HexColor("#1E2A3A"))
    c.roundRect(x, y, box_w, box_h, 2 * mm, fill=1, stroke=0)

    # Text
    c.setFillColor(colors.HexColor("#E7F3FF"))
    c.drawString(x + pad_x, y + 1.5 * mm, text)

    return box_w + 2 * mm


# ---------------------------------------------------------------------------
# MAIN PDF REPORT GENERATOR
# ---------------------------------------------------------------------------
def create_pdf_report(filepath: str, payload: dict):
    """
    payload structure:
    {
        "name": str,
        "dob": date,
        "gender": str,
        "results": {...},
        "loshu_image": "path/to/png",
        "phases": {
            "0-40": {
                "stars_raw": "...",
                "rating_clean": "...",
                "meaning_raw": "...",
                "meaning_clean": [...]
            },
            "40-80": {...}
        }
    }
    """

    c = canvas.Canvas(filepath, pagesize=A4)
    W, H = A4

    LEFT = 22 * mm
    RIGHT = W - 22 * mm
    TOP = H - 22 * mm

    y = TOP

    # ----------------------------------------------------------------------
    # HEADER
    # ----------------------------------------------------------------------
    c.setFont(FONT_NAME, 22)
    c.setFillColor(colors.HexColor("#80D8FF"))
    c.drawString(LEFT, y, "Numerology Report")
    y -= 16 * mm

    # ----------------------------------------------------------------------
    # USER INFO
    # ----------------------------------------------------------------------
    c.setFont(FONT_NAME, 12)
    c.setFillColor(colors.white)
    c.drawString(LEFT, y, f"Name: {payload['name']}")
    y -= 6 * mm
    c.drawString(LEFT, y, f"Date of Birth: {payload['dob'].strftime('%d-%m-%Y')}")
    y -= 6 * mm
    c.drawString(LEFT, y, f"Gender: {payload['gender']}")
    y -= 12 * mm

    # ----------------------------------------------------------------------
    # NUMEROLOGY SUMMARY
    # ----------------------------------------------------------------------
    c.setFont(FONT_NAME, 16)
    c.setFillColor(colors.HexColor("#80D8FF"))
    c.drawString(LEFT, y, "Core Numerology Numbers")
    y -= 10 * mm

    c.setFont(FONT_NAME, 12)
    res = payload["results"]

    lines = [
        f"Mulank (Birth Number): {res['Mulank']}",
        f"Bhagyank (Destiny Number): {res['Bhagyank']}",
        f"Name Number (Chaldean): {res['Name Number']} (Total: {res['Name Total']})",
        f"Angel Number: {res['Angel Number']}",
    ]

    for line in lines:
        c.setFillColor(colors.white)
        c.drawString(LEFT + 4 * mm, y, line)
        y -= 7 * mm

    y -= 12 * mm

    # ----------------------------------------------------------------------
    # LOSHU GRID IMAGE (Right side, properly scaled)
    # ----------------------------------------------------------------------
    img_path = payload.get("loshu_image")

    if img_path and os.path.exists(img_path):
        try:
            img = Image.open(img_path)
            w_img, h_img = img.size

            max_dim = 80 * mm
            scale = min(max_dim / w_img, max_dim / h_img)

            draw_w = w_img * scale
            draw_h = h_img * scale

            c.drawInlineImage(
                img_path,
                RIGHT - draw_w,
                TOP - draw_h,
                draw_w,
                draw_h
            )
        except:
            pass

    # ----------------------------------------------------------------------
    # DRIVER–CONDUCTOR ANALYSIS
    # ----------------------------------------------------------------------
    y -= 6 * mm
    c.setFont(FONT_NAME, 16)
    c.setFillColor(colors.HexColor("#80D8FF"))
    c.drawString(LEFT, y, "Driver–Conductor Analysis")
    y -= 12 * mm

    phases = payload["phases"]

    for ph in ["0-40", "40-80"]:
        title = (
            "0–40 Years (Mulank → Bhagyank)"
            if ph == "0-40"
            else "40–80 Years (Bhagyank → Mulank)"
        )

        entry = phases[ph]

        # ---- Section title ----
        c.setFont(FONT_NAME, 13)
        c.setFillColor(colors.HexColor("#A7D8FF"))
        c.drawString(LEFT, y, title)
        y -= 8 * mm

        # ---- Stars + Rating ----
        c.setFont(FONT_NAME, 12)
        c.setFillColor(colors.HexColor("#FFE082"))
        stars = entry["stars_raw"] or "—"
        rating = entry["rating_clean"] or "N/A"

        c.drawString(LEFT + 4 * mm, y, f"Stars: {stars}")
        c.setFillColor(colors.HexColor("#C8D8FF"))
        c.drawString(LEFT + 50 * mm, y, f"Rating: {rating}")
        y -= 9 * mm

        # ---- Meaning ----
        meaning_raw = entry["meaning_raw"] or "—"
        c.setFont(FONT_NAME, 11)
        c.setFillColor(colors.white)

        mt = c.beginText(LEFT + 4 * mm, y)
        mt.setFont(FONT_NAME, 11)
        mt.setLeading(14)

        wrapped_lines = []
        for part in meaning_raw.replace("\n", " ").split(". "):
            wrapped_lines.append(part.strip())

        for line in wrapped_lines:
            mt.textLine(line)
            y -= 5 * mm

        c.drawText(mt)

        y -= 4 * mm

        # ---- Keywords (Tags/Chips) ----
        kw = entry["meaning_clean"] or []

        chip_x = LEFT + 4 * mm
        chip_y = y

        for word in kw:
            used_width = _draw_chip_safe(c, chip_x, chip_y, word)
            chip_x += used_width

            # Wrap chips to next line
            if chip_x > RIGHT - 25 * mm:
                chip_x = LEFT + 4 * mm
                chip_y -= 10 * mm
                y -= 10 * mm

        y = chip_y - 14 * mm

        # Page break safety
        if y < 40 * mm:
            c.showPage()
            y = TOP - 20 * mm
            c.setFont(FONT_NAME, 14)

    # ----------------------------------------------------------------------
    # END REPORT
    # ----------------------------------------------------------------------
    c.showPage()
    c.save()
