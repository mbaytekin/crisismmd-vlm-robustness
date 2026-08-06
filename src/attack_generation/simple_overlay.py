from __future__ import annotations

from PIL import Image, ImageDraw

from src.attack_generation.text_rendering import fit_text


def draw_simple(image: Image.Image, text: str, font_ratio: float, min_font: int, padding_ratio: float, opacity: float, placement: str, max_area_ratio: float = 0.15):
    base = image.convert("RGBA")
    w, h = base.size
    font_size = max(min_font, round(h * font_ratio))
    padding = max(4, round(w * padding_ratio))
    text_width = max(20, w - 2 * padding)
    lines, font = fit_text(text, text_width, font_size, 2)
    # Prefer at most two lines, but never truncate the attack text. If a small
    # image cannot fit the complete string in two lines at min_font, preserve
    # the complete text and expose the extra line count for review.
    while font_size > min_font:
        probe_h = sum(font.getbbox(x)[3] - font.getbbox(x)[1] for x in lines) + max(2, round(font_size * 0.25)) * (len(lines) - 1) + 2 * padding
        probe_w = min(w - 2, max(font.getbbox(x)[2] for x in lines) + 2 * padding)
        if len(lines) <= 2 and (probe_w * probe_h) / (w * h) <= max_area_ratio: break
        font_size -= 1
        lines, font = fit_text(text, text_width, font_size, 2)
    while padding > 1:
        probe_gap = max(1, round(font_size * 0.10))
        probe_h = sum(font.getbbox(x)[3] - font.getbbox(x)[1] for x in lines) + probe_gap * (len(lines) - 1) + 2 * padding
        probe_w = min(w - 2, max(font.getbbox(x)[2] for x in lines) + 2 * padding)
        if (probe_w * probe_h) / (w * h) <= max_area_ratio: break
        padding -= 1
        lines, font = fit_text(text, text_width, font_size, 2)
    line_gap = max(1, round(font_size * 0.10))
    heights = [font.getbbox(x)[3] - font.getbbox(x)[1] for x in lines]
    box_h = sum(heights) + line_gap * (len(lines) - 1) + 2 * padding
    box_w = min(w - 2, max(font.getbbox(x)[2] for x in lines) + 2 * padding)
    x = (w - box_w) // 2
    y = padding if placement == "top_edge" else h - box_h - padding
    y = max(0, min(h - box_h, y))
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    alpha = round(255 * opacity)
    draw.rounded_rectangle((x, y, x + box_w, y + box_h), radius=max(2, padding // 2), fill=(0, 0, 0, alpha))
    ty = y + padding
    for line, line_h in zip(lines, heights):
        bbox = font.getbbox(line)
        tx = x + (box_w - (bbox[2] - bbox[0])) // 2
        draw.text((tx, ty), line, font=font, fill=(255, 255, 255, 255), stroke_width=0)
        ty += line_h + line_gap
    out = Image.alpha_composite(base, overlay).convert("RGB")
    return out, {"text_bbox": [x, y, x + box_w, y + box_h], "font_size_px": font_size, "relative_text_height": font_size / h, "occupied_area_ratio": (box_w * box_h) / (w * h), "opacity": opacity, "text_line_count": len(lines), "text_truncated": False}
