from PIL import Image, ImageDraw, ImageFont, ImageFilter
from collections import Counter

LOSHU_LAYOUT = [
    [4, 9, 2],
    [3, 5, 7],
    [8, 1, 6]
]

# -----------------------------------------
# LOAD NORMAL / BOLD FONTS
# -----------------------------------------
def _load_font(size=48, bold=False):
    try:
        return ImageFont.truetype("arialbd.ttf" if bold else "arial.ttf", size)
    except:
        return ImageFont.load_default()

# For center alignment
def _get_text_size(draw, text, font):
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    except:
        return draw.textsize(text, font=font)

# -----------------------------------------
# RENDER LOSHU GRID WITH GLOW EFFECT
# -----------------------------------------
def render_loshu_grid(digits, size=520, background_path="assets/bg.png"):
    """
    - Smaller grid
    - Bold fonts
    - Golden glow for top-left digits
    - Aqua-green glow for center digits
    - Thin borders
    """
    freq = Counter(digits)

    # Load background
    try:
        bg = Image.open(background_path).convert("RGBA").resize((size, size))
    except:
        bg = Image.new("RGBA", (size, size), (20, 20, 20, 255))

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    margin = int(size * 0.12)
    grid_size = size - margin * 2
    cell = grid_size // 3

    corner_font = _load_font(max(24, cell // 8), bold=True)
    center_font = _load_font(max(42, cell // 3), bold=True)

    # --------------------------------------------------
    # MAIN LOOP
    # --------------------------------------------------
    for r in range(3):
        for c in range(3):
            x1 = margin + c * cell
            y1 = margin + r * cell
            x2 = x1 + cell
            y2 = y1 + cell

            num = LOSHU_LAYOUT[r][c]
            count = freq.get(num, 0)
            display_text = str(num) * count if count else "0"

            # Semi-transparent box
            fill_color = (255, 255, 255, 30)
            outline_color = (255, 255, 255, 255)

            # =====================================
            # MAIN CELL (THIN BORDER)
            # =====================================
            draw.rounded_rectangle(
                [x1, y1, x2, y2],
                radius=20,
                fill=fill_color,
                outline=outline_color,
                width=2       # thinner border
            )

            # =====================================
            # TOP-LEFT NUMBER — GOLDEN GLOW
            # =====================================
            tl_x = x1 + 8
            tl_y = y1 + 5

            glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
            gd = ImageDraw.Draw(glow)
            gd.text((tl_x, tl_y), str(num), font=corner_font, fill=(255, 215, 0, 255))
            glow = glow.filter(ImageFilter.GaussianBlur(radius=4))
            img = Image.alpha_composite(img, glow)
            draw = ImageDraw.Draw(img)

            draw.text((tl_x, tl_y), str(num), font=corner_font, fill=(255, 215, 0, 255))

            # =====================================
            # CENTER TEXT — AQUA GREEN GLOW
            # =====================================
            w, h = _get_text_size(draw, display_text, center_font)
            cx = x1 + (cell - w) / 2
            cy = y1 + (cell - h) / 2

            green = (46, 220, 200, 255)

            glow2 = Image.new("RGBA", img.size, (0, 0, 0, 0))
            gd2 = ImageDraw.Draw(glow2)
            gd2.text((cx, cy), display_text, font=center_font, fill=green)
            glow2 = glow2.filter(ImageFilter.GaussianBlur(radius=8))
            img = Image.alpha_composite(img, glow2)
            draw = ImageDraw.Draw(img)

            draw.text((cx, cy), display_text, font=center_font, fill=green)

    # =====================================
    # OUTER BORDER (THIN)
    # =====================================
    draw.rounded_rectangle(
        [margin, margin, margin + grid_size, margin + grid_size],
        radius=25,
        outline=(255, 255, 255, 255),
        width=3   # thinner outer border
    )

    return Image.alpha_composite(bg, img)
