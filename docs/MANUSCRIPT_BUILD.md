# NeurIPS 2026 AI4GOOD Manuscript Build and Reproducibility Note

This document records how the anonymous NeurIPS 2026 Trustworthy AI for Good
(AI4GOOD) workshop manuscript was assembled, validated, and packaged. It is
intended to make the paper workflow reproducible for another computer or
another writing session.

## Source of truth

Paper claims and numbers must follow this precedence:

1. [`PAPER_DECISIONS.md`](PAPER_DECISIONS.md), especially accepted decisions D018--D032;
2. [`../reports/v3/ALL_RESULTS.md`](../reports/v3/ALL_RESULTS.md) for canonical V3 results;
3. [`../reports/v3/BF16_RUNTIME_DURATIONS.md`](../reports/v3/BF16_RUNTIME_DURATIONS.md) for measured open-model runtimes;
4. frozen executable configurations and result artifacts for implementation details;
5. [`../paper.md`](../paper.md) only as a historical structural blueprint.

`paper.md` contains older planning language and must not override accepted
decisions or completed V3 results. Historical V2, Qwen 9B, quantized, and MLX
repeat outputs are not paper-facing evidence. The canonical open-model results
use GCP A100/CUDA-vLLM with BF16; Gemini is reported as a separate hosted
service.

## Manuscript structure

The paper is an anonymous AI4GOOD workshop LaTeX document rooted at
`manuscript/main.tex` (`dblblindworkshop`; title “Trustworthy AI for Good”).
The NeurIPS paper checklist is not required and is not compiled.

| File | Role |
|---|---|
| `main.tex` | Anonymous entry point, packages, title, abstract, section order |
| `neurips_2026.sty` | Unmodified official NeurIPS 2026 style file |
| `sections/01_introduction.tex` | Motivation, research gap, and contributions |
| `sections/02_related_work.tex` | Crisis multimodality and typographic-attack context |
| `sections/03_method.tex` | Threat model, dataset, cohorts, attacks, models, metrics, tests |
| `sections/04_results.tex` | Clean competence, primary attacks, controls, under-triage, ablations |
| `sections/05_discussion.tex` | Interpretation and research-question answers |
| `sections/06_limitations.tex` | Scope, uncertainty, broader impact, and release constraints |
| `sections/07_conclusion.tex` | Bounded conclusion |
| `sections/appendix.tex` | Confidence intervals, panel/dataset accounting, secondary clean results, cohort composition, diagnostics, canonical and follow-up runtime, prompt, ablations, protocol amendments |
| `figures/` | Composed overlay JPEGs and generated quantitative PDF figures, including the 3x3 transition matrices |
| `references.bib` | Bibliography, including dataset, model, attack, and statistical references |
| `checklist.tex` | NeurIPS 2026 paper checklist (kept on disk; **not** `\input` for AI4GOOD) |

The paper-facing prompt is written out in the appendix as one fixed zero-shot
rubric. Internal prompt-development candidate and version labels are eliminated
from writing handoffs and reader-facing prose under D029.

## Assembly workflow

The manuscript was produced in the following order:

1. Freeze the accepted dataset, model-panel, prompt, attack, and reporting
   decisions in `PAPER_DECISIONS.md`.
2. Read the canonical V3 synthesis and runtime report, then transfer only their
   completed numbers and caveats into the LaTeX sections.
3. Use the full 720-sample cohort for the primary downward-success estimand;
   retain each model's clean-correct mild/severe eligible denominator and
   conditional ASR only as a secondary susceptibility view.
4. Separate clean competence from robustness, and separate malicious effects
   from modality-matched benign controls.
5. Put detailed Wilson intervals, event--class composition, severity-drop and
   modality-transition diagnostics, runtime accounting, and reproducibility
   details in the appendix.
6. Keep unresolved items explicit: human visual review is incomplete, Gemini
   and full preliminary compute accounting are not consolidated, and raw
   CrisisMMD assets cannot be redistributed.

The paper does not claim that the custom 720/120/60 cohorts are CrisisMMD or
literature-standard sample sizes. They are investigator-chosen V3 allocations;
the event--class structural zeros and conditional denominators are reported as
limitations.

## Compile the PDF

From the repository root, a local TeX installation can be used with:

```bash
cd manuscript
latexmk -pdf main.tex
```

The paper was also compiled with the Docker image below. The cache
directory is created as a user-owned temporary directory to avoid root-owned
cache permission problems:

```bash
cd manuscript
compile_cache_dir=$(mktemp -d /tmp/crisismmd-tectonic.XXXXXX)
docker run --rm \
  --user "$(id -u):$(id -g)" \
  -e XDG_CACHE_HOME=/tmp/tectonic-cache \
  -v "$compile_cache_dir:/tmp/tectonic-cache" \
  -v "$PWD:/work" \
  -w /work \
  dxjoke/tectonic-docker:latest \
  tectonic main.tex --keep-logs --keep-intermediates
```

Generated files such as `main.pdf`, `main.aux`, `main.bbl`, `main.log`, and
`main.out` stay in the local manuscript directory and are not included in the
source ZIP.

## Validation checklist

After editing, perform all of the following:

```bash
cd manuscript
pdfinfo main.pdf | rg '^(Pages|Page size):'
rg -n 'Overfull|undefined references|undefined citations|Emergency stop|Fatal error' main.log
```

The current validated PDF is US Letter. The main paper occupies nine pages and
the references begin on page 10; appendices and the checklist follow outside
the main-content limit. Also inspect the rendered pages containing the methods,
main results, appendix tables, and checklist for table overflow or unreadable
text.

Before sharing a revision, check that:

- every percentage, count, denominator, interval, and runtime matches the
  canonical reports;
- the five open models are described as A100/vLLM BF16 and Gemini as hosted;
- MLX, V2, Qwen 9B, and retired gate results are not imported into primary claims;
- no internal prompt-development candidate or version labels appear in
  reader-facing prose or writing handoffs;
- the nine-page main-content limit, anonymity, privacy, and unresolved caveats
  remain intact.

## Build the source ZIP

The manuscript directory is ignored by Git because it contains local PDFs and
build artifacts. To package the current source for transfer or submission, run
`zip` from the `manuscript/` directory so that the archive has a clean source root:

```bash
cd manuscript
zip -q manuscript.next.zip \
  main.tex \
  neurips_2026.sty \
  references.bib \
  README.md \
  WRITING_PLAN.md \
  figures/main_effects.pdf \
  figures/transition_matrices.pdf \
  figures/overlay_benign.jpg \
  figures/overlay_direct.jpg \
  figures/overlay_misleading.jpg \
  figures/style_simple.jpg \
  figures/style_news.jpg \
  figures/style_camo.jpg \
  figures/size_small.jpg \
  figures/size_medium.jpg \
  figures/size_large.jpg \
  figures/point_size_means.pdf \
  sections/01_introduction.tex \
  sections/02_related_work.tex \
  sections/03_method.tex \
  sections/04_results.tex \
  sections/05_discussion.tex \
  sections/06_limitations.tex \
  sections/07_conclusion.tex \
  sections/appendix.tex
mv -f manuscript.next.zip manuscript.zip
unzip -t manuscript.zip
```

The source package contains the entry point, official style, bibliography,
two manuscript notes, eight section files, and the composed paper figures. It
does not contain `checklist.tex`, raw CrisisMMD images or tweets, the private
overlay directory, model weights, caches, raw model outputs, or generated build
files.

## Git and transfer note

Because `manuscript/` is in `.gitignore`, a normal `git pull` updates the code,
configs, reports, and documentation but not the local manuscript PDF or ZIP.
Transfer `manuscript.zip` separately when moving to another
computer. On the new computer, extract it under `manuscript/` and re-run the
compile and validation commands above.

The manuscript is deliberately not versioned in this repository. It is authored
and shared through an Overleaf project, uploaded as `manuscript.zip`; the source
ZIP was verified to compile from a clean extraction with no local files present.
Keeping it out of Git also keeps the composed CrisisMMD overlay figures out of a
hosted repository, which the CrisisNLP terms and D025 require.

**One source at a time.** While the Overleaf project is being edited, treat
Overleaf as authoritative and do not edit `manuscript/` locally. When that round
finishes, download the Overleaf source back over `manuscript/`, then re-run the
validation checklist above before any further local edit. Editing both copies in
parallel silently forks the paper and breaks the guarantee that every number
traces to `reports/v3/ALL_RESULTS.md`.
