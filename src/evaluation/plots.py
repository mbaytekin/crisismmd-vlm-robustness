from __future__ import annotations

from pathlib import Path


def bar_svg(path: Path, values: dict[str, float | None], title: str, ylabel: str, n: int = 0) -> None:
    width, height, left, bottom = 900, 460, 80, 340
    finite = [float(v) for v in values.values() if v is not None]
    signed = bool(finite and min(finite) < 0)
    upper = max(1.0, max(abs(v) for v in finite) * 1.15 if finite else 1.0)
    bar_w = max(24, (width - left - 30) // max(1, len(values)) - 18)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"><style>text{{font-family:Arial,sans-serif;fill:#222}}.axis{{stroke:#777}}.bar{{fill:#356da8}}</style><text x="{width/2}" y="30" text-anchor="middle" font-size="20">{title} (n={n})</text>']
    baseline = bottom - (bottom - 70) / 2 if signed else bottom
    svg.append(f'<line class="axis" x1="{left}" y1="{baseline}" x2="{width-20}" y2="{baseline}"/><line class="axis" x1="{left}" y1="50" x2="{left}" y2="{bottom}"/>')
    for i, (label, value) in enumerate(values.items()):
        x = left + 20 + i * ((width - left - 35) / max(1, len(values)))
        v = 0 if value is None else float(value)
        scale = ((bottom - 70) / 2 if signed else (bottom - 70))
        bh = v / upper * scale
        y = baseline - bh if bh >= 0 else baseline
        svg.append(f'<rect class="bar" x="{x}" y="{y}" width="{bar_w}" height="{abs(bh)}"/><text x="{x+bar_w/2}" y="{bottom+20}" text-anchor="middle" font-size="11" transform="rotate(25 {x+bar_w/2} {bottom+20})">{label}</text><text x="{x+bar_w/2}" y="{y-6 if bh >= 0 else y+abs(bh)+14}" text-anchor="middle" font-size="11">{v:.3f}</text>')
    svg.append(f'<text x="18" y="{height/2}" font-size="13" transform="rotate(-90 18 {height/2})">{ylabel}</text></svg>')
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text("".join(svg), encoding="utf-8")


def heatmap_svg(path: Path, matrix, labels, title: str) -> None:
    size, cell, left, top = 520, 88, 150, 80
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}"><style>text{{font-family:Arial,sans-serif;fill:#222}}</style><text x="260" y="28" text-anchor="middle" font-size="18">{title}</text>']
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            shade = max(0, min(255, 245 - int(float(value) * 24)))
            x, y = left + j * cell, top + i * cell
            svg.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="rgb(53,109,{shade})" stroke="white"/><text x="{x+cell/2}" y="{y+cell/2+5}" text-anchor="middle" font-size="20" fill="white">{int(value)}</text>')
    for i, label in enumerate(labels):
        svg.append(f'<text x="{left+i*cell+cell/2}" y="{top+len(labels)*cell+22}" text-anchor="middle" font-size="11">{label}</text><text x="{left-8}" y="{top+i*cell+cell/2+4}" text-anchor="end" font-size="11">{label}</text>')
    svg.append(f'<text x="{left+cell*1.5}" y="{size-12}" text-anchor="middle" font-size="12">predicted →</text><text x="18" y="{top+cell*1.5}" text-anchor="middle" font-size="12" transform="rotate(-90 18 {top+cell*1.5})">ground truth →</text></svg>')
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text("".join(svg), encoding="utf-8")
