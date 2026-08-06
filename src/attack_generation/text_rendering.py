from __future__ import annotations

from pathlib import Path

from PIL import ImageFont


def default_font() -> str:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return path
    return ""


def fit_text(text: str, width: int, font_size: int, max_lines: int | None = 2, allow_truncation: bool = False):
    font_path = default_font()
    font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
    words, lines, current = text.split(), [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if font.getbbox(trial)[2] <= width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    if max_lines is not None and len(lines) > max_lines and allow_truncation:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(" .") + "…"
    return lines, font
