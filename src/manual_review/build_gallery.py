from __future__ import annotations

import argparse
import html
from pathlib import Path

import pandas as pd

from src.config import resolve


CONDITIONS = ["benign_simple", "benign_realistic", "direct_simple", "direct_realistic", "indirect_simple", "indirect_realistic"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["pilot", "test"], default="pilot")
    args = ap.parse_args()
    split = pd.read_csv(resolve(f"data/splits/{args.split}.csv"), dtype=str)
    attack = pd.read_csv(resolve(f"data/attacks/{args.split}_attack_manifest.csv"), dtype=str)
    root_out = resolve("reports/manual_review")
    out = root_out / args.split
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for _, sample in split.iterrows():
        cells = [f'<td><img src="../../../{html.escape(sample.image_path)}"><br>clean</td>']
        meta_text = []
        for condition in CONDITIONS:
            hit = attack[(attack.sample_id == sample.sample_id) & (attack.condition == condition)]
            if hit.empty: continue
            r = hit.iloc[0]
            cells.append(f'<td><img src="../../../{html.escape(r.attacked_image_path)}"><br>{condition}</td>')
            meta_text.append(f"{condition}: {r.text_content} | bbox={r.text_bbox} | template={r.placement_template}")
        metadata = html.escape("\n".join(meta_text))
        rows.append(f'<tr><th>{html.escape(sample.sample_id)}<br>GT: {html.escape(sample.damage_label_normalized)}</th>{"".join(cells)}<td>{metadata}</td></tr>')
    table = "".join(rows)
    page = f'''<!doctype html><meta charset="utf-8"><title>CrisisMMD manual review - {args.split}</title><style>body{{font:14px sans-serif;background:#f4f4f4}}table{{border-collapse:collapse;background:white}}th,td{{border:1px solid #bbb;padding:6px;vertical-align:top}}img{{max-width:220px;max-height:180px;object-fit:contain}}pre{{white-space:pre-wrap;max-width:360px}}</style><h1>Manual review: {args.split}</h1><p>Human review is intentionally blank. Review the image validity and placement against the README protocol.</p><table><thead><tr><th>sample / ground truth</th><th>clean</th><th>benign simple</th><th>benign realistic</th><th>direct simple</th><th>direct realistic</th><th>indirect simple</th><th>indirect realistic</th><th>metadata</th></tr></thead><tbody>{table}</tbody></table>'''
    (out / "index.html").write_text(page, encoding="utf-8")
    template = []
    for sample_id in split.sample_id:
        for condition in ["clean"] + CONDITIONS:
            template.append({"sample_id": sample_id, "condition": condition, "reviewer_id": "", "label_still_valid": "", "text_readable": "", "critical_region_obscured": "", "placement_plausible": "", "image_usable": "", "approve": "", "review_notes": ""})
    pd.DataFrame(template).to_csv(out / "review_template.csv", index=False)
    links = []
    for split_name in ("pilot", "test"):
        if (root_out / split_name / "index.html").exists(): links.append(f'<li><a href="{split_name}/index.html">{split_name} review</a></li>')
    (root_out / "index.html").write_text("<!doctype html><meta charset='utf-8'><title>CrisisMMD manual review</title><h1>CrisisMMD manual review galleries</h1><ul>" + "".join(links) + "</ul>", encoding="utf-8")
    print(out / "index.html")


if __name__ == "__main__":
    main()
