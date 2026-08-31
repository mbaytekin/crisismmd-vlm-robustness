# Session handoff (Cursor Grok, 2026-08-30)

Use this if another agent needs the manuscript/context state. Precedence: D018–D037 in `docs/PAPER_DECISIONS.md` > `reports/v3/ALL_RESULTS.md` > `docs/MANUSCRIPT_BUILD.md`. `paper.md` is a historical blueprint only. Active LaTeX root: `manuscript/main.tex` (gitignored). Venue: NeurIPS 2026 Trustworthy AI for Good (`dblblindworkshop`); checklist is not compiled. Main content ≤ 9 pages.

## Scientific locks (do not reopen)

- Six-model panel: Qwen3.5/3.6/3.8 27B BF16, Qwen3-VL 32B BF16, Mistral Small 3.1 24B BF16, Gemini 2.5 Flash.
- Primary estimand: full-cohort downward success = clean-correct mild/severe shifted lower / **720**. Eligible-only ASR is secondary.
- All **36** malicious-minus-matched-benign full-cohort effects positive and Holm-significant.
- Canonical size experiment is **relative overlay height 3%/5%/8% of image height** (60 sources, six models including Gemini). Not a literature-standard grid; investigator-chosen modest fractions. Cite Cheng et al. ECCV 2024 for size-as-factor / 3–15 px; cite Jenq & Shen (arXiv:2511.05325) only as motivation for a relative scale when resolutions vary (their ratio is max-fit 25/50/75/100%, not image-height %).
- Point-size follow-up (3/6/9/12/15 pt = px at 72 PPI, Cheng grid) is **secondary/appendix**. All six models are complete: unweighted means direct 1.67/2.22/5.83/11.94/13.61%, misleading 1.39/2.78/5.83/7.22/6.94%; **0/48** Holm. Rhetoric six-model means are 3.89/3.61/4.17/4.03%; **0/18** Holm.
- Human visual audit **COMPLETE** under D037: 234 sampled overlays, two
  independent blinded raters, all five disagreements adjudicated. Readability
  and non-occlusion statements must remain sample-bounded; no realism, stealth,
  or plausibility claims.
- D029 removes internal prompt-candidate/version labels and abandoned prompt
  proposals from all paper-facing use. The manuscript states only that one fixed
  zero-shot prompt was used and prompt dependence remains unresolved.
- Do not rerun the 720 main matrix. Do not start or stop GCP VMs unless the user asks. Do not invent missing numbers.

## What this session already did to the manuscript

- AI4GOOD packaging, overlay figures (California triplet + appendix style/size photos), restyled `figures/main_effects.pdf`.
- Main ASR table moved to appendix; Results lead with clean + Fig 2 + matched-benign + transitions.
- Point-size stays appendix with `figures/point_size_means.pdf` (six-model unweighted means). Method states 3/5/8% are investigator-chosen; Cheng/Jenq citations added (`jenq2025rendering`).
- D025 venue/figures; D026 size-citation rule; D027 Gemini execution freeze; **D028** unified six-model follow-up reporting.
- Last compile: Conclusion p.9, US Letter, workshop mode.
- The Results section now uses six clean-to-attacked 3x3 mean transition
  matrices from `manuscript/figures/transition_matrices.pdf`.

## Gemini follow-up status

Gemini is complete for main, style, **relative** size, natural-clean, official-test, text-rhetoric, and point-size. The two follow-up files contain 1,080/1,080 and 960/960 parsed rows with no request errors. D028 uses unified six-model reader-facing summaries (0/18 rhetoric, 0/48 point-size) while preserving relative size as the canonical size experiment.

API key lives only in gitignored `.env`. Never commit it or paste it into chat, commits, or logs.
