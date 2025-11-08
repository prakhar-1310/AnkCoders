# core/loshu.py
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from collections import Counter

LOSHU_LAYOUT = [
    [4, 9, 2],
    [3, 5, 7],
    [8, 1, 6]
]


def _load_font(size=48):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except:
        return ImageFont.load_default()


def _get_text_size(draw, text, font):
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:
        return draw.textsize(text, font=font)


def render_loshu_grid(digits, size=600):
    """Render a clean 3x3 Lo Shu grid with visible numbers and balanced colors"""
    freq = Counter(digits)

    img = Image.new("RGBA", (size, size), (10, 12, 25, 255))
    base_draw = ImageDraw.Draw(img)
    margin = int(size * 0.08)
    grid_size = size - margin * 2
    cell = grid_size // 3

    corner_font = _load_font(max(18, cell // 10))
    center_font = _load_font(max(28, cell // 3))

    for r in range(3):
        for c in range(3):
            x1 = margin + c * cell
            y1 = margin + r * cell
            x2 = x1 + cell
            y2 = y1 + cell
            num = LOSHU_LAYOUT[r][c]
            count = freq.get(num, 0)

            # Colors for different counts
            if count == 0:
                fill_color = (25, 30, 45, 255)
                glow_color = None
            elif count == 1:
                fill_color = (60, 85, 180, 255)
                glow_color = (100, 180, 255, 120)
            elif count == 2:
                fill_color = (90, 55, 180, 255)
                glow_color = (180, 130, 255, 120)
            else:
                fill_color = (20, 150, 120, 255)
                glow_color = (120, 255, 220, 150)

            # Draw glow first (behind cell)
            if glow_color:
                glow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
                gd = ImageDraw.Draw(glow_layer)
                gd.rounded_rectangle([x1 + 4, y1 + 4, x2 - 4, y2 - 4], radius=20, fill=glow_color)
                glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(8))
                img = Image.alpha_composite(img, glow_layer)
                base_draw = ImageDraw.Draw(img)

            # Draw cell
            base_draw.rounded_rectangle([x1, y1, x2, y2], radius=20, fill=fill_color,
                                        outline=(100, 110, 130, 255), width=2)

            # Draw Lo Shu number (top-left)
            base_draw.text((x1 + 10, y1 + 8), str(num), font=corner_font, fill=(190, 210, 255, 255))

            # Draw the digits or 0 in the center
            display_text = str(num) * count if count else "0"
            w, h = _get_text_size(base_draw, display_text, center_font)
            base_draw.text((x1 + (cell - w) / 2, y1 + (cell - h) / 2),
                           display_text, font=center_font, fill=(255, 255, 255, 255))

    # Outer border
    base_draw.rounded_rectangle([margin, margin, margin + grid_size, margin + grid_size],
                                radius=25, outline=(160, 170, 190, 255), width=3)

    return img
