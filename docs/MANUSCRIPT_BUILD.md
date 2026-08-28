# NeurIPS 2026 Manuscript Build and Reproducibility Note

This document records how the anonymous NeurIPS 2026 manuscript was assembled,
validated, and packaged. It is intended to make the paper workflow reproducible
for another computer or another writing session.

## Source of truth

Paper claims and numbers must follow this precedence:

1. [`PAPER_DECISIONS.md`](PAPER_DECISIONS.md), especially accepted decisions D018--D021;
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

The paper is an anonymous, submission-mode NeurIPS 2026 LaTeX document rooted at
`manuscript/neurips2026/main.tex`:

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
| `sections/appendix.tex` | Confidence intervals, secondary clean results, cohort composition, diagnostics, runtime, prompt, ablations, protocol amendments |
| `references.bib` | Bibliography, including dataset, model, attack, and statistical references |
| `checklist.tex` | NeurIPS 2026 paper checklist |

The paper-facing prompt is written out in the appendix as one fixed zero-shot
rubric. Internal development identifiers such as P5, V4, and P7 are not used as
reader-facing experimental names.

## Assembly workflow

The manuscript was produced in the following order:

1. Freeze the accepted dataset, model-panel, prompt, attack, and reporting
   decisions in `PAPER_DECISIONS.md`.
2. Read the canonical V3 synthesis and runtime report, then transfer only their
   completed numbers and caveats into the LaTeX sections.
3. Keep the primary analysis conditional on each model's clean-correct
   mild/severe decisions, with the exact eligible denominator shown in every
   primary attack table.
4. Separate clean competence from robustness, and separate malicious effects
   from modality-matched benign controls.
5. Put detailed Wilson intervals, event--class composition, severity-drop and
   modality-transition diagnostics, runtime accounting, prompt history, and
   protocol amendments in the appendix.
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
cd manuscript/neurips2026
latexmk -pdf main.tex
```

The paper was also compiled with the Docker image below. The cache
directory is created as a user-owned temporary directory to avoid root-owned
cache permission problems:

```bash
cd manuscript/neurips2026
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
cd manuscript/neurips2026
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
- the four open models are described as A100/vLLM BF16 and Gemini as hosted;
- MLX, V2, Qwen 9B, and retired gate results are not imported into primary claims;
- no P5/V4/P7 internal prompt labels appear in reader-facing prose;
- the nine-page main-content limit, anonymity, privacy, and unresolved caveats
  remain intact.

## Build the source ZIP

The manuscript directory is ignored by Git because it contains local PDFs and
build artifacts. To package the current source for transfer or submission, run
`zip` from the `manuscript/` directory so that the archive has a clean
`neurips2026/` root:

```bash
cd manuscript
zip -q neurips2026.next.zip \
  neurips2026/main.tex \
  neurips2026/neurips_2026.sty \
  neurips2026/checklist.tex \
  neurips2026/references.bib \
  neurips2026/README.md \
  neurips2026/WRITING_PLAN.md \
  neurips2026/sections/01_introduction.tex \
  neurips2026/sections/02_related_work.tex \
  neurips2026/sections/03_method.tex \
  neurips2026/sections/04_results.tex \
  neurips2026/sections/05_discussion.tex \
  neurips2026/sections/06_limitations.tex \
  neurips2026/sections/07_conclusion.tex \
  neurips2026/sections/appendix.tex
mv -f neurips2026.next.zip neurips2026.zip
unzip -t neurips2026.zip
```

The source package contains 14 files: the entry point, official style,
checklist, bibliography, two manuscript notes, and eight section files. It does
not contain raw CrisisMMD images or tweets, generated attack images, model
weights, caches, raw model outputs, or generated build files.

## Git and transfer note

Because `manuscript/` is in `.gitignore`, a normal `git pull` updates the code,
configs, reports, and documentation but not the local manuscript PDF or ZIP.
Transfer `manuscript/neurips2026.zip` separately when moving to another
computer. On the new computer, extract it under `manuscript/` and re-run the
compile and validation commands above.
