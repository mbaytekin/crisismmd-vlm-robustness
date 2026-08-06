(() => {
  const cards = [...document.querySelectorAll("article")];
  if (!cards.length) return;

  const css = `
    :root {
      --bg: oklch(0.965 0.012 240);
      --surface: oklch(0.995 0.004 240);
      --surface-muted: oklch(0.945 0.018 240);
      --ink: oklch(0.24 0.035 240);
      --muted: oklch(0.49 0.035 240);
      --line: oklch(0.86 0.025 240);
      --accent: oklch(0.52 0.13 205);
      --accent-soft: oklch(0.93 0.045 205);
      --success: oklch(0.48 0.12 155);
      --success-soft: oklch(0.93 0.045 155);
      --warning: oklch(0.55 0.14 75);
      --warning-soft: oklch(0.95 0.06 85);
      --danger: oklch(0.52 0.16 25);
      --danger-soft: oklch(0.95 0.045 25);
      --shadow: 0 12px 30px oklch(0.22 0.03 240 / 0.08);
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font: 14px/1.55 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    button, input, select { font: inherit; }
    button, select, input { border-radius: 9px; }
    .audit-app { min-height: 100vh; }
    .audit-topbar {
      position: sticky;
      top: 0;
      z-index: 10;
      background: oklch(0.985 0.008 240 / 0.94);
      border-bottom: 1px solid var(--line);
      backdrop-filter: blur(12px);
    }
    .audit-topbar-inner, .audit-container { width: min(1420px, calc(100% - 40px)); margin: 0 auto; }
    .audit-topbar-inner { min-height: 58px; display: flex; align-items: center; justify-content: space-between; gap: 20px; }
    .brand { display: flex; align-items: center; gap: 10px; color: var(--ink); text-decoration: none; font-weight: 750; letter-spacing: -0.015em; }
    .brand-mark { width: 28px; height: 28px; display: grid; place-items: center; border-radius: 8px; background: var(--accent); color: white; font-size: 15px; }
    .topbar-note { color: var(--muted); font-size: 12px; }
    .audit-container { padding: 42px 0 72px; }
    .hero { display: grid; grid-template-columns: minmax(0, 1.2fr) minmax(320px, .8fr); gap: 28px; align-items: stretch; margin-bottom: 24px; }
    .hero-copy, .method-panel, .legend-panel, .controls-panel { background: var(--surface); border: 1px solid var(--line); border-radius: 16px; box-shadow: var(--shadow); }
    .hero-copy { padding: clamp(24px, 4vw, 48px); }
    .kicker { color: var(--accent); font-size: 12px; font-weight: 750; letter-spacing: .08em; text-transform: uppercase; margin: 0 0 12px; }
    .hero h1 { font-size: clamp(28px, 4vw, 46px); line-height: 1.05; letter-spacing: -0.04em; text-wrap: balance; margin: 0 0 16px; }
    .hero-lede { max-width: 68ch; color: var(--muted); font-size: 16px; margin: 0; }
    .method-panel { padding: 24px; background: oklch(0.30 0.04 240); color: oklch(0.97 0.01 240); border-color: oklch(0.38 0.05 240); }
    .method-panel h2 { margin: 0 0 12px; font-size: 18px; letter-spacing: -0.015em; }
    .method-panel p { color: oklch(0.86 0.025 240); margin: 0 0 15px; }
    .method-panel ol { margin: 0; padding-left: 20px; color: oklch(0.91 0.02 240); }
    .method-panel li + li { margin-top: 7px; }
    .summary-strip { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; margin: 0 0 24px; }
    .summary-item { padding: 15px 16px; background: var(--surface); border: 1px solid var(--line); border-radius: 12px; }
    .summary-item strong { display: block; font-size: 25px; line-height: 1; letter-spacing: -0.03em; }
    .summary-item span { display: block; margin-top: 6px; color: var(--muted); font-size: 12px; }
    .summary-item.success strong { color: var(--success); }
    .summary-item.warning strong { color: var(--warning); }
    .summary-item.accent strong { color: var(--accent); }
    .legend-panel { padding: 18px 20px; margin-bottom: 18px; }
    .legend-panel h2 { margin: 0 0 10px; font-size: 16px; }
    .legend-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; }
    .legend-item { display: flex; gap: 9px; align-items: flex-start; color: var(--muted); font-size: 12px; }
    .legend-item strong { display: block; color: var(--ink); font-size: 13px; }
    .legend-dot { flex: 0 0 9px; width: 9px; height: 9px; border-radius: 50%; margin-top: 5px; background: var(--accent); }
    .legend-dot.benign { background: var(--success); }
    .legend-dot.direct { background: var(--danger); }
    .legend-dot.misleading { background: var(--warning); }
    .controls-panel { position: sticky; top: 74px; z-index: 5; padding: 14px; margin-bottom: 22px; box-shadow: 0 8px 20px oklch(0.22 0.03 240 / 0.06); }
    .controls { display: grid; grid-template-columns: minmax(220px, 1.4fr) repeat(3, minmax(140px, .65fr)) auto; gap: 9px; align-items: center; }
    .control { width: 100%; min-height: 40px; padding: 9px 11px; border: 1px solid var(--line); background: var(--surface); color: var(--ink); outline: none; }
    .control:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }
    .reset { min-height: 40px; padding: 9px 13px; border: 1px solid var(--line); background: var(--surface-muted); color: var(--ink); cursor: pointer; font-weight: 650; }
    .reset:hover { border-color: var(--accent); color: var(--accent); }
    .gallery-heading { display: flex; justify-content: space-between; align-items: baseline; gap: 16px; margin: 0 0 12px; }
    .gallery-heading h2 { margin: 0; font-size: 21px; letter-spacing: -0.025em; }
    .gallery-count { color: var(--muted); font-size: 13px; }
    .gallery { display: grid; gap: 16px; }
    .audit-card { background: var(--surface); border: 1px solid var(--line); border-radius: 16px; padding: 22px; margin: 0; box-shadow: 0 6px 18px oklch(0.22 0.03 240 / 0.045); scroll-margin-top: 145px; }
    .audit-card[hidden] { display: none; }
    .card-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; padding-bottom: 14px; border-bottom: 1px solid var(--line); }
    .card-title { margin: 0; font-size: 18px; line-height: 1.2; letter-spacing: -0.02em; }
    .card-context { margin: 4px 0 0; color: var(--muted); font-size: 12px; }
    .badge { display: inline-flex; align-items: center; gap: 5px; flex: 0 0 auto; padding: 5px 9px; border-radius: 999px; background: var(--accent-soft); color: var(--accent); font-size: 11px; font-weight: 750; }
    .badge.benign { background: var(--success-soft); color: var(--success); }
    .badge.direct, .badge.misleading { background: var(--danger-soft); color: var(--danger); }
    .badge.warning { background: var(--warning-soft); color: oklch(0.39 0.10 70); }
    .card-explainer { margin: 15px 0; padding: 12px 14px; border-radius: 10px; background: var(--surface-muted); color: var(--muted); font-size: 13px; }
    .card-explainer strong { color: var(--ink); }
    .fact-grid { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 9px; margin: 0 0 18px; }
    .fact { padding: 10px 11px; border: 1px solid var(--line); border-radius: 9px; min-width: 0; }
    .fact dt { color: var(--muted); font-size: 10px; margin-bottom: 3px; }
    .fact dd { margin: 0; color: var(--ink); font-size: 12px; font-weight: 650; overflow-wrap: anywhere; }
    .model-comparison { margin: 18px 0 0; padding: 16px; background: oklch(0.975 0.012 215); border: 1px solid oklch(0.84 0.045 215); border-radius: 13px; }
    .model-comparison-head { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; margin-bottom: 12px; }
    .model-comparison-head h4 { margin: 0; color: var(--ink); font-size: 14px; letter-spacing: -0.01em; }
    .model-comparison-head p { margin: 0; color: var(--muted); font-size: 11px; }
    .model-output-grid { display: grid; grid-template-columns: minmax(0, 1fr) 130px minmax(0, 1fr); gap: 10px; align-items: stretch; }
    .model-output, .model-delta { min-width: 0; padding: 13px; border: 1px solid var(--line); border-radius: 10px; background: var(--surface); }
    .model-output.clean { border-color: oklch(0.78 0.08 155); background: oklch(0.97 0.025 155); }
    .model-output.condition { border-color: oklch(0.78 0.07 205); background: oklch(0.97 0.025 205); }
    .model-output-label { display: block; color: var(--muted); font-size: 11px; font-weight: 750; }
    .model-output strong { display: block; margin-top: 5px; color: var(--ink); font: 750 16px/1.2 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; overflow-wrap: anywhere; }
    .confidence { display: inline-block; margin-top: 6px; padding: 3px 7px; border-radius: 999px; background: var(--surface-muted); color: var(--ink); font-size: 11px; font-weight: 700; }
    .rationale { margin: 10px 0 0; color: var(--muted); font-size: 12px; line-height: 1.45; }
    .rationale-label { display: block; margin-bottom: 3px; color: var(--ink); font-size: 11px; font-weight: 700; }
    .model-delta { display: flex; flex-direction: column; justify-content: center; gap: 8px; text-align: center; background: var(--surface); }
    .delta-item { color: var(--muted); font-size: 11px; }
    .delta-item strong { display: block; margin-top: 2px; color: var(--ink); font-size: 13px; }
    .delta-item.changed strong { color: var(--danger); }
    .delta-item.stable strong { color: var(--success); }
    .comparison-note { margin: 11px 0 0; color: var(--muted); font-size: 11px; }
    .imgs { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; margin: 0; }
    .imgs figure { max-width: none; min-width: 0; margin: 0; padding: 10px; background: oklch(0.965 0.012 240); border: 1px solid var(--line); border-radius: 12px; }
    .imgs img { width: 100%; max-width: none; height: 300px; max-height: none; object-fit: contain; background: oklch(0.17 0.02 240); border: 0; border-radius: 7px; display: block; }
    .imgs figcaption { margin: 0 0 7px; color: var(--ink); font-size: 12px; font-weight: 750; }
    .imgs code { display: block; margin-top: 8px; color: var(--muted); font: 10px/1.35 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; overflow-wrap: anywhere; }
    .tweets { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; margin-top: 14px; }
    .tweets section { min-width: 0; }
    .tweets b { display: block; margin-bottom: 6px; font-size: 12px; }
    .tweets pre { min-height: 76px; max-height: 180px; overflow: auto; white-space: pre-wrap; word-break: break-word; margin: 0; padding: 12px; background: var(--surface-muted); border: 1px solid var(--line); border-radius: 9px; color: var(--ink); font: 12px/1.5 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
    .empty { padding: 36px; text-align: center; color: var(--muted); background: var(--surface); border: 1px dashed var(--line); border-radius: 14px; }
    .audit-footer { margin-top: 26px; color: var(--muted); font-size: 12px; }
    .audit-footer a { color: var(--accent); }
    @media (max-width: 1050px) { .controls { grid-template-columns: 1fr 1fr 1fr; } .controls .search { grid-column: 1 / -1; } .fact-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
    @media (max-width: 800px) { .audit-topbar-inner, .audit-container { width: min(100% - 24px, 680px); } .hero { grid-template-columns: 1fr; } .summary-strip, .legend-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .controls { grid-template-columns: 1fr 1fr; } .controls .search { grid-column: 1 / -1; } .imgs, .tweets, .model-output-grid { grid-template-columns: 1fr; } .imgs img { height: auto; max-height: 360px; } .card-head, .model-comparison-head { flex-direction: column; } .model-delta { text-align: left; } }
    @media (max-width: 500px) { .summary-strip, .legend-grid, .controls, .fact-grid { grid-template-columns: 1fr; } .controls .search { grid-column: auto; } .hero-copy { padding: 24px; } .audit-card { padding: 16px; } .topbar-note { display: none; } }
    @media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } *, *::before, *::after { transition-duration: 0.01ms !important; animation-duration: 0.01ms !important; } }
  `;
  const style = document.createElement("style");
  style.textContent = css;
  document.head.append(style);

  const fieldMap = (paragraph) => {
    const values = {};
    paragraph.querySelectorAll("b").forEach((label) => {
      let value = "";
      for (let node = label.nextSibling; node && node.nodeName !== "BR" && node.nodeName !== "B"; node = node.nextSibling) value += node.textContent;
      values[label.textContent.replace(/:$/, "").trim()] = value.replace(/\u00a0/g, " ").trim();
    });
    return values;
  };
  const conditionLabels = {
    clean: "Temiz referans",
    benign_image: "Benign · görsel",
    benign_text: "Benign · metin",
    benign_joint: "Benign · birleşik",
    direct_image: "Doğrudan · görsel",
    direct_text: "Doğrudan · metin",
    direct_joint: "Doğrudan · birleşik",
    benign_simple: "Benign · simple",
    benign_news: "Benign · news",
    benign_camouflage: "Benign · camouflage",
    direct_simple: "Doğrudan · simple",
    direct_news: "Doğrudan · news",
    direct_camouflage: "Doğrudan · camouflage",
    misleading_simple: "Yanıltıcı · simple",
    misleading_news: "Yanıltıcı · news",
    misleading_camouflage: "Yanıltıcı · camouflage",
    benign_small: "Benign · küçük",
    benign_medium: "Benign · orta",
    benign_large: "Benign · büyük",
    direct_small: "Doğrudan · küçük",
    direct_medium: "Doğrudan · orta",
    direct_large: "Doğrudan · büyük",
    misleading_small: "Yanıltıcı · küçük",
    misleading_medium: "Yanıltıcı · orta",
    misleading_large: "Yanıltıcı · büyük"
  };
  const splitLabels = { pilot: "pilot", main: "ana deney", style_ablation: "stil ablation", size_ablation: "boyut ablation" };
  const explain = (condition) => {
    if (condition === "clean") return "Hiçbir değişiklik uygulanmadı; tüm karşılaştırmaların temiz referansıdır.";
    if (condition.startsWith("benign")) return "Nötr payload veya görsel biçimlendirme uygulanır. Bu koşul bir adversarial başarı ölçümü değil, müdahalenin doğal karar değişimini ölçen kontrol grubudur.";
    if (condition.startsWith("direct")) return "Payload, modeli hedeflenen yanlış hasar sınıfına doğrudan yönlendirmeyi amaçlar.";
    if (condition.startsWith("misleading")) return "Payload, haber/olay bağlamı gibi görünen yanıltıcı bir ifade ile modelin hasar değerlendirmesini değiştirmeyi amaçlar.";
    return "Bu kart, bağımsız audit sırasında otomatik olarak seçilmiş bir inceleme örneğidir.";
  };
  const escapeHtml = (value) => String(value ?? "").replace(/[&<>\"']/g, (character) => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[character]));
  const severityLevel = { little_or_no_damage: 0, mild_damage: 1, severe_damage: 2 };
  const modelResult = (split, sample, condition) => window.AUDIT_MODEL_RESULTS?.[`${split}::${sample}::${condition}`] || null;

  const app = document.createElement("div");
  app.className = "audit-app";
  app.innerHTML = `
    <header class="audit-topbar"><div class="audit-topbar-inner">
      <a class="brand" href="#top"><span class="brand-mark">✓</span><span>CrisisMMD · Audit Gallery</span></a>
      <span class="topbar-note">V2 · Seed 42 · bağımsız, salt-okunur denetim</span>
    </div></header>
    <main id="top" class="audit-container">
      <section class="hero" aria-labelledby="page-title">
        <div class="hero-copy">
          <p class="kicker">Araştırma inceleme yüzeyi</p>
          <h1 id="page-title">Adversarial görsel veri seti denetimi</h1>
          <p class="hero-lede">Bu sayfa, CrisisMMD V2 üzerinde üretilen temiz, benign, doğrudan ve yanıltıcı koşullardan seçilmiş örnekleri yan yana gösterir. Amaç, saldırıların gerçekten uygulandığını, metnin doğru yerde bulunduğunu ve sonuçların güvenilir biçimde yorumlanabileceğini hızlıca kontrol etmektir.</p>
        </div>
        <aside class="method-panel" aria-labelledby="method-title">
          <h2 id="method-title">Yöntem nasıl çalışıyor?</h2>
          <p>Audit, yeni veri üretmeden ve mevcut dosyaları değiştirmeden manifest ile görselleri karşılaştırır.</p>
          <ol><li>Temiz görüntü ve koşullu görüntü eşleştirilir.</li><li>Manifestteki payload, stil, boyut, yerleşim ve metin kutusu doğrulanır.</li><li>Dosya okunabilirliği, bbox, metin korunumu, kontrast ve yasaklı logo kontrolleri uygulanır.</li><li>Otomatik uyarı görülen örnekler insan incelemesine ayrılır.</li></ol>
        </aside>
      </section>
      <section class="summary-strip" aria-label="Audit özeti">
        <div class="summary-item success"><strong>0</strong><span>kritik / yüksek sorun</span></div>
        <div class="summary-item warning"><strong>859</strong><span>orta seviye uyarı</span></div>
        <div class="summary-item accent"><strong>4</strong><span>incelenen split</span></div>
        <div class="summary-item"><strong id="card-total">—</strong><span>galerideki temsilî kart</span></div>
      </section>
      <section class="legend-panel" aria-labelledby="legend-title">
        <h2 id="legend-title">Koşulları nasıl okumalı?</h2>
        <div class="legend-grid">
          <div class="legend-item"><i class="legend-dot"></i><div><strong>clean</strong>Değişiklik yok; referans koşulu.</div></div>
          <div class="legend-item"><i class="legend-dot benign"></i><div><strong>benign_*</strong>Nötr kontrol müdahalesi; saldırı başarısı olarak yorumlanmaz.</div></div>
          <div class="legend-item"><i class="legend-dot direct"></i><div><strong>direct_*</strong>Modeli hedef sınıfa doğrudan yönlendirmeyi dener.</div></div>
          <div class="legend-item"><i class="legend-dot misleading"></i><div><strong>misleading_*</strong>Yanıltıcı bağlamla model kararını değiştirmeyi dener.</div></div>
        </div>
      </section>
      <section class="controls-panel" aria-label="Galeri filtreleri"><div class="controls">
        <input class="control search" id="search" type="search" placeholder="Örnek, payload veya koşul ara…" aria-label="Galeride ara">
        <select class="control" id="split-filter" aria-label="Split filtresi"><option value="all">Tüm splitler</option><option value="pilot">Pilot</option><option value="main">Ana deney</option><option value="style_ablation">Stil ablation</option><option value="size_ablation">Boyut ablation</option></select>
        <select class="control" id="type-filter" aria-label="Koşul türü"><option value="all">Tüm koşullar</option><option value="clean">Clean</option><option value="benign">Benign</option><option value="direct">Direct</option><option value="misleading">Misleading</option></select>
        <select class="control" id="status-filter" aria-label="Audit sonucu"><option value="all">Tüm sonuçlar</option><option value="pass">PASS</option><option value="warning">Uyarı / inceleme</option></select>
        <button class="reset" id="reset" type="button">Filtreleri temizle</button>
      </div></section>
      <div class="gallery-heading"><h2>Görsel galeri</h2><span class="gallery-count" id="gallery-count" aria-live="polite"></span></div>
      <section class="gallery" id="gallery" aria-label="Audit örnekleri"></section>
      <p class="audit-footer">Otomatik “PASS”, örneğin makine kontrollerinden geçtiğini gösterir; insanın görsel okunabilirlik ve gerçekçilik değerlendirmesinin yerine geçmez. Ayrıntılı sorun listesi: <a href="audit_issues.csv">audit_issues.csv</a> · özet: <a href="audit_summary.md">audit_summary.md</a></p>
    </main>`;
  document.body.replaceChildren(app);

  const gallery = app.querySelector("#gallery");
  const transformed = cards.map((card) => {
    const oldTitle = card.querySelector("h2");
    const oldParagraph = card.querySelector("p");
    const fields = oldParagraph ? fieldMap(oldParagraph) : {};
    const splitCondition = (fields["split/condition"] || "").split("/").map((x) => x.trim());
    const split = splitCondition[0] || (oldTitle.textContent.split(":")[0] || "unknown").trim();
    const condition = splitCondition[1] || "unknown";
    const kind = condition === "clean" ? "clean" : condition.startsWith("benign") ? "benign" : condition.startsWith("direct") ? "direct" : condition.startsWith("misleading") ? "misleading" : "other";
    const result = fields["automatic result"] || "";
    const status = result.startsWith("PASS") ? "pass" : "warning";
    const sample = fields.sample || "";
    const title = document.createElement("div");
    title.className = "card-head";
    title.innerHTML = `<div><h3 class="card-title">${escapeHtml(split)} · ${escapeHtml(condition)}</h3><p class="card-context">${escapeHtml(sample)}</p></div><span class="badge ${kind} ${status === "warning" ? "warning" : ""}">${status === "pass" ? "PASS · otomatik" : "UYARI · inceleme"}</span>`;
    const note = document.createElement("div");
    note.className = "card-explainer";
    note.innerHTML = `<strong>Bu koşul:</strong> ${explain(condition)}`;
    const facts = document.createElement("dl");
    facts.className = "fact-grid";
    const factValues = [
      ["Split / koşul", `${split} / ${condition}`],
      ["Gerçek etiket", fields.GT || "—"],
      ["Payload", fields.payload || "—"],
      ["Stil · boyut · yer", fields["style/size/place"] || "—"],
      ["Kontrast · opacity", fields["contrast/opacity"] || "—"],
      ["Otomatik sonuç", result || "—"]
    ];
    factValues.forEach(([label, value]) => {
      const item = document.createElement("div"); item.className = "fact";
      item.innerHTML = `<dt>${escapeHtml(label)}</dt><dd>${escapeHtml(value)}</dd>`; facts.append(item);
    });
    const cleanOutput = modelResult(split, sample, "clean");
    const conditionOutput = modelResult(split, sample, condition);
    const sameLabel = cleanOutput && conditionOutput && cleanOutput.label === conditionOutput.label;
    const cleanSeverity = cleanOutput ? severityLevel[cleanOutput.label] : undefined;
    const conditionSeverity = conditionOutput ? severityLevel[conditionOutput.label] : undefined;
    const severityDrop = Number.isFinite(cleanSeverity) && Number.isFinite(conditionSeverity) ? cleanSeverity - conditionSeverity : null;
    const confidenceDelta = cleanOutput && conditionOutput && Number.isFinite(cleanOutput.confidence) && Number.isFinite(conditionOutput.confidence) ? (conditionOutput.confidence - cleanOutput.confidence) * 100 : null;
    const comparison = document.createElement("section");
    comparison.className = "model-comparison";
    comparison.setAttribute("aria-label", "Model inference comparison");
    if (!cleanOutput || !conditionOutput) {
      comparison.innerHTML = `<div class="model-comparison-head"><h4>Model inference comparison</h4><p>Bu kart için prediction kaydı bulunamadı.</p></div>`;
    } else {
      const confidenceText = (value) => Number.isFinite(value) ? value.toFixed(2) : "—";
      const deltaText = confidenceDelta === null ? "—" : `${confidenceDelta >= 0 ? "+" : ""}${confidenceDelta.toFixed(1)} puan`;
      const severityText = severityDrop === null ? "—" : `${severityDrop >= 0 ? "+" : ""}${severityDrop.toFixed(0)}`;
      const severityMeaning = severityDrop === null ? "Seviye karşılaştırılamadı." : severityDrop > 0 ? "Oynanmış girdide daha düşük hasar seviyesi." : severityDrop < 0 ? "Oynanmış girdide daha yüksek hasar seviyesi." : "Hasar seviyesi aynı kaldı.";
      comparison.innerHTML = `
        <div class="model-comparison-head"><h4>Model inference comparison</h4><p>${escapeHtml(condition === "clean" ? "Referans çıktısı" : `${condition} · ${conditionOutput.model_id}`)}</p></div>
        <div class="model-output-grid">
          <div class="model-output clean"><span class="model-output-label">Clean (original) · temiz/orijinal</span><strong>${escapeHtml(cleanOutput.label)}</strong><span class="confidence">confidence ${confidenceText(cleanOutput.confidence)}</span><p class="rationale"><span class="rationale-label">Model rationale · model gerekçesi</span>${escapeHtml(cleanOutput.rationale || "Gerekçe kaydı yok.")}</p></div>
          <div class="model-delta"><div class="delta-item ${sameLabel ? "stable" : "changed"}">Label changed?<strong>${sameLabel ? "Hayır" : "Evet"}</strong></div><div class="delta-item">Confidence Δ<strong>${deltaText}</strong></div><div class="delta-item">Severity drop<strong>${severityText}</strong></div></div>
          <div class="model-output condition"><span class="model-output-label">Condition (modified) · oynanmış/koşullu</span><strong>${escapeHtml(conditionOutput.label)}</strong><span class="confidence">confidence ${confidenceText(conditionOutput.confidence)}</span><p class="rationale"><span class="rationale-label">Model rationale · model gerekçesi</span>${escapeHtml(conditionOutput.rationale || "Gerekçe kaydı yok.")}</p></div>
        </div>
        <p class="comparison-note"><strong>Nasıl okunur?</strong> Pozitif severity drop, modelin oynanmış görselde daha düşük hasar tahmin ettiğini gösterir. ${escapeHtml(severityMeaning)} Bu karşılaştırma aynı sample’ın clean ve condition prediction kayıtlarından yapılmıştır.</p>`;
    }
    oldTitle.replaceWith(title);
    if (oldParagraph) oldParagraph.remove();
    card.className = "audit-card";
    card.dataset.split = split;
    card.dataset.condition = condition;
    card.dataset.kind = kind;
    card.dataset.status = status;
    card.dataset.search = `${sample} ${split} ${condition} ${fields.payload || ""} ${fields.GT || ""}`.toLowerCase();
    card.prepend(facts);
    card.prepend(note);
    card.prepend(title);
    const imageGroup = card.querySelector(".imgs");
    if (imageGroup) imageGroup.before(comparison);
    card.querySelectorAll(".imgs figure").forEach((figure, index) => {
      const caption = document.createElement("figcaption");
      caption.textContent = index === 0 ? "Temiz referans görüntü" : "Uygulanan koşul görüntüsü";
      figure.prepend(caption);
    });
    card.querySelectorAll(".tweets section b").forEach((label, index) => { label.textContent = index === 0 ? "Temiz girdi" : "Koşul girdisi"; });
    gallery.append(card);
    return card;
  });

  app.querySelector("#card-total").textContent = transformed.length;
  const search = app.querySelector("#search");
  const splitFilter = app.querySelector("#split-filter");
  const typeFilter = app.querySelector("#type-filter");
  const statusFilter = app.querySelector("#status-filter");
  const count = app.querySelector("#gallery-count");
  const applyFilters = () => {
    const query = search.value.trim().toLowerCase();
    const split = splitFilter.value;
    const type = typeFilter.value;
    const status = statusFilter.value;
    let visible = 0;
    transformed.forEach((card) => {
      const match = (!query || card.dataset.search.includes(query)) && (split === "all" || card.dataset.split === split) && (type === "all" || card.dataset.kind === type) && (status === "all" || card.dataset.status === status);
      card.hidden = !match;
      if (match) visible += 1;
    });
    count.textContent = `${visible} / ${transformed.length} kart gösteriliyor`;
  };
  [search, splitFilter, typeFilter, statusFilter].forEach((control) => control.addEventListener("input", applyFilters));
  app.querySelector("#reset").addEventListener("click", () => { search.value = ""; splitFilter.value = "all"; typeFilter.value = "all"; statusFilter.value = "all"; applyFilters(); });
  applyFilters();
})();
