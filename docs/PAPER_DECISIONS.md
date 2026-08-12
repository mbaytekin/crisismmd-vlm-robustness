# Paper decision log

Last updated: 2026-08-12

This is the single living record of decisions that can affect the manuscript.
It records what was decided, why, where the evidence lives, what changed, and
which caveats must remain visible. `paper.md` is the manuscript blueprint;
executable YAML and frozen artifact hashes are the implementation truth. When
they disagree, do not silently choose one: update this log and reconcile the
paper before making a claim.

## How to use this file

- Add a dated entry whenever a prompt, cohort, threshold, model panel, metric,
  statistical test, claim, or exclusion rule changes.
- Never delete an old decision. Mark it `SUPERSEDED` and link its replacement.
- A result observed before a protocol change stays historical; do not relabel
  it as a result from the new protocol.
- Link every empirical statement to a repository artifact. Conversation memory
  alone is not evidence.
- Do not change thresholds after viewing attack outcomes. A necessary change
  requires a dated amendment and a separately labeled analysis.

For an external GPT session, provide the GitHub links to this file and
`paper.md`, then use:

> Treat ACCEPTED decisions in `docs/PAPER_DECISIONS.md` as current. Treat
> SUPERSEDED entries as history and OPEN entries as unresolved. Check every
> proposed manuscript claim against the linked evidence, preserve all stated
> caveats, and identify any conflict with `paper.md` before rewriting it.

## Current protocol snapshot

| Item | Current decision |
|---|---|
| Task | Three-class CrisisMMD image damage severity |
| Input | Target image plus accompanying tweet; image annotation is ground truth |
| Scope | Visible physical damage to man-made infrastructure and utilities |
| Prompt | `frozen_prompt_v4.yaml`, zero-shot P5 rubric |
| Prompt hash | `1fa1a4a2b61c4aaadb95215385cd97915fd515ca4b19fc477ba98291cdf39ee6` |
| First clean screen | 180 examples, balanced 60 per class |
| First gate | Parse >= 99.5%, accuracy >= 60%, macro-F1 >= 55%, every class recall >= 40% |
| Confirmatory clean gate | Untouched 720-example main split, balanced 240 per class |
| Main gate | Parse >= 99.5%, accuracy >= 70%, macro-F1 >= 65%, every class recall >= 50% |
| Attack eligibility | A model must pass both clean gates |
| Decoding | Temperature 0, top-p 1, seed 42, max 150 tokens, thinking disabled |
| Primary runtime | Native MLX-VLM 0.6.3 on Apple Silicon; one model at a time |
| Precision | Standard 12B-32B panel at 8-bit; 235B/397B ultra tier at 4-bit |
| Primary safety focus | Downward severity shifts and induced under-triage |

Executable sources:

- [`configs/v3/models.yaml`](../configs/v3/models.yaml)
- [`configs/prompts/frozen_prompt_v4.yaml`](../configs/prompts/frozen_prompt_v4.yaml)
- [`reports/v3/artifact_lock.json`](../reports/v3/artifact_lock.json)
- [`scripts/run_v3_model.sh`](../scripts/run_v3_model.sh)
- [`scripts/run_all_v3_mac_models.sh`](../scripts/run_all_v3_mac_models.sh)

## Active decisions

### D001 - Paper framing

- **Status:** ACCEPTED
- **Date:** 2026-08-11
- **Decision:** Frame the paper as a competence-gated, paired robustness study,
  not a general model leaderboard or an operational disaster-response trial.
- **Reason:** Attack effects are interpretable only when the clean classifier is
  sufficiently competent and each modified input can be paired with its clean
  source observation.
- **Paper impact:** Lead with direction-sensitive under-triage risk. Keep broad
  real-world safety and model-scaling claims bounded.
- **Evidence:** [`paper.md`](../paper.md),
  [`docs/V3_MODEL_SELECTION.md`](V3_MODEL_SELECTION.md).

### D002 - Task semantics and evidence hierarchy

- **Status:** ACCEPTED
- **Date:** 2026-08-11
- **Decision:** Predict `little_or_no_damage`, `mild_damage`, or
  `severe_damage` from visible physical damage to man-made infrastructure and
  utilities. The tweet can clarify visible evidence but cannot override the
  image. Hazard context, vegetation damage, response activity, and disaster
  seriousness do not by themselves establish infrastructure damage.
- **Reason:** The original severity label is image-centric, and the earlier
  prompt over-inferred damage from contextual hazard cues.
- **Paper impact:** State this operational scope verbatim in Methods and discuss
  any mismatch with broader interpretations of CrisisMMD labels.
- **Evidence:** [`configs/prompts/frozen_prompt_v4.yaml`](../configs/prompts/frozen_prompt_v4.yaml),
  [`docs/V3_PROMPT_VALIDATION.md`](V3_PROMPT_VALIDATION.md).

### D003 - Frozen production prompt

- **Status:** ACCEPTED
- **Date:** 2026-08-11
- **Decision:** Use the P5 rubric zero-shot prompt, locked as V4, for primary
  model screening and production inference. Do not modify its text after lock.
- **Reason:** On the independent 180-example development split, P5 exceeded P6
  in accuracy, macro-F1, mild recall, severe recall, and latency. The paired
  accuracy difference was small and not statistically distinguishable from
  zero, so few-shot examples had no supported primary benefit.
- **Paper impact:** Report P5 as a post-hoc prompt revision. Report P6 only as a
  prompt sensitivity analysis.
- **Evidence:** [`reports/v3/prompt_validation_comparison.json`](../reports/v3/prompt_validation_comparison.json),
  [`docs/V3_PROMPT_VALIDATION.md`](V3_PROMPT_VALIDATION.md).

### D004 - First-stage clean screen uses 180 examples

- **Status:** ACCEPTED WITH CAVEAT
- **Date:** 2026-08-12
- **Decision:** Replace the former 90-example production pilot with the
  180-example `prompt_validation` clean screen, balanced at 60 per class. The
  first-stage thresholds remain 60% accuracy, 55% macro-F1, 40% minimum class
  recall, and 99.5% parse rate.
- **Reason:** The larger sample gives a less volatile class-balanced estimate
  and matches the configuration used for the selected rubric comparison.
- **Caveat:** V4 was selected on this split using Qwen3.5 27B, so that model's
  180-example score is post-hoc and cannot be its confirmatory result. In
  addition, all remaining independent little/no examples in this split are
  from Hurricane Irma, creating a class-event confound. Use this split for
  screening/model routing, not event-general performance claims.
- **Paper impact:** The untouched 720-example main gate must carry confirmatory
  clean-performance claims, especially for Qwen3.5 27B.
- **Supersedes:** D004-H1 below.
- **Evidence:** [`configs/v3/models.yaml`](../configs/v3/models.yaml),
  [`reports/v3/prompt_validation_split.json`](../reports/v3/prompt_validation_split.json).

### D005 - Main clean confirmation remains untouched

- **Status:** ACCEPTED
- **Date:** 2026-08-12
- **Decision:** A first-stage passer must also pass the balanced 720-example
  main clean gate: 70% accuracy, 65% macro-F1, 50% recall in every class, and
  99.5% parse rate.
- **Reason:** A stricter untouched cohort prevents prompt-development results
  and aggregate accuracy from hiding class collapse.
- **Paper impact:** No attack result is confirmatory unless its model passes
  this gate. Publish clean failures to avoid selective reporting.
- **Evidence:** [`configs/v3/models.yaml`](../configs/v3/models.yaml),
  [`src/v3_clean_gate.py`](../src/v3_clean_gate.py).

### D006 - Attack design and controls

- **Status:** ACCEPTED
- **Date:** 2026-08-11
- **Decision:** Use fixed black-box payloads with direct-instruction,
  misleading-claim, and benign families. Deliver matched semantics through the
  image, tweet, or both. Keep style and size ablations separate.
- **Reason:** This isolates delivery modality and malicious semantics while
  measuring generic instability from added text.
- **Paper impact:** Contrast every malicious condition with clean and its
  modality-matched benign control. Do not equate every label change with a
  successful attack.
- **Evidence:** [`configs/v3/attack_payloads.yaml`](../configs/v3/attack_payloads.yaml),
  [`reports/v3/attack_validation.md`](../reports/v3/attack_validation.md).

### D007 - Primary robustness outcomes

- **Status:** ACCEPTED; IMPLEMENTATION PARTLY PENDING
- **Date:** 2026-08-11
- **Decision:** Emphasize target-eligible attack success, ordinal severity drop,
  induced under-triage, induced critical under-triage, and malicious-minus-
  benign paired effects. Treat attacked accuracy as descriptive.
- **Reason:** Downward errors are the safety-relevant direction, while aggregate
  accuracy can hide corrections and newly induced failures in the same run.
- **Paper impact:** Exact numerators/denominators and uncertainty must accompany
  percentages. The final evaluator still needs target-eligible ASR and induced
  critical under-triage before submission.
- **Evidence:** [`paper.md`](../paper.md),
  [`reports/v3/methodology_summary.md`](../reports/v3/methodology_summary.md).

### D008 - Statistical analysis

- **Status:** ACCEPTED BEFORE FULL ATTACK RESULTS
- **Date:** 2026-08-11
- **Decision:** Use Wilson 95% intervals for proportions, paired bootstrap with
  seed 42 and at least 2,000 replicates for continuous/paired effects, exact
  two-sided McNemar tests for paired binary outcomes, and Holm correction within
  each predeclared comparison family. Analyze models separately before any
  equal-model aggregate; do not pool predictions as independent observations.
- **Paper impact:** Avoid causal language and report model/event dependence.
- **Evidence:** Statistical analysis plan in [`paper.md`](../paper.md).

### D009 - Model panel and precision tiers

- **Status:** ACCEPTED
- **Date:** 2026-08-11
- **Decision:** Screen eight open VLM candidates from Gemma, Mistral, Qwen3-VL,
  and Qwen3.5. Use 8-bit MLX for 12B-32B models and separately label the 235B
  and 397B 4-bit tier.
- **Reason:** The panel adds family and architecture diversity while fitting the
  available 512 GB Apple unified-memory system.
- **Paper impact:** Do not interpret standard-versus-ultra differences as pure
  parameter scaling; architecture and precision are confounded.
- **Evidence:** [`configs/v3/models.yaml`](../configs/v3/models.yaml),
  [`docs/V3_MODEL_SELECTION.md`](V3_MODEL_SELECTION.md).

### D010 - Runtime and reproducibility

- **Status:** ACCEPTED
- **Date:** 2026-08-12
- **Decision:** Run MLX-VLM 0.6.3 natively on Apple Silicon, one model server at
  a time, with deterministic settings and immutable model locks. Stop each
  server after its run to offload weights from unified memory while retaining
  the Hugging Face disk cache.
- **Reason:** Metal is unavailable through the ordinary Linux pipeline
  container, and concurrent large checkpoints create unnecessary memory risk.
- **Paper impact:** Record backend patches and dependencies. Do not pool MLX and
  NVIDIA/vLLM results without an explicit backend-equivalence study.
- **Evidence:** [`docs/MAC_STUDIO_RUNBOOK.md`](MAC_STUDIO_RUNBOOK.md),
  [`scripts/patch_mlx_vlm_mac_thread_stream.py`](../scripts/patch_mlx_vlm_mac_thread_stream.py).

### D011 - Claims discipline for external baselines

- **Status:** ACCEPTED; LITERATURE TABLE PENDING
- **Date:** 2026-08-12
- **Decision:** Do not present 60% clean accuracy as a universal literature
  standard and do not directly rank scores obtained from different splits,
  class distributions, prompts, or supervised regimes. Supervised CLIP/VLM
  classifiers and zero-shot generative VLMs are contextual baselines, not
  interchangeable measurements.
- **Reason:** CrisisMMD severity is imbalanced in its natural distribution, and
  majority-class accuracy alone can exceed 60%. Macro-F1 and per-class recall
  are required alongside accuracy.
- **Paper impact:** Add a regime-aware related-work table after primary-source
  verification; avoid a claim of being the first study until the systematic
  search is complete.
- **Evidence:** Research-gap and claims-discipline sections in
  [`paper.md`](../paper.md). Citation verification remains OPEN-003.

## Superseded decisions and historical results

### D004-H1 - Use the 90-example pilot as the production screen

- **Status:** SUPERSEDED by D004
- **Active period:** 2026-08-11 to 2026-08-12
- **Old decision:** Screen each model on 90 clean pilot examples before main.
- **Preservation rule:** Existing 90-example metrics remain historical and must
  not determine eligibility under the current 180-example protocol.

Historical results:

| Model/prompt | Cohort | Accuracy | Macro-F1 | Current interpretation |
|---|---:|---:|---:|---|
| Qwen3.5 27B, frozen P3 | 90 | 0.489 | 0.447 | Historical failed pilot |
| Qwen3.5 27B, P4 few-shot | 90 | 0.578 | 0.557 | Historical failed pilot; minimum recall 0.30 |
| Qwen3-VL 32B, V4 | 90 | 0.544 | 0.546 | Historical only; rerun on 180 required |

### D003-H1 - Frozen P3 is the production prompt

- **Status:** SUPERSEDED by D003
- **Old decision:** Use `frozen_prompt.yaml` / frozen P3 for production.
- **Preservation rule:** Keep its files and results as historical baselines; do
  not overwrite or relabel them as V4 results.

## Current empirical status

| Model/configuration | Current evidence | Status |
|---|---|---|
| Qwen3.5 27B + P5/V4 | 115/180 correct; accuracy 0.639; macro-F1 0.631; minimum recall 0.433 | Passes the 180 numerical gate, but post-hoc; main pending |
| Qwen3.5 27B + P6 few-shot | 113/180 correct; accuracy 0.628; macro-F1 0.621 | Sensitivity only; not selected |
| Mistral Small 3.1 24B + V4 | Model load and one-image 180-manifest smoke test passed | Full 180 screen pending |
| Qwen3-VL 32B + V4 | Only superseded 90-example result exists | New 180 screen pending |
| Qwen3-VL 235B-A22B + V4 | Checkpoint present | Screen pending |
| Qwen3.5 397B-A17B + V4 | Checkpoint present | Screen pending |
| Gemma 4 candidates | Gated checkpoints absent from standard local cache | Download/access pending |

The Qwen3.5 P5 gate artifact is
[`reports/v3/clean_gates/v3_qwen35_27b_p5_rubric_zero_promptval_seed42.json`](../reports/v3/clean_gates/v3_qwen35_27b_p5_rubric_zero_promptval_seed42.json).

## Paper synchronization debt

`paper.md` predates D003 and D004 in several places. Before treating it as a
current manuscript snapshot, update all of the following:

- Draft abstract: distinguish the 180-example screen from the attack cohorts;
  remove the old implication that all 990 V3 pairs receive ten conditions.
- Final V3 split table: retain the generated 90-example historical pilot but
  explain that current production screening uses a separate 180-example split.
- Frozen prompt section: replace P3 as the active prompt with V4/P5 and disclose
  post-hoc selection.
- Competence gate section: replace the 90-example active gate with the
  180-example screen and retain the 720-example main confirmation.
- Qualification-results template: rename the `Pilot` column to `180-screen`.
- Workload/reproducibility counts: current qualified-model protocol produces
  180 screening predictions plus 9,000 main/style/size condition predictions.

Until that reconciliation is complete, this decision log is authoritative for
the active protocol and `paper.md` remains authoritative for unchanged threat
model, outcome, and statistical-analysis sections.

## Open decisions

### OPEN-001 - Main qualification outcomes

Run all locally available candidates through the 180 screen and then the
untouched 720 main gate. Do not alter thresholds in response to these results.

### OPEN-002 - Human visual review

Freeze reviewer sampling/full-review scope, collect at least two blinded
ratings per unique modified image, and select the agreement statistic before
final robustness claims.

### OPEN-003 - Related-work verification

Complete a primary-source literature table separating zero-shot generative
VLMs, supervised VLM/CLIP classifiers, caption-augmentation pipelines, data
splits, class distributions, and reported metrics.

### OPEN-004 - Evaluator completion

Implement target-eligible ASR and induced critical under-triage, then verify
paired confidence intervals and Holm families before full attack inference.

### OPEN-005 - Paper protocol synchronization

Resolve every item in `Paper synchronization debt` and date the resulting
`paper.md` snapshot before pushing a manuscript-facing release.

## New entry template

```markdown
### DNNN - Short title

- **Status:** PROPOSED | ACCEPTED | ACCEPTED WITH CAVEAT | SUPERSEDED
- **Date:** YYYY-MM-DD
- **Decision:** What changes or stays fixed.
- **Reason:** Why this choice is justified.
- **Caveat:** Bias, leakage, uncertainty, or scope limitation.
- **Paper impact:** Sections, claims, figures, or tables affected.
- **Supersedes:** Prior decision ID, if any.
- **Evidence:** Repository paths or primary sources.
```
