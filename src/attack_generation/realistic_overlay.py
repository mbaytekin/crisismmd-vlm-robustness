from __future__ import annotations

from PIL import Image, ImageDraw

from src.attack_generation.text_rendering import fit_text


def draw_realistic(image: Image.Image, text: str, font_ratio: float, min_font: int, padding_ratio: float, opacity: float, template: str, max_area_ratio: float = 0.15):
    base = image.convert("RGBA")
    w, h = base.size
    font_size = max(min_font, round(h * font_ratio))
    pad = max(4, round(w * padding_ratio))
    preferred_width = max(20, int(w * (0.55 if template != "watermark" else 0.45)))
    available_width = max(20, w - 2 * pad)
    text_width = min(preferred_width, available_width) - 2 * pad
    lines, font = fit_text(text, max(20, text_width), font_size, 2)
    # A realistic label may be narrower for short text, but long direct
    # prompts must expand to the available width instead of being truncated.
    if len(lines) > 2:
        text_width = available_width - 2 * pad
        lines, font = fit_text(text, max(20, text_width), font_size, 2)
    while font_size > min_font:
        probe_line_h = max(font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines)
        probe_h = probe_line_h * len(lines) + int(probe_line_h * 0.22) * (len(lines) - 1) + 2 * pad
        probe_w = min(w - 2, max(font.getbbox(line)[2] for line in lines) + 2 * pad)
        if len(lines) <= 2 and (probe_w * probe_h) / (w * h) <= max_area_ratio: break
        font_size -= 1
        lines, font = fit_text(text, max(20, text_width), font_size, 2)
    line_h = max(font.getbbox(line)[3] - font.getbbox(line)[1] for line in lines)
    box_w = min(w - 2, max(font.getbbox(line)[2] for line in lines) + 2 * pad)
    box_h = line_h * len(lines) + int(line_h * 0.22) * (len(lines) - 1) + 2 * pad
    if template == "news_lower_third":
        x, y, fill = 0, int(h * 0.73), (13, 35, 62, round(255 * opacity))
    elif template == "social_label":
        x, y, fill = pad, pad, (255, 255, 255, round(230 * opacity))
    elif template == "watermark":
        x, y, fill = w - box_w - pad, h - box_h - pad, (20, 20, 20, round(135 * opacity))
    else:
        x, y, fill = w - box_w - pad, pad, (154, 30, 27, round(245 * opacity))
    y = max(0, min(h - box_h, y))
    x = max(0, min(w - box_w, x))
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    radius = max(0, pad // 2) if template != "news_lower_third" else 0
    draw.rounded_rectangle((x, y, x + box_w, y + box_h), radius=radius, fill=fill)
    ty = y + pad
    for line in lines:
        bbox = font.getbbox(line)
        color = (25, 25, 25, 255) if template == "social_label" else (255, 255, 255, 255)
        draw.text((x + pad, ty), line, font=font, fill=color)
        ty += line_h + int(line_h * 0.22)
    out = Image.alpha_composite(base, overlay).convert("RGB")
    return out, {"text_bbox": [x, y, x + box_w, y + box_h], "font_size_px": font_size, "relative_text_height": font_size / h, "occupied_area_ratio": (box_w * box_h) / (w * h), "opacity": opacity, "text_line_count": len(lines), "text_truncated": False}
