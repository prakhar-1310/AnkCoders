# core/pdf_report.py

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from PIL import Image

# ----------------------------------------------------
# ALWAYS SAFE FONT — No external file needed
# ----------------------------------------------------
FONT_NAME = "Helvetica"   # Built-in, guaranteed to work


# ----------------------------------------------------
# Draw chip tag (keyword pill)
# ----------------------------------------------------
def _draw_chip_safe(c: canvas.Canvas, x: float, y: float, text: str):
    pad_x = 2.5 * mm
    pad_y = 1.5 * mm

    c.setFont(FONT_NAME, 9)

    width = c.stringWidth(text, FONT_NAME, 9)
    box_w = width + pad_x * 2
    box_h = 6 * mm

    c.setFillColor(colors.HexColor("#1E2A3A"))
    c.roundRect(x, y, box_w, box_h, 2 * mm, fill=1, stroke=0)

    c.setFillColor(colors.HexColor("#E7F3FF"))
    c.drawString(x + pad_x, y + 1.5 * mm, text)

    return box_w + 2 * mm


# ----------------------------------------------------
# MAIN PDF GENERATOR
# ----------------------------------------------------
def create_pdf_report(filepath: str, payload: dict):

    c = canvas.Canvas(filepath, pagesize=A4)
    W, H = A4

    LEFT = 22 * mm
    RIGHT = W - 22 * mm
    TOP = H - 22 * mm

    y = TOP

    # -------------------------------------------------
    # HEADER
    # -------------------------------------------------
    c.setFont(FONT_NAME, 22)
    c.setFillColor(colors.HexColor("#80D8FF"))
    c.drawString(LEFT, y, "Numerology Report")
    y -= 16 * mm

    # -------------------------------------------------
    # USER INFO
    # -------------------------------------------------
    c.setFont(FONT_NAME, 12)
    c.setFillColor(colors.white)

    c.drawString(LEFT, y, f"Name: {payload['name']}")
    y -= 6 * mm
    c.drawString(LEFT, y, f"DOB: {payload['dob'].strftime('%d-%m-%Y')}")
    y -= 6 * mm
    c.drawString(LEFT, y, f"Gender: {payload['gender']}")
    y -= 12 * mm

    # -------------------------------------------------
    # SUMMARY
    # -------------------------------------------------
    c.setFont(FONT_NAME, 16)
    c.setFillColor(colors.HexColor("#80D8FF"))
    c.drawString(LEFT, y, "Core Numerology Numbers")
    y -= 10 * mm

    c.setFont(FONT_NAME, 12)
    res = payload["results"]

    for line in [
        f"Mulank: {res['Mulank']}",
        f"Bhagyank: {res['Bhagyank']}",
        f"Name Number: {res['Name Number']} (Total {res['Name Total']})",
        f"Angel Number: {res['Angel Number']}",
    ]:
        c.setFillColor(colors.white)
        c.drawString(LEFT + 4 * mm, y, line)
        y -= 7 * mm

    y -= 12 * mm

    # -------------------------------------------------
    # LOSHU GRID IMAGE
    # -------------------------------------------------
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
        except Exception as e:
            print("Image error:", e)

    # -------------------------------------------------
    # PHASE ANALYSIS
    # -------------------------------------------------
    y -= 10 * mm

    c.setFont(FONT_NAME, 16)
    c.setFillColor(colors.HexColor("#80D8FF"))
    c.drawString(LEFT, y, "Driver–Conductor Analysis")
    y -= 12 * mm

    phases = payload["phases"]

    for ph in ["0-40", "40-80"]:
        entry = phases[ph]

        # title
        c.setFont(FONT_NAME, 13)
        c.setFillColor(colors.HexColor("#A7D8FF"))
        c.drawString(
            LEFT,
            y,
            "0–40 Years (Mulank → Bhagyank)" if ph == "0-40"
            else "40–80 Years (Bhagyank → Mulank)"
        )
        y -= 10 * mm

        # stars & rating
        c.setFont(FONT_NAME, 12)
        c.setFillColor(colors.yellow)
        c.drawString(LEFT, y, f"Stars: {entry['stars_raw']}")
        c.setFillColor(colors.HexColor("#C8D8FF"))
        c.drawString(LEFT + 45 * mm, y, f"Rating: {entry['rating_clean']}")
        y -= 8 * mm

        # meaning
        c.setFont(FONT_NAME, 11)
        c.setFillColor(colors.white)

        for line in entry["meaning_raw"].split(". "):
            c.drawString(LEFT + 4 * mm, y, line.strip())
            y -= 6 * mm

        y -= 4 * mm

        # Keywords chips
        chip_x = LEFT + 4 * mm
        chip_y = y

        for kw in entry["meaning_clean"]:
            used_w = _draw_chip_safe(c, chip_x, chip_y, kw)
            chip_x += used_w

            if chip_x > RIGHT - 25 * mm:
                chip_x = LEFT + 4 * mm
                chip_y -= 10 * mm
                y -= 10 * mm

        y = chip_y - 12 * mm

        if y < 40 * mm:
            c.showPage()
            y = TOP - 20 * mm

    c.showPage()
    c.save()
