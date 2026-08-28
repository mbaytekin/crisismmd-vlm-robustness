# Paper decision log

Last updated: 2026-08-26

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
| Prompt development evidence | 180 examples, balanced 60 per class; post-hoc routing/history only, not a model gate |
| Main clean evaluation | Frozen 720-example main split, balanced 240 per class; descriptive clean characterization |
| Secondary clean evaluation | All 3,474 exact-SHA-unique valid rows plus the published 529-row test split |
| Dataset interpretation | Main-720 is a custom balanced paired cohort; official-529 is natural but secondary/post-hoc |
| Clean-performance interpretation | Report parse rate, accuracy, macro-F1, ordinal MAE, and per-class recall without a pass/fail or deployment threshold |
| Robustness denominator | Predeclared clean-correct mild/severe decisions for each model |
| Attack eligibility | The fixed five-model paper panel is analyzed separately; lower clean competence narrows interpretation rather than invalidating paired estimates |
| Decoding | Temperature 0, top-p 1, seed 42, max 150 tokens, thinking disabled |
| Runtime | Canonical open-model outputs use GCP A100/CUDA-vLLM; Gemini uses its hosted Batch API; MLX repeats are noncanonical audit evidence |
| Paper panel | Qwen3.5 27B BF16, Qwen3.6 27B BF16, Qwen3-VL 32B BF16, Mistral Small 3.1 24B BF16, Gemini 2.5 Flash |
| Precision | Four open checkpoints use BF16; Gemini is a hosted model with provider-managed precision |
| Primary safety focus | Downward severity shifts and induced under-triage |

Executable sources:

- [`configs/v3/models.yaml`](../configs/v3/models.yaml)
- [`configs/v3/final_analysis_protocol.yaml`](../configs/v3/final_analysis_protocol.yaml)
- [`configs/prompts/frozen_prompt_v4.yaml`](../configs/prompts/frozen_prompt_v4.yaml)
- [`reports/v3/artifact_lock.json`](../reports/v3/artifact_lock.json)
- [`scripts/run_v3_final_experiments.sh`](../scripts/run_v3_final_experiments.sh)

## Active decisions

### D001 - Paper framing

- **Status:** SUPERSEDED IN PART by D012 and D018; paired-study framing remains active, competence-gated wording does not
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

- **Status:** SUPERSEDED IN PART by D018; the cohort remains prompt-development history, while its model pass/fail thresholds are inactive
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
- **Paper impact:** Report this cohort only as prompt-development/routing history.
  Final clean characterization comes from the 720 main, 3,474 natural, and 529
  official-test evaluations without a qualification label.
- **Supersedes:** D004-H1 below.
- **Evidence:** [`configs/v3/models.yaml`](../configs/v3/models.yaml),
  [`reports/v3/prompt_validation_split.json`](../reports/v3/prompt_validation_split.json).

### D005 - Main clean confirmation remains untouched

- **Status:** SUPERSEDED by D018 for thresholds and by D016 for the cohort's current role
- **Date:** 2026-08-12
- **Historical decision:** A first-stage passer had to pass the balanced
  720-example main clean gate before receiving attack inference.
- **Preserved history:** The 720-example cohort and original thresholds remain
  recorded in historical artifacts. D016 preserves the cohort as the primary
  balanced paired experiment; D018 removes threshold-based paper reporting.
- **Reason:** A stricter untouched cohort prevents prompt-development results
  and aggregate accuracy from hiding class collapse.
- **Historical paper impact (superseded by D012):** This gate originally
  blocked confirmatory attack results. It is now reported as a descriptive
  deployment-readiness indicator, and clean failures remain visible.
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

- **Status:** ACCEPTED; IMPLEMENTED BEFORE CANONICAL ATTACK INFERENCE
- **Date:** 2026-08-11
- **Decision:** Emphasize target-eligible attack success, ordinal severity drop,
  induced under-triage, induced critical under-triage, and malicious-minus-
  benign paired effects. Treat attacked accuracy as descriptive.
- **Reason:** Downward errors are the safety-relevant direction, while aggregate
  accuracy can hide corrections and newly induced failures in the same run.
- **Paper impact:** Exact numerators/denominators and uncertainty must accompany
  percentages. Generic ASR remains supplementary.
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

- **Status:** SUPERSEDED IN PART by D013; historical 8-bit results are retained
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

- **Status:** SUPERSEDED IN PART by D020; deterministic provenance remains active, MLX-only runtime scope does not
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

### D012 - Separate deployment readiness from conditional robustness

- **Status:** SUPERSEDED IN PART by D018; conditional clean-correct estimation remains active, deployment-threshold reporting does not
- **Date:** 2026-08-12
- **Decision:** Keep the frozen 720-example thresholds as a descriptive
  deployment-readiness gate, but do not use them to block the fixed attack
  matrix. Estimate robustness separately for each model among predeclared
  clean-correct target-eligible decisions and report every denominator.
- **Reason:** A model can be unsuitable for deployment yet still provide a
  valid conditional estimate of whether an initially correct mild/severe
  judgment is pushed downward by malicious content.
- **Caveat:** Low clean competence can make the eligible denominator small or
  class-skewed. Such estimates are conditional security audits, not evidence
  that the model is operationally useful.
- **Paper impact:** Remove statements that equate gate failure with invalid
  attack inference. Report clean competence first and keep models separate.
- **Supersedes:** The attack-blocking parts of D001 and D005.
- **Evidence:** [`configs/v3/final_analysis_protocol.yaml`](../configs/v3/final_analysis_protocol.yaml),
  [`src/v3_final_analysis.py`](../src/v3_final_analysis.py).

### D013 - Canonical Qwen precision and local model identity

- **Status:** SUPERSEDED by D019 for the final paper panel; retained as execution history
- **Date:** 2026-08-12
- **Decision:** Use the verified local
  `mlx-community/Qwen3.5-27B-bf16` checkpoint for the primary dense-Qwen run.
  Treat `mlx-community/Qwen3-VL-32B-Instruct-bf16` as unavailable because that
  checkpoint is not present locally; do not download it automatically. Keep
  Mistral 24B 8-bit as a cross-family run and preserve every historical 8-bit
  result without overwrite.
- **Caveat:** Precision, architecture, and family differ across some models;
  comparisons are descriptive, not pure parameter- or precision effects.
- **Paper impact:** Always report exact model ID and precision. A clean-only
  BF16-versus-8-bit table is secondary sensitivity evidence.
- **Evidence:** [`configs/v3/final_analysis_protocol.yaml`](../configs/v3/final_analysis_protocol.yaml),
  [`scripts/run_v3_final_experiments.sh`](../scripts/run_v3_final_experiments.sh).

### D014 - Single modality-neutral prompt sensitivity

- **Status:** SUPERSEDED by D021; no P7 inference was run
- **Date:** 2026-08-12
- **Decision:** Keep frozen V4/P5 unchanged for primary results. After the main
  experiment, compare it on the same 90-sample pilot with one predeclared P7
  variant that preserves the rubric and output format but uses modality-neutral
  context wording. Do not add attack-aware or prompt-injection language.
- **Paper impact:** Label P7 secondary. If modality ordering changes, describe
  it as prompt-sensitive rather than replacing the primary prompt.
- **Evidence:** [`configs/prompts/p7_modality_neutral_sensitivity.yaml`](../configs/prompts/p7_modality_neutral_sensitivity.yaml).

### D015 - Final analysis definitions are frozen before new attack outputs

- **Status:** ACCEPTED
- **Date:** 2026-08-12
- **Decision:** Primary outcomes are downward ASR, severity drop on three
  declared cohorts, induced severe and critical under-triage, corrected direct
  target-eligible ASR, malicious-minus-matched-benign paired effects, class
  transitions, and predeclared modality interaction patterns. Use 5,000 paired
  bootstrap draws with seed 42, exact two-sided McNemar, and Holm correction
  within comparison families.
- **Caveat:** `joint_only_synergy`, `persistent_visual`, and related labels are
  observational pattern names, not mechanistic causal proof.
- **Evidence:** [`configs/v3/final_analysis_protocol.yaml`](../configs/v3/final_analysis_protocol.yaml),
  [`tests/test_v3_final_analysis.py`](../tests/test_v3_final_analysis.py).

### D016 - Preserve V3 main and add natural/official clean benchmarks

- **Status:** ACCEPTED WITH CAVEAT BEFORE SECONDARY CLEAN INFERENCE
- **Date:** 2026-08-14
- **Decision:** Keep the frozen 720-row, class-balanced V3 main cohort as the
  primary paired robustness experiment. Add clean-only evaluation on all 3,474
  locally valid exact-SHA-unique severity rows and on the exact published
  529-row CrisisMMD test split. Do not relabel either secondary cohort as a new
  untouched confirmatory test.
- **Reason:** Main-720 follows the literature-supported principle of
  exact/near-duplicate separation and gives equal class precision for paired
  under-triage analysis. Natural-3,474 characterizes local class/event
  prevalence, while official-529 enables split-named literature comparability.
  No single cohort serves all three purposes. The exact 720/120/60 allocation
  is an investigator-chosen V3 protocol decision, not a CrisisMMD or literature
  standard and not the result of an a priori power calculation.
- **Caveat:** Main-720 is custom, event-equalizing, and allocated after smaller
  V3 cohorts; it is neither event-proportional nor the official split. Under
  the V3 clustering rule, official train/test share 106 duplicate clusters and
  only 319/529 official-test rows are independent of every existing V3 cohort.
  The official test is severe-majority (332/529; 62.8%), so accuracy must be
  paired with macro-F1 and per-class recall. Main event-by-class structural
  zeros prevent source-population event-by-class reweighting; only class-prior
  reweighting is supported, and event results remain descriptive.
- **Label-quality amendment:** The published severity files contain 11
  exact-byte image groups with conflicting severity labels. Four retained main
  rows belong to those groups. Preserve the frozen main result and report an
  exclusion sensitivity; do not silently overwrite labels or samples.
- **Versioning rule:** Any replacement sample design must be introduced as V4,
  allocate its main cohort before auxiliary cohorts, predeclare its precision
  target, regenerate all attacks, and rerun every model. Existing V3 artifacts
  and results remain immutable.
- **Paper impact:** State explicitly what 18,082, 3,526, 3,474, 529, and 720
  count. Report natural-clean event/event-by-class metrics and cluster-bootstrap
  intervals separately from balanced paired attack effects.
- **Evidence:** [`reports/v3/dataset_protocol_audit.md`](../reports/v3/dataset_protocol_audit.md),
  [`configs/v3/dataset_evaluation.yaml`](../configs/v3/dataset_evaluation.yaml),
  [`src/v3_dataset_protocol.py`](../src/v3_dataset_protocol.py),
  [Alam et al. 2020](https://doi.org/10.1109/ASONAM49781.2020.9381294).

### D017 - Freeze paired presentation-style and text-size ablations

- **Status:** ACCEPTED FOR DESIGN AND ANALYSIS; model-panel/runtime clauses superseded by D019-D020
- **Date:** 2026-08-14
- **Decision:** Preserve the existing V3 style (120 sources; 40 per class) and
  size (60 sources; 20 per class) cohorts. Run them as separate, secondary,
  within-sample paired experiments on locally complete checkpoints. The current
  default panel is Qwen3.5-27B BF16, Mistral Small 3.1 24B 8-bit, and Qwen3-VL
  32B 8-bit. Keep models serial, inference concurrency one, and report every
  model and precision separately.
- **Terminology:** Rename the paper-facing style analysis to
  **presentation-style ablation**. Simple, fictional-news, and camouflage
  variants change a bundled presentation strategy that includes contrast,
  background, occupied area, and placement policy. Do not attribute their
  contrast to a single isolated style component. The size experiment is a
  cleaner one-factor contrast: within sample and semantics, payload, simple
  renderer, placement, colors, and opacity are fixed while target relative font
  height changes from 3% to 5% to 8%.
- **Sampling rationale:** Both cohorts are class-balanced, event-diversified,
  deterministic, globally duplicate-cluster-disjoint, and complete across ten
  paired conditions. They are mechanism-analysis cohorts, not estimates of the
  natural CrisisMMD event/class prevalence. No published CrisisMMD protocol
  defines a canonical visual-ablation distribution.
- **Metrics:** Primary reporting is downward ASR among clean-correct
  mild/severe samples. Report exact numerators/denominators, Wilson intervals,
  malicious-minus-matched-benign paired risk differences, target-eligible
  severity drop, induced severe/critical under-triage, 5,000-draw paired
  bootstrap intervals, exact McNemar tests, and Holm correction within each
  semantics/ablation family. Add direct pairwise variant contrasts and retain
  sample-level size patterns; do not claim monotonicity from an aggregate line
  alone.
- **Precision caveat:** At the full-cohort worst case, a binomial 95% interval
  has an approximate half-width of 8.8 percentage points for style and 12.3
  points for size. Model-specific clean-correct mild/severe denominators can be
  smaller, so exact denominators and intervals determine claim strength.
- **Data caveat:** News banners always render at the bottom, while 171 news rows
  retain the deterministic simple-overlay `placement_region=top_edge` metadata.
  Use actual geometry for auditing and preserve the presentation-package
  interpretation; do not silently rewrite frozen images or metadata after
  model outputs are observed.
- **Runtime decision:** Other VLM training/inference processes may remain active
  when capacity permits. The ablation runner only warns about them, uses a
  separate port, checks model-specific peak plus a 64 GiB reserve before every
  load, and never stops an unrelated process or downloads a model.
- **Paper impact:** Methods must define the paired cohorts, factor isolation,
  bundled-style caveat, precision limits, and human-review dependency. Results
  must keep these ablations secondary and model-specific.
- **Evidence:** [`configs/v3/ablation_protocol.yaml`](../configs/v3/ablation_protocol.yaml),
  [`reports/v3/ablation_protocol/dataset_audit.md`](../reports/v3/ablation_protocol/dataset_audit.md),
  [`reports/v3/ablation_protocol/ram_readiness.md`](../reports/v3/ablation_protocol/ram_readiness.md),
  [Wang et al., NAACL 2025](https://aclanthology.org/2025.naacl-long.626/),
  [SceneTAP, CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/papers/Cao_SceneTAP_Scene-Coherent_Typographic_Adversarial_Planner_against_Vision-Language_Models_in_Real-World_CVPR_2025_paper.pdf),
  and [Balakrishnan et al. 2026](https://arxiv.org/abs/2604.12371) as concurrent
  preprint evidence.

### D018 - Remove deployment and clean pass/fail thresholds from the manuscript

- **Status:** ACCEPTED AFTER COMPLETION OF THE FIVE-MODEL MATRIX; REPORTING AMENDMENT
- **Date:** 2026-08-26
- **Decision:** The manuscript will report clean parse rate, accuracy, macro-F1,
  ordinal MAE, confusion matrices, and per-class recall as continuous descriptive
  measurements. It will not label models as deployment-ready, qualified, failed,
  or passed, and it will not display the former 60%/55% development or 70%/65%
  main thresholds as current criteria.
- **Reason:** The thresholds were investigator-defined routing and caution rules,
  not externally validated operating points for CrisisMMD deployment. No model
  was blocked from the fixed attack matrix, and the paper's primary estimand is
  the paired downward effect among each model's clean-correct mild/severe cases.
  Keeping a pass/fail label would add an unsupported operational interpretation
  without changing that estimand.
- **Post-result amendment disclosure:** This change was made after all five
  paper-panel results were available. It changes manuscript framing only; it
  does not alter the frozen main cohort, prompt, payloads, predictions, eligible
  denominators, statistical tests, or any attack effect. Historical gate JSONs
  and numeric thresholds remain in the repository for auditability.
- **Caveat:** Low clean competence remains a central limitation. The paper must
  report the 50.28%-55.69% balanced-main accuracy range and must describe all
  robustness estimates as conditional rather than operational.
- **Paper impact:** Replace every gate/pass/fail figure, column, and sentence
  with clean-characterization metrics and exact eligible denominators.
- **Supersedes:** Threshold/pass-fail portions of D001, D004, D005, and D012.
- **Evidence:** [`reports/v3/ALL_RESULTS.md`](../reports/v3/ALL_RESULTS.md),
  [`reports/v3/final_analysis/`](../reports/v3/final_analysis/).

### D019 - Final paper model panel is four BF16 open VLMs plus Gemini

- **Status:** ACCEPTED AFTER COMPLETION; SCOPE CONSOLIDATION
- **Date:** 2026-08-26
- **Decision:** The paper-facing panel is Qwen3.5 27B BF16, Qwen3.6 27B BF16,
  Qwen3-VL 32B BF16, Mistral Small 3.1 24B BF16, and Gemini 2.5 Flash. Include a
  model only if the full main matrix, natural clean, official-test clean,
  presentation-style, and size outputs are complete. Historical 8-bit, 4-bit,
  V2, and Qwen 9B outputs are excluded from the primary paper tables.
- **Reason:** This rule yields the complete common experiment matrix requested
  for the manuscript, aligns the open-model panel at BF16, adds one hosted model,
  and does not select models by observed attack effect.
- **Caveat:** Gemini's internal precision is provider-managed, model families and
  architectures differ, and Qwen3.6 was originally optional. Cross-model
  comparisons are descriptive; no scale, family, or precision effect is causal.
- **Paper impact:** Present all five models separately and never pool their
  predictions as independent observations.
- **Supersedes:** D009, D013, and the model-panel clauses of D017.
- **Evidence:** [`reports/v3/ALL_RESULTS.md`](../reports/v3/ALL_RESULTS.md).

### D020 - Canonical open-model results use the common A100/vLLM runtime

- **Status:** ACCEPTED AFTER COMPLETION; EXECUTION AMENDMENT
- **Date:** 2026-08-27
- **Decision:** Use the completed GCP A100/CUDA-vLLM runs as the canonical
  paper-facing outputs for all four open models. Gemini remains a hosted Batch
  API model. Retain local MLX-VLM repeats as noncanonical audit evidence, but do
  not mix their predictions or percentages into primary tables.
- **Reason:** The repeated Qwen3.5 and Qwen3.6 A100 runs complete a common open-
  model execution family while preserving the frozen prompt, input records,
  decoding targets, parsing, and analysis. Runtime remains an execution choice,
  not a research factor.
- **Caveat:** Gemini remains a separate hosted service, and checkpoint/runtime
  preprocessing can still differ across model families. Architecture or runtime
  therefore cannot be assigned as the cause of cross-model effect differences.
- **Paper impact:** Put A100/vLLM and Gemini provenance in the reproducibility
  table, use only A100 percentages for the four open models, and keep runtime
  claims out of the findings.
- **Supersedes:** The MLX-only scope of D010 and runtime clauses of D017.
- **Evidence:** Model-level resolved configs and locks linked from
  [`reports/v3/ALL_RESULTS.md`](../reports/v3/ALL_RESULTS.md).

### D021 - Retire the unrun P7 prompt sensitivity from required paper scope

- **Status:** ACCEPTED AFTER COMPLETION; DOCUMENTED PROTOCOL DEVIATION
- **Date:** 2026-08-26
- **Decision:** Do not run or present the 90-sample P7 modality-neutral prompt
  sensitivity as part of the final paper. Retain its config and D014 as a record
  of the predeclared secondary analysis.
- **Reason:** V4/P5 remained unchanged across the complete five-model matrix,
  and P7 was never part of the primary estimand. Adding a small prompt comparison
  after inspecting the completed outcomes would increase researcher degrees of
  freedom without changing the fixed main result.
- **Caveat:** The paper must disclose that this secondary sensitivity was
  predeclared but not executed. Prompt dependence therefore remains a limitation.
- **Paper impact:** Remove P7 from the submission checklist and add one sentence
  to protocol deviations/limitations; do not claim prompt invariance.
- **Supersedes:** D014.
- **Evidence:** [`configs/prompts/p7_modality_neutral_sensitivity.yaml`](../configs/prompts/p7_modality_neutral_sensitivity.yaml),
  [`reports/v3/ALL_RESULTS.md`](../reports/v3/ALL_RESULTS.md).

### D022 - Report clean-aware full-cohort directional effects and transition matrices

- **Status:** ACCEPTED AFTER SUPERVISOR FEEDBACK; REPORTING AMENDMENT
- **Date:** 2026-08-28
- **Decision:** Use downward successes divided by all 720 main samples as the
  headline attack percentage. Report the modality-matched benign-adjusted
  full-cohort contrast as `(malicious successes - benign successes) / 720`.
  Retain eligible-only downward ASR as a conditional susceptibility measure.
  Add symmetric upward-shift outcomes and replace mean severity drop in the
  main presentation with row-normalized clean-to-attacked transition matrices.
  Show the unweighted mean of model-level row percentages in the main text and
  retain model-specific count matrices for the appendix.
- **Reason:** The full-cohort rate incorporates clean competence into the
  displayed population effect, while the conditional rate still identifies
  attack susceptibility after a correct actionable decision. Transition
  matrices communicate both direction and magnitude more directly than one
  signed mean.
- **Clarification:** Benign behavior is a matched control baseline, not a
  standard deviation. It is not multiplied by clean accuracy after subtraction;
  clean correctness is already encoded in both full-cohort success indicators.
- **Caveat:** The five-model mean matrix is descriptive and does not pool model
  predictions as independent observations. Qwen3.8 is an additional
  same-protocol model and remains pending until main, style, size, natural, and
  official outputs are complete.
- **Paper impact:** Lead with full-cohort downward and benign-adjusted effects;
  label eligible-only ASR as conditional; report upward shifts; place
  model-specific clean and attack transition matrices in the appendix.
- **Evidence:** [`reports/v3/ALL_RESULTS.md`](../reports/v3/ALL_RESULTS.md),
  `reports/v3/gcp_a100/models/*/main/{attack_metrics,benign_adjusted_effects,clean_confusion_matrix,severity_shift_matrix}.csv`.

### D023 - Freeze supervisor-requested rhetoric, point-size, and disaster-type follow-ups

- **Status:** ACCEPTED; SECONDARY FOLLOW-UP PROTOCOL FROZEN BEFORE MODEL RESPONSES WERE INSPECTED
- **Date:** 2026-08-28
- **Decision:** Preserve the completed canonical main/style/relative-size matrix.
  Add two separate secondary paired experiments on existing globally disjoint
  cohorts: (1) a 120-source text-rhetoric experiment with exact-label direct,
  natural-language direct, plain misleading, authority-framed misleading, and
  four matched benign controls; and (2) a 60-source point-size response with
  benign/direct/misleading overlays at nominal 3, 6, 9, 12, and 15 pt. Run the
  follow-ups for Qwen3.5 27B, Qwen3.6 27B, Qwen3.8 27B, Qwen3-VL 32B, and
  Mistral 24B BF16 on separate A100 80GB instances. Add disaster-type
  post-analysis for the completed main predictions without new inference.
- **Semantic rule:** Direct payloads are imperative requests to ignore/override
  evidence and produce a low-damage output. Misleading payloads are declarative
  false low-damage scene claims without a model-directed command. Because the
  direct message is embedded in external image/tweet content, its delivery is
  indirect prompt injection even though its payload semantics are direct.
- **Point-size rule:** D017's completed canonical size experiment remains a
  relative-height comparison at 3%, 5%, and 8%. The new experiment uses nominal
  points under a frozen 72-PPI raster convention, so 3/6/9/12/15 pt map to the
  same pixel counts. Report nominal pt, realized px, relative height, line count,
  and occupied area. Do not describe the units as device-independent physical
  size. The 15-pt endpoint follows the five-level 3-15 px typography grid in
  Cheng et al. (ECCV 2024); 18-27 pt were rejected after frozen pre-rendering
  showed 53%-100% occupied area on the smallest source image.
- **Analysis:** Retain clean-aware full-cohort downward and upward rates,
  conditional eligible rates, matched-benign paired risk differences, 5,000
  paired bootstrap draws, exact McNemar/Holm tests, signed severity shift, and
  clean-to-attacked transition matrices. Plot point-size response but do not
  infer monotonicity from an aggregate line alone.
- **Disaster-type caveat:** Group the main split descriptively into wildfire,
  hurricane, earthquake, and flood, with per-model and unweighted model-mean
  rates. Do not call differences causal disaster-type effects because event and
  class are confounded and group sizes range from 29 to 559.
- **Paper impact:** Keep these results secondary and label them post-review.
  Qwen3.8 enters no completed aggregate table until all requested outputs pass
  completeness checks. The original canonical results remain valid regardless
  of follow-up outcome.
- **Evidence:** [`configs/v3/followup_ablation_protocol.yaml`](../configs/v3/followup_ablation_protocol.yaml),
  [`src/v3_followup_ablations.py`](../src/v3_followup_ablations.py),
  [`reports/v3/ALL_RESULTS.md`](../reports/v3/ALL_RESULTS.md),
  [Cheng et al., ECCV 2024](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/07650.pdf),
  [SceneTAP, CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/html/Cao_SceneTAP_Scene-Coherent_Typographic_Adversarial_Planner_against_Vision-Language_Models_in_Real-World_CVPR_2025_paper.html),
  [Words or Vision, CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/html/Deng_Words_or_Vision_Do_Vision-Language_Models_Have_Blind_Faith_in_CVPR_2025_paper.html),
  and [InjecAgent, ACL 2024](https://aclanthology.org/2024.findings-acl.624/).

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

| Paper model | Precision | Main clean accuracy / macro-F1 | Eligible mild+severe n | Complete paper matrix |
|---|---|---:|---:|---|
| Qwen3.5 27B | BF16 | 0.5569 / 0.5494 | 245 | Yes |
| Qwen3.6 27B | BF16 | 0.5389 / 0.5317 | 245 | Yes |
| Qwen3-VL 32B | BF16 | 0.5319 / 0.5298 | 294 | Yes |
| Mistral Small 3.1 24B | BF16 | 0.5028 / 0.4857 | 232 | Yes |
| Gemini 2.5 Flash | provider-managed | 0.5458 / 0.5485 | 273 | Yes |

The canonical interpretation, complete result tables, dataset construction, and
paper-writing guidance are in
[`reports/v3/ALL_RESULTS.md`](../reports/v3/ALL_RESULTS.md). Historical 8-bit,
4-bit, V2, and 9B outputs remain available but are outside the paper panel.

## Paper synchronization debt

The methodology predates the completed matrix. Synchronize `paper.md` from the
canonical paper-writing reference before submission:

- replace final model and result placeholders only from saved canonical run artifacts;
- insert completed presentation-style and size results with exact denominators;
- remove deployment/pass/fail threshold language under D018;
- disclose the unrun P7 sensitivity under D021 rather than presenting prompt invariance;
- complete the blinded visual review before final perceptual claims;
- leave V2 and Qwen 9B findings explicitly historical/exploratory.

This decision log and executable YAML remain authoritative if a future result
edit introduces a conflict with the paper blueprint.

## Resolved and open decisions

### RESOLVED-001 - Canonical main clean and attack outcomes

**Resolved 2026-08-26.** The five-model panel has complete main clean and fixed
attack matrices. D018 changes reporting language only; prompt, payloads,
exclusions, predictions, and metric denominators remain unchanged.

### OPEN-002 - Human visual review

Freeze reviewer sampling/full-review scope, collect at least two blinded
ratings per unique modified image, and select the agreement statistic before
final robustness claims.

### OPEN-003 - Related-work verification

Complete a primary-source literature table separating zero-shot generative
VLMs, supervised VLM/CLIP classifiers, caption-augmentation pipelines, data
splits, class distributions, and reported metrics.

### RESOLVED-004 - Secondary natural and official clean outcomes

**Resolved 2026-08-26.** Natural-3,474 and official-test-529 clean outputs exist
for all five paper models. The two formerly empty GCP label-conflict sensitivity
tables were regenerated locally from saved predictions without new inference.

### OPEN-005 - Paper protocol synchronization

Resolve every item in `Paper synchronization debt` and date the resulting
`paper.md` snapshot before pushing a manuscript-facing release.

### RESOLVED-006 - Ablation outcomes; visual validation remains OPEN-002

**Resolved for inference 2026-08-26.** Presentation-style and size outputs and
paired analyses exist for all five paper models. Blinded readability,
plausibility, and critical-damage-occlusion review remains OPEN-002 and bounds
perceptual claims.

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
