"""Leakage-resistant V3 dataset and typographic attack generator.

V2 remains immutable as an experiment record.  V3 rebuilds split assignment and
visual interventions so that tweet/near-image groups cannot cross splits and
non-target visual factors are held fixed.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from src.attack_generation.text_rendering import default_font, fit_text
from src.config import ROOT, load_yaml, resolve
from src.evaluation.metrics import LABELS


V3_ROOT = ROOT / "data" / "v3"
V3_REPORT = ROOT / "reports" / "v3"
CONFIG = load_yaml("configs/v3/pipeline.yaml")
MOJIBAKE = re.compile(r"(?:Ã.|Â.|â.|ðŸ|\ufffd)")


def stable_int(value: str, seed: int | None = None) -> int:
    seed = CONFIG["seed"] if seed is None else seed
    return int.from_bytes(hashlib.sha256(f"{seed}:{value}".encode()).digest()[:8], "big")


def ensure_dirs() -> None:
    for path in [V3_ROOT / "splits", V3_ROOT / "manifests", V3_ROOT / "attacks",
                 V3_REPORT / "tables", V3_REPORT / "manual_review", ROOT / "results" / "v3"]:
        path.mkdir(parents=True, exist_ok=True)


class UnionFind:
    def __init__(self, n: int): self.parent = list(range(n))
    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]; x = self.parent[x]
        return x
    def union(self, a: int, b: int) -> None:
        a, b = self.find(a), self.find(b)
        if a != b: self.parent[b] = a


def build_duplicate_clusters(df: pd.DataFrame) -> pd.DataFrame:
    """Union exact tweet/image identities and dHash neighbours at Hamming <= 4."""
    df = df.reset_index(drop=True).copy(); uf = UnionFind(len(df))
    for column in ["tweet_id", "tweet_text", "sha256", "perceptual_hash"]:
        seen: dict[str, int] = {}
        for i, value in enumerate(df[column].fillna("").astype(str)):
            if not value: continue
            if value in seen: uf.union(i, seen[value])
            else: seen[value] = i
    hashes = []
    for i, value in enumerate(df.perceptual_hash.fillna("")):
        try: hashes.append((i, int(value, 16)))
        except ValueError: pass
    threshold = int(CONFIG["near_duplicate_hamming"])
    for pos, (i, value) in enumerate(hashes):
        for j, other in hashes[:pos]:
            if (value ^ other).bit_count() <= threshold: uf.union(i, j)
    roots = [uf.find(i) for i in range(len(df))]
    canonical = {root: f"cluster_{rank:05d}" for rank, root in enumerate(sorted(set(roots)))}
    df["duplicate_cluster_id"] = [canonical[uf.find(i)] for i in range(len(df))]
    df["suspected_mojibake"] = df.tweet_text.fillna("").str.contains(MOJIBAKE)
    return df


def choose_splits(pool: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Choose one row per cluster, class-balanced and event-aware."""
    targets = CONFIG["split_sizes_per_class"]
    # Rare labels first; small splits first prevents the main split consuming diversity.
    label_order = sorted(LABELS, key=lambda x: int((pool.damage_label_normalized == x).sum()))
    split_order = sorted(targets, key=lambda x: int(targets[x]))
    used: set[str] = set(); selected: dict[str, list[pd.Series]] = {x: [] for x in targets}
    event_counts: dict[tuple[str, str, str], int] = defaultdict(int)
    for label in label_order:
        candidates = pool[pool.damage_label_normalized == label].copy()
        # One deterministic candidate per (cluster,label), preferring complete paths/text.
        candidates["_rank"] = candidates.sample_id.map(lambda x: stable_int(str(x)))
        candidates = candidates.sort_values(["duplicate_cluster_id", "_rank"]).drop_duplicates("duplicate_cluster_id")
        for split in split_order:
            need = int(targets[split])
            for _ in range(need):
                available = candidates[~candidates.duplicate_cluster_id.isin(used)]
                if available.empty: raise RuntimeError(f"Insufficient independent clusters for {split}/{label}")
                # Fill under-represented events first, with stable hash tie-breaking.
                row = min(available.itertuples(), key=lambda r: (
                    event_counts[(split, label, str(r.event_name))],
                    stable_int(f"{split}:{label}:{r.event_name}:{r.sample_id}")))
                chosen = candidates[candidates.sample_id == row.sample_id].iloc[0]
                selected[split].append(chosen); used.add(str(chosen.duplicate_cluster_id))
                event_counts[(split, label, str(chosen.event_name))] += 1
    result = {}
    for split, rows in selected.items():
        frame = pd.DataFrame(rows).drop(columns=["_rank"], errors="ignore").sort_values("sample_id").reset_index(drop=True)
        frame["v3_split"] = split; result[split] = frame
    return result


def payloads() -> dict: return load_yaml("configs/v3/attack_payloads.yaml")


def payload_assignment(row: pd.Series) -> dict[str, str]:
    cfg = payloads(); out = {}
    for family in ["benign", "direct_instruction", "misleading_claim"]:
        ids = sorted(cfg[family]); pid = ids[stable_int(f"{row.sample_id}:{family}") % len(ids)]
        out[f"{family}_payload_id"] = pid; out[f"{family}_payload_text"] = cfg[family][pid]
    return out


def condition_spec(split: str, condition: str) -> tuple[str, str, str, str]:
    if condition == "clean": return "none", "none", "none", "none"
    semantics = "benign" if condition.startswith("benign") else "direct_instruction" if condition.startswith("direct") else "misleading_claim"
    if split in {"pilot", "main"}:
        modality = "image" if condition.endswith("image") else "text" if condition.endswith("text") else "joint"
        return modality, semantics, "simple_overlay" if modality != "text" else "none", "medium" if modality != "text" else "none"
    if split == "style_ablation":
        style = "simple_overlay" if condition.endswith("simple") else "news_banner" if condition.endswith("news") else "camouflage"
        return "image", semantics, style, "medium"
    return "image", semantics, "simple_overlay", condition.rsplit("_", 1)[-1]


def build_manifest(splits: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows, assignment_rows = [], []
    for split, frame in splits.items():
        conditions = CONFIG["conditions"]["main" if split in {"pilot", "main"} else split]
        for _, source in frame.iterrows():
            assigned = payload_assignment(source); assignment_rows.append({"sample_id": source.sample_id, "split_name": split, **assigned})
            for condition in conditions:
                modality, semantics, style, size = condition_spec(split, condition)
                if semantics == "none": pid = ptext = ""
                else: pid, ptext = assigned[f"{semantics}_payload_id"], assigned[f"{semantics}_payload_text"]
                visual_key = ""
                image_path = source.image_path
                if modality in {"image", "joint"}:
                    visual_key = f"{semantics}__{style}__{size}"
                    image_path = f"data/v3/attacks/{split}/{visual_key}/{source.sample_id}.webp"
                tweet = source.tweet_text if modality not in {"text", "joint"} else f"{ptext}\n\n{source.tweet_text}"
                placement = "" if modality not in {"image", "joint"} else ("top_edge" if stable_int(str(source.sample_id)) % 2 == 0 else "bottom_edge")
                rows.append({
                    "sample_id": source.sample_id, "duplicate_cluster_id": source.duplicate_cluster_id,
                    "tweet_id": source.tweet_id, "split_name": split, "condition": condition,
                    "attack_modality": modality, "attack_semantics": semantics, "visual_style": style,
                    "text_size": size, "payload_id": pid, "payload_text": ptext,
                    "original_image_path": source.image_path, "condition_image_path": image_path,
                    "original_tweet": source.tweet_text, "condition_tweet": tweet,
                    "ground_truth": source.damage_label_normalized, "event_name": source.event_name,
                    "perceptual_hash": source.perceptual_hash, "sha256": source.sha256,
                    "visual_key": visual_key, "placement_region": placement, "text_bbox": "",
                    "font_size_px": "", "relative_font_height": "", "line_count": "",
                    "occupied_area_ratio": "", "opacity": "", "background_color": "",
                    "text_color": "", "rendered_contrast_ratio": "", "edge_density": "",
                    "local_variance": "", "template_version": "v3", "generation_seed": CONFIG["seed"],
                    "generation_status": "not_applicable" if not visual_key else "pending", "generation_error": ""})
    manifest = pd.DataFrame(rows)
    pd.DataFrame(assignment_rows).drop_duplicates("sample_id").to_csv(V3_ROOT / "manifests" / "payload_assignments.csv", index=False)
    write_manifest(manifest); return manifest


def write_manifest(frame: pd.DataFrame) -> None:
    serial=frame.copy()
    for column in serial.columns: serial[column]=serial[column].fillna("").astype(str)
    serial.to_csv(V3_ROOT / "manifests" / "all_conditions.csv", index=False)
    serial.to_parquet(V3_ROOT / "manifests" / "all_conditions.parquet", index=False)


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    return ImageFont.truetype(default_font(), max(1, size)) if default_font() else ImageFont.load_default()


def _luminance(rgb) -> float:
    vals = [v / 255 for v in rgb]
    vals = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in vals]
    return .2126 * vals[0] + .7152 * vals[1] + .0722 * vals[2]


def contrast_ratio(a, b) -> float:
    x, y = _luminance(a), _luminance(b); return (max(x, y) + .05) / (min(x, y) + .05)


def _fixed_text(image: Image.Image, text: str, ratio: float, placement: str, opacity: float,
                style: str = "simple_overlay") -> tuple[Image.Image, dict]:
    base = image.convert("RGBA"); w, h = base.size; pad = max(2, round(w * .018)); target_fs = max(8, round(h * ratio))
    if style == "news_banner": box = (0, max(0, h - round(h * .20)), w, h); tx = round(w * .20) + pad; bg = (16, 31, 52); fg = (255, 255, 255)
    else:
        box_h = min(h, max(2 * pad + round(target_fs * 2.5), round(h * (ratio * 2.7))))
        y = 0 if placement == "top_edge" else h - box_h; box = (round(w * .04), y, round(w * .96), y + box_h); tx = box[0] + pad; bg = (0, 0, 0); fg = (255, 255, 255)
    available_w, available_h = max(8, box[2] - tx - pad), max(8, box[3] - box[1] - 2 * pad)
    chosen = None
    for fs in range(target_fs, 5, -1):
        lines, f = fit_text(text, available_w, fs, 2); gap = max(1, round(fs * .15))
        heights = [max(1, f.getbbox(line)[3] - f.getbbox(line)[1]) for line in lines]
        if len(lines) <= 2 and sum(heights) + gap * max(0, len(lines) - 1) <= available_h:
            chosen = fs, lines, f, heights, gap; break
    if chosen is None: raise RuntimeError("payload cannot fit fixed box")
    fs, lines, f, heights, gap = chosen; overlay = Image.new("RGBA", base.size, (0, 0, 0, 0)); draw = ImageDraw.Draw(overlay)
    draw.rectangle(box, fill=(*bg, round(opacity * 255)))
    if style == "news_banner":
        logo_w = round(w * .20); draw.rectangle((0, box[1], logo_w, box[3]), fill=(190, 35, 38, round(opacity * 255)))
        draw.text((pad, box[1] + pad), "CRISIS24", font=_font(max(7, round(fs * .55))), fill="white")
    ty = box[1] + pad
    for line, line_h in zip(lines, heights): draw.text((tx, ty), line, font=f, fill=(*fg, 255)); ty += line_h + gap
    output = Image.alpha_composite(base, overlay).convert("RGB")
    return output, {"text_bbox": list(box), "font_size_px": fs, "relative_font_height": fs / h,
        "line_count": len(lines), "occupied_area_ratio": ((box[2]-box[0])*(box[3]-box[1]))/(w*h),
        "opacity": opacity, "background_color": ",".join(map(str,bg)), "text_color": ",".join(map(str,fg)),
        "rendered_contrast_ratio": contrast_ratio(bg, fg), "placement_region": placement,
        "template_version": "crisis24_v3" if style == "news_banner" else "fixed_overlay_v3"}


def _camouflage(image: Image.Image, text: str, ratio: float, opacity: float) -> tuple[Image.Image, dict]:
    base = image.convert("RGB"); arr = np.asarray(base); gray = np.asarray(base.convert("L"), dtype=float); w, h = base.size
    regions = [("top",0,0,w,h//4),("bottom",0,3*h//4,w,h)]
    scored=[]
    for name,x1,y1,x2,y2 in regions:
        crop=gray[y1:y2,x1:x2]; edge=float(np.abs(np.diff(crop,axis=0)).mean()+np.abs(np.diff(crop,axis=1)).mean()); var=float(crop.var())
        scored.append((edge+math.sqrt(var),name,x1,y1,x2,y2,edge,var))
    _,name,x1,y1,x2,y2,edge,var=min(scored); bg=tuple(np.mean(arr[y1:y2,x1:x2],axis=(0,1)).round().astype(int)); target=(CONFIG["camouflage_contrast_min"]+CONFIG["camouflage_contrast_max"])/2
    best=None
    for endpoint in [(0,0,0),(255,255,255)]:
        for step in range(256):
            raw=tuple(round(bg[k]+(endpoint[k]-bg[k])*step/255) for k in range(3)); rendered=tuple(round(opacity*raw[k]+(1-opacity)*bg[k]) for k in range(3)); cr=contrast_ratio(bg,rendered)
            candidate=(abs(cr-target),raw,rendered,cr)
            if best is None or candidate[0]<best[0]: best=candidate
    _,fg,rendered,cr=best
    output, meta=_fixed_text(base,text,ratio,"top_edge" if name=="top" else "bottom_edge",opacity)
    # Replace simple overlay rendering with transparent text only in the same fixed geometry.
    box=meta["text_bbox"]; fs=meta["font_size_px"]; pad=max(2,round(w*.018)); lines,f=fit_text(text,max(8,box[2]-box[0]-2*pad),fs,2); overlay=Image.new("RGBA",base.size,(0,0,0,0)); draw=ImageDraw.Draw(overlay); ty=box[1]+pad; gap=max(1,round(fs*.15))
    for line in lines:
        draw.text((box[0]+pad,ty),line,font=f,fill=(*fg,round(opacity*255))); ty += max(1,f.getbbox(line)[3]-f.getbbox(line)[1])+gap
    output=Image.alpha_composite(base.convert("RGBA"),overlay).convert("RGB")
    meta.update({"background_color":",".join(map(str,bg)),"text_color":",".join(map(str,fg)),"rendered_contrast_ratio":cr,"edge_density":edge,"local_variance":var,"placement_region":name,"template_version":"camouflage_v3"})
    return output,meta


def generate(split: str, force: bool = False) -> None:
    manifest = pd.read_csv(V3_ROOT / "manifests" / "all_conditions.csv", dtype=str).fillna("")
    candidates = manifest[(manifest.split_name == split) & (manifest.visual_key != "")].drop_duplicates(["sample_id", "visual_key"])
    updates={}; errors=0
    for item_no, row in enumerate(candidates.itertuples(), start=1):
        out=resolve(row.condition_image_path); out.parent.mkdir(parents=True,exist_ok=True)
        try:
            if out.exists() and not force:
                # Existing output is only trusted if matching rows were already validated.
                current=manifest[(manifest.sample_id==row.sample_id)&(manifest.visual_key==row.visual_key)]
                if set(current.generation_status)=={"success"}: continue
            with Image.open(resolve(row.original_image_path)) as im: image=im.convert("RGB")
            ratio=float(CONFIG["font_size_ratios"][row.text_size]); opacity=float(CONFIG["default_opacity"])
            if row.visual_style=="camouflage": result,meta=_camouflage(image,row.payload_text,ratio,float(CONFIG["camouflage_opacity"]))
            else: result,meta=_fixed_text(image,row.payload_text,ratio,row.placement_region,opacity,row.visual_style)
            # WebP method changes encoder effort only; lossless pixels are identical.
            result.save(out,"WEBP",lossless=True,method=0); meta.update(generation_status="success",generation_error="")
        except Exception as exc: meta={"generation_status":"error","generation_error":f"{type(exc).__name__}: {exc}"}; errors+=1
        mask=(manifest.sample_id==row.sample_id)&(manifest.visual_key==row.visual_key)
        for key,value in meta.items(): manifest.loc[mask,key]=json.dumps(value) if isinstance(value,(list,dict)) else value
        updates[(row.sample_id,row.visual_key)]=meta
        if item_no % 50 == 0: write_manifest(manifest)
    write_manifest(manifest); print(f"generated split={split} unique_visuals={len(updates)} errors={errors}")


def split_validation(splits: dict[str, pd.DataFrame], clustered: pd.DataFrame, excluded: dict) -> None:
    rows=[]; failures=[]
    for name, frame in splits.items():
        rows.append({"split":name,"n":len(frame),"clusters":frame.duplicate_cluster_id.nunique(),**{x:int((frame.damage_label_normalized==x).sum()) for x in LABELS}})
    for a,left in splits.items():
        for b,right in splits.items():
            if a>=b: continue
            for col in ["sample_id","tweet_id","sha256","duplicate_cluster_id"]:
                overlap=set(left[col].dropna())&set(right[col].dropna())
                if overlap: failures.append({"split_a":a,"split_b":b,"field":col,"n":len(overlap)})
    report={"status":"passed" if not failures else "failed","near_duplicate_hamming":CONFIG["near_duplicate_hamming"],"splits":rows,"exclusions":excluded,"failures":failures}
    public=pd.concat([frame.assign(split_name=name) for name,frame in splits.items()],ignore_index=True)
    public[["split_name","sample_id","duplicate_cluster_id","event_name","damage_label_normalized","sha256","perceptual_hash"]].to_csv(V3_REPORT/"public_split_index.csv",index=False)
    (V3_REPORT/"split_validation.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    lines=["# V3 split validation","",f"Status: **{report['status']}**. Tweet, exact-image and near-image clusters are grouped before selection.","",f"Near-duplicate threshold: dHash Hamming distance <= {CONFIG['near_duplicate_hamming']}.","","| split | n | independent clusters | little/no | mild | severe |","|---|---:|---:|---:|---:|---:|"]
    for r in rows: lines.append(f"| {r['split']} | {r['n']} | {r['clusters']} | {r['little_or_no_damage']} | {r['mild_damage']} | {r['severe_damage']} |")
    lines += ["","## Exclusions","",f"Old prompt-pilot cluster rows: {excluded['old_pilot_cluster_rows']}; suspected mojibake rows: {excluded['mojibake_rows']}; short-side below {excluded['minimum_image_side_px']} px: {excluded['below_minimum_image_side_rows']}. No selected cluster crosses a split."]
    (V3_REPORT/"split_validation.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    if failures: raise RuntimeError(f"V3 split leakage: {failures[:3]}")


def build_review_package(manifest: pd.DataFrame) -> None:
    out=V3_REPORT/"manual_review"; out.mkdir(parents=True,exist_ok=True)
    fields=["reviewer_id","split_name","sample_id","condition","original_label_still_valid","text_readable","text_too_obvious","text_completely_invisible","critical_damage_obscured","layout_plausible","image_usable","approve","notes"]
    template=manifest[["split_name","sample_id","condition"]].copy()
    for col in fields:
        if col not in template: template[col]=""
    template[fields].to_csv(out/"review_template_all_splits.csv",index=False)
    for split,group in template.groupby("split_name"): group[fields].to_csv(out/f"review_template_{split}.csv",index=False)
    protocol="""# V3 human review protocol

Human labels must never be auto-filled. Use at least two independent reviewers who are blind to model predictions. Review the clean image first for label validity, then each attacked image for readability, visibility, obscuration, plausibility and usability. Keep `reviewer_id` pseudonymous.

Allowed categorical values are `yes`, `no`, and `uncertain`; `approve` is `yes` only when the original label remains valid, the image is usable, and the intervention matches its intended style. Resolve disagreements only after the independent pass. Report raw agreement and Cohen's kappa for two reviewers (or Krippendorff's alpha for more than two), plus adjudicated acceptance rates by split/style/size. Never report empty templates as completed human validation.
"""
    (out/"PROTOCOL.md").write_text(protocol,encoding="utf-8")


def build_visual_audit(manifest: pd.DataFrame) -> None:
    """Create a tweet-redacted, local visual QA page for a small stratified sample."""
    cards=[]
    descriptions={"pilot":"Teknik pilot","main":"Ana dengeli değerlendirme","style_ablation":"Stil karşılaştırması","size_ablation":"Yazı boyutu karşılaştırması"}
    for split in CONFIG["split_sizes_per_class"]:
        frame=manifest[manifest.split_name==split]; chosen=[]
        for label in LABELS:
            chosen.extend(frame[frame.ground_truth==label].sample_id.drop_duplicates().head(1).tolist())
        for sid in chosen:
            sample=frame[frame.sample_id==sid]; cells=[]
            for row in sample[(sample.condition=="clean") | (sample.visual_key!="")].itertuples():
                src="../../../"+str(row.condition_image_path)
                cells.append(f'<figure><img loading="lazy" src="{html.escape(src)}"><figcaption><b>{html.escape(row.condition)}</b><br><span>{html.escape(row.attack_semantics)} · {html.escape(row.visual_style)} · {html.escape(row.text_size)}</span></figcaption></figure>')
            cards.append(f'<article><header><div><span class="pill">{html.escape(split)}</span><h2>{html.escape(sid)}</h2></div><strong>{html.escape(str(sample.ground_truth.iloc[0]))}</strong></header><p>{descriptions[split]}. Kaynak tweet mahremiyet nedeniyle gösterilmez.</p><div class="rail">{"".join(cells)}</div></article>')
    page='''<!doctype html><html lang="tr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>V3 Görsel Veri Denetimi</title><style>
:root{color-scheme:dark;--bg:#0b1020;--panel:#131b2e;--line:#283650;--text:#edf3ff;--muted:#9aabc5;--accent:#75e0bd}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:14px/1.5 system-ui,sans-serif}main{max-width:1440px;margin:auto;padding:40px 24px}h1{font-size:clamp(28px,4vw,48px);margin:.2em 0}.lead{max-width:850px;color:var(--muted);font-size:17px}article{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:18px;margin:26px 0}header{display:flex;justify-content:space-between;gap:16px;align-items:start}h2{font-size:14px;overflow-wrap:anywhere}.pill{color:var(--accent);font-size:12px;text-transform:uppercase;letter-spacing:.08em}.rail{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}figure{margin:0;border:1px solid var(--line);border-radius:10px;overflow:hidden;background:#080c15}img{display:block;width:100%;height:170px;object-fit:contain}figcaption{padding:10px}figcaption span,article p{color:var(--muted)}code{color:var(--accent)}</style><main><span class="pill">CrisisMMD VLM Robustness · V3</span><h1>Görsel veri ve müdahale denetimi</h1><p class="lead">Bu sayfa model sonucu değil, düzeltilmiş veri üretiminin görsel kalite kontrolüdür. Her sınıftan bir örnek gösterilir. Image ve joint aynı saldırı görselini kullanır; text-only koşullar tweet metnini açığa çıkarmamak için burada gösterilmez. İnsan değerlendirmesi <code>PROTOCOL.md</code> ve boş CSV şablonlarıyla yapılmalıdır.</p>'''+"".join(cards)+"</main></html>"
    (V3_REPORT/"manual_review"/"visual_audit.html").write_text(page,encoding="utf-8")


def prepare() -> None:
    ensure_dirs(); raw=pd.read_csv(resolve("data/processed/all_valid_damage_samples.csv"),dtype=str).fillna("")
    clustered=build_duplicate_clusters(raw); old=pd.read_csv(resolve("data/splits/pilot.csv"),dtype=str).fillna("")
    old_clusters=set(clustered.loc[clustered.sample_id.isin(set(old.sample_id)),"duplicate_cluster_id"])
    blocked=clustered.duplicate_cluster_id.isin(old_clusters); bad=clustered.suspected_mojibake.astype(bool)
    too_small=(pd.to_numeric(clustered.image_width,errors="coerce")<int(CONFIG["minimum_image_side_px"])) | (pd.to_numeric(clustered.image_height,errors="coerce")<int(CONFIG["minimum_image_side_px"]))
    eligible=clustered[~blocked & ~bad & ~too_small].copy()
    splits=choose_splits(eligible)
    for name,frame in splits.items(): frame.to_csv(V3_ROOT/"splits"/f"{name}.csv",index=False)
    exclusions={"source_rows":len(clustered),"old_pilot_cluster_rows":int(blocked.sum()),"mojibake_rows":int((~blocked & bad).sum()),"below_minimum_image_side_rows":int((~blocked & ~bad & too_small).sum()),"minimum_image_side_px":int(CONFIG["minimum_image_side_px"]),"eligible_rows":len(eligible),"selected_rows":sum(map(len,splits.values()))}
    split_validation(splits,clustered,exclusions); manifest=build_manifest(splits); build_review_package(manifest); build_visual_audit(manifest)
    print(json.dumps({"splits":{k:len(v) for k,v in splits.items()},"exclusions":exclusions},indent=2))


def validate(allow_pending: bool=False) -> dict:
    m=pd.read_csv(V3_ROOT/"manifests"/"all_conditions.csv",dtype=str).fillna(""); failures=[]; warnings=[]
    if m.duplicated(["sample_id","condition"]).any(): failures.append({"check":"duplicate_sample_condition"})
    for split,npc in CONFIG["split_sizes_per_class"].items():
        expected=int(npc)*3*len(CONFIG["conditions"]["main" if split in {"pilot","main"} else split])
        actual=len(m[m.split_name==split])
        if actual!=expected: failures.append({"check":"manifest_count","split":split,"expected":expected,"actual":actual})
    for row in m.itertuples():
        if row.attack_modality in {"text","joint"} and row.condition_tweet != f"{row.payload_text}\n\n{row.original_tweet}": failures.append({"check":"tweet_preservation","sample_id":row.sample_id,"condition":row.condition})
        if row.visual_key:
            if row.generation_status=="pending" and allow_pending: continue
            if row.generation_status!="success" or not resolve(row.condition_image_path).exists(): failures.append({"check":"missing_visual","sample_id":row.sample_id,"condition":row.condition})
    # Image and joint must be byte-identical by construction (same path), and main semantic boxes must be area matched.
    for (split,sid,sem),g in m[(m.visual_key!="")].groupby(["split_name","sample_id","attack_semantics"]):
        if split in {"pilot","main"} and g.condition_image_path.nunique()!=1: failures.append({"check":"image_joint_path_mismatch","sample_id":sid,"semantics":sem})
    complete=m[m.generation_status=="success"].copy()
    for (split,sid,style,size),g in complete.groupby(["split_name","sample_id","visual_style","text_size"]):
        if g.attack_semantics.nunique()>1 and g.occupied_area_ratio.astype(float).max()-g.occupied_area_ratio.astype(float).min()>1e-9: failures.append({"check":"area_not_matched","sample_id":sid,"style":style,"size":size})
    for (sid,sem),g in complete[complete.split_name=="size_ablation"].groupby(["sample_id","attack_semantics"]):
        if g.placement_region.nunique()!=1: failures.append({"check":"size_placement_changed","sample_id":sid,"semantics":sem})
    cam=complete[complete.visual_style=="camouflage"]
    for row in cam.itertuples():
        cr=float(row.rendered_contrast_ratio)
        if not float(CONFIG["camouflage_contrast_min"]) <= cr <= float(CONFIG["camouflage_contrast_max"]): failures.append({"check":"camouflage_contrast","sample_id":row.sample_id,"condition":row.condition,"actual":cr})
    lengths={family:[len(v) for v in values.values()] for family,values in payloads().items()}; means={k:float(np.mean(v)) for k,v in lengths.items()}
    if max(means.values())/min(means.values())>1.10: failures.append({"check":"payload_length_means","means":means})
    result={"status":"passed" if not failures else "failed","records":len(m),"generated_records":len(complete),"failures":failures,"warnings":warnings,"payload_lengths":lengths,"payload_length_means":means}
    (V3_REPORT/"attack_validation.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    (V3_REPORT/"attack_validation.md").write_text(f"# V3 attack validation\n\nStatus: **{result['status']}**\n\nRecords: {len(m)}; generated condition records: {len(complete)}; failures: {len(failures)}.\n",encoding="utf-8")
    if failures: raise RuntimeError(f"V3 validation failed: {failures[:5]}")
    return result


def main() -> None:
    parser=argparse.ArgumentParser(); sub=parser.add_subparsers(dest="cmd",required=True); sub.add_parser("prepare")
    p=sub.add_parser("generate"); p.add_argument("--split",choices=list(CONFIG["split_sizes_per_class"]),required=True); p.add_argument("--force",action="store_true")
    p=sub.add_parser("validate"); p.add_argument("--allow-pending",action="store_true")
    args=parser.parse_args()
    if args.cmd=="prepare": prepare()
    elif args.cmd=="generate": generate(args.split,args.force)
    else: print(json.dumps(validate(args.allow_pending),indent=2))


if __name__ == "__main__": main()
