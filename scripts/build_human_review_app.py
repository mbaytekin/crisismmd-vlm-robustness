#!/usr/bin/env python3
"""Generate the blinded human visual-review app from the frozen 303-row instrument.

Scope is frozen: the 303 rows of reports/v3/manual_review/final_visual_review.csv.
Rating fields follow the predeclared gates in docs/HUMAN_EVALUATION.md section 5,
which the 303-row header did not yet carry. No ratings exist, so fixing the field
list now is legitimate; it must not change once any reviewer has started.

The app is deliberately local and offline. It never shows a model prediction,
a tweet, or the ground-truth severity label.

Usage:
    python scripts/build_human_review_app.py
    open reports/v3/manual_review/review_app.html
"""

import csv
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "reports" / "v3" / "manual_review" / "final_visual_review.csv"
OUT = REPO / "reports" / "v3" / "manual_review" / "review_app.html"

# Predeclared rating fields. `applies_to_clean` marks the two questions that are
# meaningful on an unmodified photograph; the overlay questions are not asked
# there and are exported as "na" rather than being auto-filled with a judgement.
FIELDS = [
    ("original_label_still_valid", "Does the scene still support a damage-severity judgement?", True),
    ("image_usable", "Is this still a usable damage photograph?", True),
    ("text_readable", "Is the overlay text legible?", False),
    ("text_too_obvious", "Is the overlay salient or banner-like?", False),
    ("text_completely_invisible", "Is there no usable text at all?", False),
    ("critical_damage_obscured", "Does the overlay cover decisive damage?", False),
    ("layout_plausible", "Could this pass as ordinary text-on-image social media?", False),
    ("approve", "Overall: is this stimulus valid?", True),
]

RULES = [
    "You are rating <strong>images only</strong>. You will not see any model prediction, any tweet text, or the ground-truth severity label. That is deliberate.",
    "Work <strong>independently</strong>. Do not discuss any image with the other reviewer, and do not compare files, until both of you have finished and exported.",
    "Every answer is <strong>yes</strong>, <strong>no</strong>, or <strong>uncertain</strong>. Use <em>uncertain</em> honestly; it is a real answer, not a failure. Never guess just to move on.",
    "Answer what you actually see. Do not try to be consistent with an earlier image, and do not go back to make your ratings look tidier.",
    "<strong>Approve</strong> is <em>yes</em> only when all three hold: the original damage judgement is still supportable, the image is still usable, and the intervention looks like the presentation it is meant to be.",
    "On unmodified photographs only two questions are asked, because there is no overlay to rate. The overlay questions are recorded as not-applicable, not as a rating.",
    "Your ratings are exported exactly as you enter them. They will not be adjusted, filtered, or replaced to fit any model result.",
    "Your image order is shuffled and differs from the other reviewer's. Progress is saved in this browser automatically; you can stop and resume.",
]

HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Blinded visual review</title>
<style>
  :root{
    --bg:#f6f7f9; --panel:#fff; --ink:#16191d; --muted:#5d646e; --line:#dfe3e8;
    --accent:#0b5fa5; --yes:#1a7f4b; --no:#b3401f; --unc:#8a6d1f; --shadow:0 1px 3px rgba(16,24,40,.07);
  }
  @media (prefers-color-scheme:dark){
    :root{ --bg:#14171b; --panel:#1c2026; --ink:#e9edf2; --muted:#9aa4b2; --line:#2c333c;
           --accent:#5aa9f0; --yes:#4ec27f; --no:#f08a63; --unc:#dcc06a; --shadow:none; }
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
       font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
  .wrap{max-width:1180px;margin:0 auto;padding:22px 20px 60px}
  h1{font-size:21px;margin:0 0 4px} h2{font-size:16px;margin:0 0 10px}
  .sub{color:var(--muted);font-size:13.5px;margin:0 0 20px}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:20px;box-shadow:var(--shadow)}
  ol.rules{margin:0;padding-left:20px} ol.rules li{margin:0 0 9px}
  label{display:block;font-weight:600;font-size:13px;margin:0 0 5px}
  input[type=text]{width:100%;max-width:340px;padding:9px 11px;font-size:14px;border:1px solid var(--line);
       border-radius:7px;background:var(--bg);color:var(--ink)}
  button{font:inherit;border:1px solid var(--line);background:var(--panel);color:var(--ink);
       padding:8px 15px;border-radius:7px;cursor:pointer}
  button:hover{border-color:var(--accent)}
  button.primary{background:var(--accent);color:#fff;border-color:var(--accent);font-weight:600}
  button.primary:disabled{opacity:.45;cursor:not-allowed}
  .bar{height:5px;background:var(--line);border-radius:3px;overflow:hidden;margin:14px 0 6px}
  .bar > i{display:block;height:100%;background:var(--accent);width:0}
  .grid{display:grid;grid-template-columns:minmax(0,1fr) 400px;gap:24px;align-items:start}
  @media (max-width:900px){ .grid{grid-template-columns:1fr} }
  .stage{background:#0d0f12;border:1px solid var(--line);border-radius:10px;display:flex;
       align-items:center;justify-content:center;min-height:430px;overflow:hidden}
  .stage img{max-width:100%;max-height:74vh;display:block}
  .q{border-bottom:1px solid var(--line);padding:11px 0}
  .q:last-of-type{border-bottom:none}
  .q.active{background:color-mix(in srgb,var(--accent) 8%,transparent);
       margin:0 -10px;padding-left:10px;padding-right:10px;border-radius:7px}
  .q p{margin:0 0 7px;font-size:13.5px}
  .opts{display:flex;gap:7px}
  .opts button{flex:1;padding:7px 0;font-size:13px}
  .opts button.sel[data-v=yes]{background:var(--yes);border-color:var(--yes);color:#fff;font-weight:600}
  .opts button.sel[data-v=no]{background:var(--no);border-color:var(--no);color:#fff;font-weight:600}
  .opts button.sel[data-v=uncertain]{background:var(--unc);border-color:var(--unc);color:#fff;font-weight:600}
  .na{color:var(--muted);font-size:12.5px;font-style:italic}
  .meta{color:var(--muted);font-size:12.5px;display:flex;justify-content:space-between;margin-bottom:8px}
  .foot{display:flex;gap:10px;align-items:center;margin-top:16px;flex-wrap:wrap}
  textarea{width:100%;min-height:48px;padding:8px;border:1px solid var(--line);border-radius:7px;
       background:var(--bg);color:var(--ink);font:inherit;font-size:13px;resize:vertical}
  .kbd{font:12px ui-monospace,SFMono-Regular,Menlo,monospace;background:var(--bg);
       border:1px solid var(--line);border-radius:4px;padding:1px 5px}
  .warn{background:color-mix(in srgb,var(--unc) 14%,transparent);border:1px solid var(--unc);
       border-radius:8px;padding:11px 13px;font-size:13px;margin:16px 0}
  .done{text-align:center;padding:36px 20px}
  [hidden]{display:none!important}
</style>
</head>
<body>
<div class="wrap">

<section id="gate">
  <h1>Blinded visual review</h1>
  <p class="sub">303 images &middot; frozen instrument &middot; independent pass</p>
  <div class="card">
    <h2>Read this before you start</h2>
    <ol class="rules">__RULES__</ol>
    <div class="warn">
      Once you begin, the image list and the questions are fixed. If something looks wrong with the
      instrument itself, stop and report it rather than working around it.
    </div>
    <label for="rid">Your reviewer ID (a pseudonym, not your name)</label>
    <input type="text" id="rid" placeholder="e.g. rater-a" autocomplete="off">
    <div class="foot">
      <button class="primary" id="start" disabled>I have read the rules &mdash; start</button>
      <span class="na" id="resume"></span>
    </div>
  </div>
</section>

<section id="app" hidden>
  <div class="meta">
    <span><strong id="pos"></strong> &middot; reviewer <span id="who"></span></span>
    <span id="grp"></span>
  </div>
  <div class="bar"><i id="fill"></i></div>
  <div class="grid">
    <div class="stage"><img id="shot" alt="image under review"></div>
    <div class="card">
      <div id="qs"></div>
      <div class="q">
        <p>Notes (optional)</p>
        <textarea id="notes" placeholder="Anything unusual about this image"></textarea>
      </div>
      <div class="foot">
        <button id="prev">&larr; Back</button>
        <button class="primary" id="next" disabled>Next &rarr;</button>
      </div>
      <p class="na" style="margin-top:12px">
        Keys: <span class="kbd">y</span> yes &middot; <span class="kbd">n</span> no &middot;
        <span class="kbd">u</span> uncertain &middot; <span class="kbd">&larr;</span>
        <span class="kbd">&rarr;</span> move between images
      </p>
    </div>
  </div>
  <div class="foot"><button id="export">Export my ratings (CSV)</button><span class="na" id="exportnote"></span></div>
</section>

<section id="finished" hidden>
  <div class="card done">
    <h2>All 303 images rated</h2>
    <p class="sub">Export your file and send it to the coordinator. Do not compare it with the other
      reviewer's file &mdash; agreement is computed from the two independent passes.</p>
    <button class="primary" id="export2">Export my ratings (CSV)</button>
    <div class="foot" style="justify-content:center"><button id="reopen">Review my answers again</button></div>
  </div>
</section>

</div>
<script>
const ROWS = __ROWS__;
const FIELDS = __FIELDS__;
const VALUES = ["yes","no","uncertain"];

let rid = "", order = [], idx = 0, ans = {}, activeField = 0;

const $ = s => document.querySelector(s);
const keyOf = r => r.sample_id + "|" + r.condition;

// Deterministic per-reviewer shuffle: same ID always reproduces the same order,
// different IDs decouple fatigue effects between the two raters.
function seeded(id){
  let h = 2166136261 >>> 0;
  for (const ch of id){ h ^= ch.charCodeAt(0); h = Math.imul(h, 16777619) >>> 0; }
  return () => { h ^= h << 13; h >>>= 0; h ^= h >> 17; h ^= h << 5; h >>>= 0; return h / 4294967296; };
}
function shuffle(n, rnd){
  const a = [...Array(n).keys()];
  for (let i = a.length - 1; i > 0; i--){ const j = Math.floor(rnd() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
  return a;
}

const store = () => "hvr:" + rid;
function save(){ try{ localStorage.setItem(store(), JSON.stringify({idx, ans})); }catch(e){} }
function load(){
  try{
    const raw = localStorage.getItem(store());
    if (raw){ const d = JSON.parse(raw); ans = d.ans || {}; idx = d.idx || 0; return true; }
  }catch(e){}
  return false;
}

function fieldsFor(row){
  const clean = row.condition === "clean";
  return FIELDS.filter(f => !clean || f.clean);
}
function complete(row){
  const rec = ans[keyOf(row)] || {};
  return fieldsFor(row).every(f => VALUES.includes(rec[f.name]));
}
function ratedCount(){ return ROWS.filter(complete).length; }

function render(){
  const row = ROWS[order[idx]];
  const rec = ans[keyOf(row)] || (ans[keyOf(row)] = {});
  const fs = fieldsFor(row);
  if (activeField >= fs.length) activeField = fs.length - 1;

  $("#pos").textContent = "Image " + (idx + 1) + " of " + ROWS.length;
  $("#who").textContent = rid;
  $("#grp").textContent = ratedCount() + " rated";
  $("#fill").style.width = (100 * ratedCount() / ROWS.length) + "%";
  $("#shot").src = row.src;

  $("#qs").innerHTML = fs.map((f, i) =>
    '<div class="q' + (i === activeField ? ' active' : '') + '"><p>' + f.label + '</p><div class="opts">' +
    VALUES.map(v => '<button data-f="' + f.name + '" data-v="' + v + '"' +
      (rec[f.name] === v ? ' class="sel"' : '') + '>' + v + '</button>').join("") +
    '</div></div>').join("") +
    (row.condition === "clean"
      ? '<p class="na">Unmodified photograph &mdash; the overlay questions do not apply and are recorded as not-applicable.</p>'
      : "");

  $("#qs").querySelectorAll("button").forEach(b => b.onclick = () => {
    pick(b.dataset.f, b.dataset.v);
  });
  $("#notes").value = rec.notes || "";
  $("#next").disabled = !complete(row);
  $("#prev").disabled = idx === 0;
}

function pick(name, val){
  const row = ROWS[order[idx]];
  ans[keyOf(row)][name] = val;
  const fs = fieldsFor(row);
  const at = fs.findIndex(f => f.name === name);
  const nextUnset = fs.findIndex((f, i) => i > at && !VALUES.includes(ans[keyOf(row)][f.name]));
  activeField = nextUnset >= 0 ? nextUnset : Math.min(at + 1, fs.length - 1);
  save(); render();
}

function go(step){
  const row = ROWS[order[idx]];
  ans[keyOf(row)].notes = $("#notes").value;
  const n = idx + step;
  if (n < 0 || n >= ROWS.length) return;
  idx = n; activeField = 0; save(); render();
  if (ratedCount() === ROWS.length) finish();
}

function finish(){
  $("#app").hidden = true; $("#finished").hidden = false;
}

function toCSV(){
  const head = ["reviewer_id","review_group","sample_id","event_name","condition","condition_image_path"]
    .concat(FIELDS.map(f => f.name)).concat(["notes"]);
  const esc = s => '"' + String(s == null ? "" : s).replace(/"/g, '""') + '"';
  const lines = [head.join(",")];
  for (const r of ROWS){
    const rec = ans[keyOf(r)] || {};
    const clean = r.condition === "clean";
    const cells = [rid, r.review_group, r.sample_id, r.event_name, r.condition, r.path]
      .concat(FIELDS.map(f => (!clean || f.clean) ? (rec[f.name] || "") : "na"))
      .concat([rec.notes || ""]);
    lines.push(cells.map(esc).join(","));
  }
  return lines.join("\n");
}

function download(){
  const missing = ROWS.length - ratedCount();
  if (missing > 0 && !confirm(missing + " image(s) are still unrated. Export the partial file anyway?")) return;
  const blob = new Blob([toCSV()], {type:"text/csv"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "human_review__" + rid.replace(/[^a-z0-9_-]/gi, "") + ".csv";
  document.body.appendChild(a); a.click(); a.remove();
  $("#exportnote").textContent = "Exported " + ratedCount() + "/" + ROWS.length + " ratings.";
}

$("#rid").addEventListener("input", e => {
  const v = e.target.value.trim();
  $("#start").disabled = v.length < 2;
  let has = false;
  try{ has = !!localStorage.getItem("hvr:" + v); }catch(e){}
  $("#resume").textContent = has ? "Saved progress found for this ID — it will be resumed." : "";
});

$("#start").onclick = () => {
  rid = $("#rid").value.trim();
  order = shuffle(ROWS.length, seeded(rid));
  load();
  $("#gate").hidden = true; $("#app").hidden = false;
  activeField = 0; render();
};
$("#next").onclick = () => go(1);
$("#prev").onclick = () => go(-1);
$("#export").onclick = download;
$("#export2").onclick = download;
$("#reopen").onclick = () => { $("#finished").hidden = true; $("#app").hidden = false; idx = 0; render(); };

document.addEventListener("keydown", e => {
  if ($("#app").hidden) return;
  if (e.target.tagName === "TEXTAREA" || e.target.tagName === "INPUT") return;
  const row = ROWS[order[idx]], fs = fieldsFor(row);
  const k = e.key.toLowerCase();
  if (k === "y" || k === "n" || k === "u"){
    e.preventDefault();
    pick(fs[activeField].name, k === "y" ? "yes" : k === "n" ? "no" : "uncertain");
  } else if (e.key === "ArrowRight"){ e.preventDefault(); if (!$("#next").disabled) go(1); }
  else if (e.key === "ArrowLeft"){ e.preventDefault(); go(-1); }
  else if (e.key === "ArrowDown"){ e.preventDefault(); activeField = Math.min(activeField + 1, fs.length - 1); render(); }
  else if (e.key === "ArrowUp"){ e.preventDefault(); activeField = Math.max(activeField - 1, 0); render(); }
});
</script>
</body>
</html>
"""


def main() -> None:
    rows = list(csv.DictReader(SRC.open()))
    if len(rows) != 303:
        raise SystemExit(f"expected the frozen 303-row instrument, found {len(rows)}")

    out_dir = OUT.parent
    payload = []
    for r in rows:
        path = r["condition_image_path"]
        abs_path = REPO / path
        if not abs_path.exists():
            raise SystemExit(f"missing image: {path}")
        # The ground-truth severity label is deliberately not carried into the app.
        payload.append(
            {
                "review_group": r["review_group"],
                "sample_id": r["sample_id"],
                "event_name": r["event_name"],
                "condition": r["condition"],
                "path": path,
                "src": __import__("os").path.relpath(abs_path, out_dir),
            }
        )

    fields = [{"name": n, "label": q, "clean": c} for n, q, c in FIELDS]
    html = (
        HTML.replace("__ROWS__", json.dumps(payload))
        .replace("__FIELDS__", json.dumps(fields))
        .replace("__RULES__", "".join(f"<li>{r}</li>" for r in RULES))
    )
    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT}  ({len(payload)} images, {len(FIELDS)} rating fields)")
    print("open it with:  open " + str(OUT))


if __name__ == "__main__":
    main()
