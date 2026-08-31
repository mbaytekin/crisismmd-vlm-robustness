# Paper decision log

Last updated: 2026-08-31

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
| Prompt | Fixed zero-shot damage-assessment rubric; internal development labels are not paper-facing |
| Prompt hash | `1fa1a4a2b61c4aaadb95215385cd97915fd515ca4b19fc477ba98291cdf39ee6` |
| Prompt development evidence | 180 examples, balanced 60 per class; post-hoc routing/history only, not a model gate |
| Main clean evaluation | Frozen 720-example main split, balanced 240 per class; descriptive clean characterization |
| Secondary clean evaluation | All 3,474 exact-SHA-unique valid rows plus the published 529-row test split |
| Dataset interpretation | Main-720 is a custom balanced paired cohort; official-529 is natural but secondary/post-hoc |
| Clean-performance interpretation | Report parse rate, accuracy, macro-F1, ordinal MAE, and per-class recall without a pass/fail or deployment threshold |
| Robustness denominator | Predeclared clean-correct mild/severe decisions for each model |
| Attack eligibility | The fixed six-model paper panel is analyzed separately; lower clean competence narrows interpretation rather than invalidating paired estimates |
| Decoding | Temperature 0, top-p 1, seed 42, max 150 tokens, thinking disabled |
| Runtime | Canonical open-model outputs use GCP A100/CUDA-vLLM; Gemini uses its hosted Batch API; MLX repeats are noncanonical audit evidence |
| Paper panel | Qwen3.5 27B BF16, Qwen3.6 27B BF16, Qwen3.8 27B BF16, Qwen3-VL 32B BF16, Mistral Small 3.1 24B BF16, Gemini 2.5 Flash |
| Precision | Five open checkpoints use BF16; Gemini is a hosted model with provider-managed precision |
| Primary safety focus | Downward severity shifts and induced under-triage |
| Venue | NeurIPS 2026 Trustworthy AI for Good (AI4GOOD) workshop; anonymous `dblblindworkshop` style; checklist not required |
| Paper figures | Illustrative generated overlays in the PDF only; no perceptual/realism claim; raw overlays stay private |

Executable sources:

- [`configs/v3/models.yaml`](../configs/v3/models.yaml)
- [`configs/v3/final_analysis_protocol.yaml`](../configs/v3/final_analysis_protocol.yaml)
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
- **Evidence:** the exact prompt reproduced in the manuscript appendix and its
  content hash in [`reports/v3/artifact_lock.json`](../reports/v3/artifact_lock.json).

### D003 - Frozen production prompt

- **Status:** ACCEPTED FOR THE FIXED PROMPT TEXT; INTERNAL CANDIDATE/VERSION NAMES ELIMINATED FROM PAPER-FACING SCOPE BY D029
- **Date:** 2026-08-11
- **Decision:** Use the selected zero-shot damage-assessment rubric for
  production inference. Do not modify its text after lock.
- **Reason:** On the independent 180-example development split, the selected
  zero-shot candidate exceeded the few-shot candidate in accuracy, macro-F1,
  mild recall, severe recall, and latency. The paired
  accuracy difference was small and not statistically distinguishable from
  zero, so few-shot examples had no supported primary benefit.
- **Paper impact:** Reproduce the fixed rubric and summarize the clean
  development comparison without internal candidate or version labels.
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
- **Caveat:** The selected rubric was chosen on this split using Qwen3.5 27B,
  so that model's
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

### D014 - Alternative-prompt sensitivity proposal

- **Status:** ELIMINATED FROM THE STUDY AND PAPER-FACING SCOPE; DO NOT RUN, CITE, OR DISCUSS
- **Date:** 2026-08-12
- **Decision:** This abandoned proposal is not part of the completed study.
- **Paper impact:** None. The manuscript states only the supported limitation:
  the attack matrix was evaluated with one fixed prompt, so prompt dependence
  remains unknown.

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
- **Versioning rule:** Any replacement sample design must be introduced as a
  new, separately frozen cohort version,
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

- **Status:** ACCEPTED AFTER COMPLETION OF THE ORIGINAL MATRIX; REPORTING AMENDMENT (CURRENT SIX-MODEL SCOPE IS D024/D028)
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

### D019 - Historical initial paper model panel

- **Status:** SUPERSEDED BY D024; HISTORICAL INITIAL PANEL (ELIMINATED FROM CURRENT PAPER SCOPE)
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
- **Paper impact (historical):** Present the then-selected models separately and never pool their
  predictions as independent observations.
- **Supersedes:** D009, D013, and the model-panel clauses of D017.
- **Evidence:** [`reports/v3/ALL_RESULTS.md`](../reports/v3/ALL_RESULTS.md).

### D020 - Canonical open-model results use the common A100/vLLM runtime

- **Status:** ACCEPTED AFTER COMPLETION; EXECUTION AMENDMENT (CURRENT FIVE-OPEN-MODEL RUNTIME SCOPE)
- **Date:** 2026-08-27
- **Decision:** Use the completed GCP A100/CUDA-vLLM runs as the canonical
  paper-facing outputs for the five open models. Gemini remains a hosted Batch
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
  table, use only A100 percentages for the five open models, and keep runtime
  claims out of the findings.
- **Supersedes:** The MLX-only scope of D010 and runtime clauses of D017.
- **Evidence:** Model-level resolved configs and locks linked from
  [`reports/v3/ALL_RESULTS.md`](../reports/v3/ALL_RESULTS.md).

### D021 - Remove the abandoned prompt sensitivity from required scope

- **Status:** SUPERSEDED BY D029; ELIMINATED FROM PAPER-FACING SCOPE
- **Date:** 2026-08-26
- **Decision:** Do not run or present the abandoned alternative-prompt
  sensitivity. It was never part of the primary estimand.
- **Reason:** Adding a small comparison after inspecting the completed outcomes
  would increase researcher degrees of freedom without changing the fixed main
  result.
- **Paper impact:** Do not narrate abandoned internal prompt candidates. Keep
  only the general limitation that the attack matrix used one fixed prompt and
  therefore does not establish prompt invariance.
- **Supersedes:** D014.
- **Evidence:** Historical prompt-validation artifacts retained for audit; no
  alternative prompt is part of the current paper scope.

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
- **Caveat:** Model-mean matrices are descriptive and do not pool model
  predictions as independent observations. The initial panel and later extension
  remain distinguishable in audit history even though the current reader-facing
  panel contains all six models.
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
  Before D024, Qwen3.8 entered no completed aggregate table until all
  requested outputs passed completeness checks. D024 records that condition as
  satisfied; the original canonical results remain valid regardless of the
  extension outcome.
- **Evidence:** [`configs/v3/followup_ablation_protocol.yaml`](../configs/v3/followup_ablation_protocol.yaml),
  [`src/v3_followup_ablations.py`](../src/v3_followup_ablations.py),
  [`reports/v3/ALL_RESULTS.md`](../reports/v3/ALL_RESULTS.md),
  [Cheng et al., ECCV 2024](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/07650.pdf),
  [SceneTAP, CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/html/Cao_SceneTAP_Scene-Coherent_Typographic_Adversarial_Planner_against_Vision-Language_Models_in_Real-World_CVPR_2025_paper.html),
  [Words or Vision, CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/html/Deng_Words_or_Vision_Do_Vision-Language_Models_Have_Blind_Faith_in_CVPR_2025_paper.html),
  and [InjecAgent, ACL 2024](https://aclanthology.org/2024.findings-acl.624/).

### D024 - Incorporate the validated Qwen3.8 extension and completed follow-ups

- **Status:** ACCEPTED AFTER COMPLETENESS VALIDATION; REPORTING UPDATE
- **Date:** 2026-08-29
- **Decision:** Add Qwen3.8 27B BF16 to the current paper-facing model panel and
  incorporate the completed open-model text-rhetoric and point-size analyses as
  secondary post-review evidence. Preserve the initial completion point and
  D023's pre-outcome freeze in the audit trail.
- **Completeness evidence:** Qwen3.8 has 7,200 main, 1,200 presentation-style,
  600 relative-size, 3,474 natural-clean, 529 official-clean, 1,080
  text-rhetoric, and 960 point-size parsed predictions (13,003 total). Each of
  the other open models has 1,080 text-rhetoric and 960 point-size parsed
  predictions. Validation found the exact expected rows and unique
  source-condition pairs, one prompt hash per file, the expected model identity,
  no parse failures, and no recorded inference errors.
- **Result:** Qwen3.8 has 52.78% balanced-main clean accuracy and 249 eligible
  mild/severe decisions. Its six full-cohort malicious-minus-benign downward
  effects are +6.53, +4.17, +13.33, +4.31, +3.33, and +5.56 percentage points;
  all six are Holm-significant. The current six-model main result is therefore
  36/36 positive Holm-significant matched-control effects.
- **Follow-up interpretation (superseded by D028):** The earlier open-only
  contrast counts are historical and are not the current reader-facing summary.
  D028 replaces them with unified six-model follow-up families. Point-size model
  means remain descriptive and do not establish a universal monotonic law.
- **Caveat:** The follow-ups were prompted by review and remain secondary. The
  initial Qwen3.8 all-in-one attempt stopped after 611 rows; only the complete
  successful split reruns enter analysis. Human visual review remains open and
  still bounds readability, plausibility, camouflage, and non-occlusion claims.
- **Paper impact:** Update current model and aggregate tables to six models;
  add separate text-rhetoric and point-size tables; retain exact denominators,
  paired tests, and the original amendment chronology.
- **Supersedes:** D019 and D020 only for the current model-panel count; resolves
  the completion conditions in D022 and D023 without changing their estimands.
- **Evidence:** [`reports/v3/ALL_RESULTS.md`](../reports/v3/ALL_RESULTS.md),
  [`reports/v3/gcp_a100/models/qwen38_27b_bf16/`](../reports/v3/gcp_a100/models/qwen38_27b_bf16/),
  and `reports/v3/gcp_a100/models/*/followups/`.

### D025 - AI4GOOD workshop venue, readable presentation, and illustrative overlays

- **Status:** ACCEPTED
- **Date:** 2026-08-30
- **Decision:** Submit the current manuscript to the NeurIPS 2026 Trustworthy
  AI for Good (AI4GOOD) workshop using official workshop mode
  (`dblblindworkshop` + `\workshoptitle{Trustworthy AI for Good}`). The NeurIPS
  paper checklist is not required and is not compiled into the PDF. Keep the
  six-model evidence, full-cohort `n/720` primary estimand, and all D018--D024
  claim bounds. Prefer reader-facing presentation over protocol density:
  move cohort-construction accounting, official-test leakage, Wilson
  half-widths, and formal estimand equations to the appendix; keep the main
  Method to the threat, the 720/120/60 roles, the three payload families, and
  the matched-control idea. Include a small number of generated overlay
  examples in the paper PDF so the attack is visible: a main-text California
  wildfire benign/direct/misleading triplet, plus appendix style and relative-
  size variants. Keep `reports/private/visual_examples/` private. Do not put
  raw CrisisMMD tweets, clean source dumps, or the private overlay directory
  into a public/anonymous archive.
- **Reason:** The workshop page states 2--9 pages of main content, references
  and appendices excluded, and no checklist. Reviewers cannot interpret
  typographic attacks from tables alone. The selected California triplet has
  no prominent commercial logo and shows a source on which Qwen3.6 and
  Qwen3.8 move from `severe_damage` to `little_or_no_damage` under the direct
  overlay. Style/size panels remain secondary illustrations, not stealth
  evidence.
- **Caveat:** OPEN-002 human visual review is still incomplete. Figure captions
  must say the overlays are generated examples and must not claim realism,
  stealth, readability, plausibility, or non-occlusion. Identifiable buildings
  in CrisisMMD flood photos are dataset content, not an extra release of
  private user data, but they must not be treated as camera-ready stock.
- **Paper impact:** Keep `manuscript/main.tex` in workshop mode and do not
  input `checklist.tex`. Put the California overlay triplet in the main Method
  section and the style/size variants in the appendix. Keep Method short.
- **Supersedes:** None of D018--D024. Narrows only the submission venue and
  the allowed use of private overlay examples inside the anonymous PDF.
- **Evidence:** [`reports/private/visual_examples/README.md`](../reports/private/visual_examples/README.md),
  [`manuscript/figures/`](../manuscript/figures/),
  and the AI4GOOD 2026 workshop page (2--9 pages; checklist not required).

### D026 - Relative 3/5/8% size is investigator-chosen; point-size stays appendix-only

- **Status:** ACCEPTED
- **Date:** 2026-08-30
- **Decision:** Keep D017's 3%/5%/8% of image height as the canonical size
  experiment. Do not claim those percentages are a literature standard. Cite
  Cheng et al. (ECCV 2024) for size as a typographic factor and for the 3--15~px
  grid used in the secondary point-size follow-up. Cite Jenq and Shen
  (CIKM 2025 / arXiv:2511.05325) only as motivation that variable-resolution
  images call for a relative font scale rather than a fixed pixel size; their
  ratio is of the largest fitting overlay (25/50/75/100%), not of image height.
  Report the point-size follow-up in the appendix with a line plot of
  unweighted open-model means; the main-text size story remains relative
  height. Do not infer a second size law from the aggregate line.
- **Reason:** CrisisMMD resolutions vary; an absolute px/pt overlay is not
  comparable across frames. No published protocol uses 3/5/8% of image
  height.
- **Paper impact:** Method states the two citations and the investigator-chosen
  3/5/8% levels. Results mention relative size in the main text and point to
  Appendix Figure `fig:pointsize` for nominal pt. Add
  `jenq2025rendering` to `manuscript/references.bib`.
- **Supersedes:** None. Narrows only how size is cited and presented.
- **Evidence:** Cheng et al. ECCV 2024 (3--15 px); Jenq and Shen arXiv:2511.05325
  (font-size ratio of max-fit); [`reports/v3/ALL_RESULTS.md`](../reports/v3/ALL_RESULTS.md)
  unweighted point-size means 2.00/2.33/6.67/14.00/16.00 (direct) and
  1.67/3.00/6.33/7.67/7.67 (misleading).

### D027 - Pre-declare Gemini completion of the two missing follow-ups

- **Status:** ACCEPTED BEFORE GEMINI FOLLOW-UP RESPONSES ARE INSPECTED; REPORTING CLAUSE SUPERSEDED BY D028
- **Date:** 2026-08-30
- **Decision:** Complete Gemini 2.5 Flash on the two supervisor follow-ups that
  currently exist only for the five open BF16 models: text-rhetoric
  (`text_rhetoric_ablation`, 120 sources × 9 conditions = 1,080) and point-size
  (`size_response_pt`, 60 sources × 16 conditions = 960). Use the frozen
  manifests, frozen zero-shot prompt, temperature 0, thinking budget 0, and the
  existing Gemini Batch/sharded pipeline. Do not re-run main, style, relative
  size, natural-clean, or official-test. Do not start GCP VMs. Include every
  completed Gemini follow-up row in the appendix regardless of sign, magnitude,
  or Holm outcome. Do not drop Gemini if the curve is ugly. Do not promote
  point-size over D017's relative 3%/5%/8% height experiment. Do not rewrite
  preserve the already-completed open-model follow-up analyses. After both files
  parse completely, add a Gemini row to the appendix tables and recompute the
  unweighted appendix mean over the six models that then have complete files.
- **Reason:** The six-model paper panel is already complete on the canonical
  matrix. The follow-ups were frozen for open models only (D023). Completing
  Gemini now is a hosted-panel extension of already-frozen manifests, not a
  new size law and not a reason to reopen the 720-source matrix.
- **Caveat:** This extension is decided after the initial open-model follow-up
  outcomes were known. That is why the earlier audit family remains historical;
  the current paper uses D028's unified six-model summary. Human visual review remains
  OPEN-002.
- **Paper impact:** Do not edit appendix numbers until both Gemini JSONL files
  exist, parse 1,080 and 960 rows, and pass the same completeness checks used in
  D024. Relative-height size remains the canonical size story.
- **Supersedes:** None of D023--D026. Narrows only Gemini's missing follow-up
  coverage.
- **Evidence:** [`configs/v3/followup_ablation_protocol.yaml`](../configs/v3/followup_ablation_protocol.yaml),
  `data/v3/manifests/text_rhetoric_ablation_conditions.csv`,
  `data/v3/manifests/size_response_pt_conditions.csv`,
  [`scripts/gemini_v3_batch.py`](../scripts/gemini_v3_batch.py),
  and [`docs/CODEX_GEMINI_FOLLOWUPS.md`](CODEX_GEMINI_FOLLOWUPS.md).

### D028 - Incorporate the complete Gemini follow-ups in unified six-model reporting

- **Status:** ACCEPTED AFTER COMPLETENESS VALIDATION; REPORTING UPDATE
- **Date:** 2026-08-30
- **Decision:** Incorporate Gemini 2.5 Flash into the same reader-facing
  text-rhetoric and point-size tables as the five open BF16 models. Report the
  six-model summaries as 0/18 Holm-significant within-model rhetoric contrasts
  and 0/48 Holm-significant within-model adjacent point-size contrasts. Use
  unweighted six-model means in both appendix tables and the point-size figure.
- **Completeness evidence:** Gemini has 1,080/1,080 parsed text-rhetoric rows
  and 960/960 parsed point-size rows, exact unique source-condition coverage,
  one prompt hash per file, the expected `gemini-2.5-flash` identity, and no
  recorded request errors. The frozen manifests, zero-shot prompt, temperature zero,
  and thinking budget zero were used.
- **Result:** Gemini full-cohort rhetoric rates are 1.67%, 3.33%, 3.33%, and
  4.17%; none of its three within-model rhetoric contrasts is Holm-significant.
  Its direct point-size rates are 0.00%, 1.67%, 1.67%, 1.67%, and 1.67%, and
  its misleading rates are 0.00%, 1.67%, 3.33%, 5.00%, and 3.33%; none of its
  eight adjacent-size contrasts is Holm-significant.
- **Paper impact:** Present unified six-model tables and aggregate counts without
  protocol-history narration in the manuscript. Keep point-size secondary and
  appendix-only; the canonical size result remains relative 3%/5%/8% of image
  height. Do not alter the 36/36 main matched-control result.
- **Supersedes:** D027 only for the reader-facing instruction to keep Gemini's
  contrast counts separate. The D027 execution freeze and audit history remain
  unchanged.
- **Evidence:**
  `results/v3/gemini_batch/gemini-2.5-flash/followups-d027-20260830/`,
  `reports/v3/final_analysis/models/gemini_2_5_flash/followups/`, and
  [`reports/v3/ALL_RESULTS.md`](../reports/v3/ALL_RESULTS.md).

### D029 - Remove internal prompt-development labels from paper-facing use

- **Status:** ACCEPTED; CURRENT
- **Date:** 2026-08-30
- **Decision:** The paper and all writing handoffs describe one fixed zero-shot
  damage-assessment rubric without internal candidate, phase, or version names.
  The abandoned alternative-prompt proposal is eliminated from the study and
  must not be run, presented, or discussed in the manuscript. Prompt dependence
  remains a limitation because only one fixed prompt was used for the attack
  matrix.
- **Eliminated decisions:** D014 and D021 are eliminated from paper-facing
  scope. D003 remains active only for the selected prompt text and immutable
  content hash; its internal naming history is eliminated. D003-H1 and the
  prompt-labelled rows in D004-H1 are historical implementation records and
  must not be supplied to a writing model.
- **Reproducibility boundary:** Immutable run metadata and executable filenames
  may retain historical identifiers. They are audit artifacts, not manuscript
  content, and must not be rewritten because doing so would falsify provenance.
- **Paper impact:** No protocol-deviation narrative about abandoned prompt
  candidates. Retain the neutral sentence that the full attack matrix was not
  repeated under another prompt and therefore prompt dependence is unresolved.
- **Supersedes:** D014 and D021 for all reader-facing and writing-handoff use;
  narrows D003 to the fixed prompt text.

### D030 - Reviewer-facing framing, figure encoding, and table-order audit

- **Status:** ACCEPTED; PRESENTATION AND FRAMING AMENDMENT
- **Date:** 2026-08-31
- **Decision:** Make three framing commitments explicit in the manuscript and
  re-encode the three generated figures. (1) The threat model states why such an
  adversary is plausible---open contributor access to crisis feeds and the
  incentive to understate damage---while explicitly declining to estimate attack
  prevalence. (2) The Introduction defends the conditional estimand directly:
  modest clean competence does not make the audit vacuous, because the primary
  rate counts only initially correct mild/severe decisions yet always divides by
  all 720 sources. (3) The Discussion states that no mitigation is evaluated by
  design, because a countermeasure chosen after these outcomes were visible would
  be tuned to the payloads, cohorts, and models it is meant to be tested against.
- **Figures:** `main_effects.pdf` now splits each bar at its modality-matched
  benign control, so the saturated segment is the paired effect of the
  risk-difference table, and prints the full-cohort value above each bar; both
  panels keep one shared axis. `transition_matrices.pdf` colours cells by
  direction---red below the diagonal for downward movement, grey on the diagonal,
  blue above---instead of by magnitude alone. `point_size_means.pdf` plots the six
  individual model traces behind the unweighted mean, so the flat Gemini trace and
  the steep Qwen3-VL trace bound the aggregate rise on the figure itself.
- **Corrections found in the audit:** the secondary-clean sentence in Results read
  "Six models obtain 54.8--56.8% natural accuracy, whereas Mistral falls to
  36.56%", which is self-contradictory because Mistral is one of the six; it now
  reads "Five of the six models". Seven appendix tables carried Qwen3.8 or Mistral
  in a legacy extension position and were reordered to the canonical panel order
  used everywhere else. One cross-reference rendered as "Appendix 11" while
  pointing at a table and now reads "appendix Table 11".
- **Verified unchanged:** every value in the main and appendix tables was
  re-checked against `reports/v3/ALL_RESULTS.md` and matches, including main
  full-cohort rates, conditional ASR with Wilson intervals, matched-benign risk
  differences, per-class recall, upward-shift rates, severe/critical under-triage,
  style, relative size, rhetoric, and point size. No estimand, denominator,
  statistic, or result changed.
- **Caveat:** These are presentation and framing changes made after the results
  were known. They add no new evidence, and OPEN-002 human visual review remains
  incomplete.
- **Paper impact:** Method threat model, Introduction, Discussion RQ5, Results
  secondary paragraph, three figure captions, and appendix table order. Prose
  elsewhere was tightened only to hold the nine-page limit; the compiled draft
  ends the main content on page 9 with references on page 10.
- **Supersedes:** None.
- **Evidence:** [`scripts/make_paper_figure.py`](../scripts/make_paper_figure.py),
  `manuscript/figures/`, and [`reports/v3/ALL_RESULTS.md`](../reports/v3/ALL_RESULTS.md).

### D031 - Denominator worked example, ablation design map, and hedge deduplication

- **Status:** ACCEPTED; PRESENTATION AMENDMENT
- **Date:** 2026-08-31
- **Decision:** Six reader-facing clarifications, none of which changes an
  estimand, denominator, statistic, or result. (1) Results carries one worked
  denominator case: Qwen3.5 has 245 eligible decisions, 107 move lower under
  direct image delivery, so the primary rate is 107/720 = 14.86% and the
  conditional rate is 107/245 = 43.67%. (2) The corrected-test counts are
  decomposed in text: 0/18 is six models x three rhetoric contrasts, and 0/48 is
  six models x two payload families x four adjacent point-size contrasts.
  (3) Results states that relative overlay height is the canonical size
  experiment and nominal point size is an appendix check on the same 60 sources,
  not a competing result. (4) Appendix Table `tab:ablation_map` maps all four
  secondary families by manipulated factor, held-fixed factors, cohort and
  eligible n, and outcome. (5) Results section 4.5 is split into a competence-context
  subsection and a secondary-ablations subsection, because natural/official clean
  and event-stratified results are not ablations; the event-stratified paragraph
  now reports 86.67% mean earthquake and 33.91% mean flood clean accuracy, the
  hurricane conditional maximum, and the 2--12 eligible-case floor, with the
  confounding stated. (6) Repeated hedging was deduplicated.
- **Hedge rule applied:** reduce repetition, never coverage. Each claim boundary
  keeps at least one statement at its strongest location; only second and third
  copies were removed. Verified present after the edit: modest competence and
  non-operational status, no style or size effect holding across models, bundled
  presentation contrast, incomplete human review, architecture confounding,
  event/class confounding, no prevalence estimate, unresolved prompt dependence,
  no evaluated defense, attacked-accuracy supplementarity, and small ablation
  denominators.
- **Caveat:** Presentation only, made after results were known. OPEN-002 human
  visual review remains incomplete.
- **Paper impact:** Abstract, Introduction, Related work, Method 3.3 and 3.5,
  Results 4.1/4.4/4.5, Discussion RQ1 and RQ4, Conclusion, and one new appendix
  table. The compiled draft still ends the main content on page 9 with references
  on page 10, no overfull boxes and no undefined references.
- **Supersedes:** None.
- **Evidence:** `manuscript/sections/`, [`reports/v3/ALL_RESULTS.md`](../reports/v3/ALL_RESULTS.md).

### D032 - Human-review instrument: field set completed and capture tooling built

- **Status:** ACCEPTED BEFORE ANY RATING IS COLLECTED
- **Date:** 2026-08-31
- **Decision:** Keep the frozen 303-image scope of
  `reports/v3/manual_review/final_visual_review.csv` unchanged, and complete its
  rating field set to the eight fields the predeclared gates in
  `docs/HUMAN_EVALUATION.md` section 5 actually require:
  `original_label_still_valid`, `image_usable`, `text_readable`,
  `text_too_obvious`, `text_completely_invisible`, `critical_damage_obscured`,
  `layout_plausible`, `approve`. Capture runs through
  `reports/v3/manual_review/review_app.html`, generated by
  `scripts/build_human_review_app.py`; agreement is computed by
  `scripts/analyze_human_review.py`.
- **Reason:** The 303-row header carried six partly renamed fields and no
  `reviewer_id`, so `text_completely_invisible` and `text_too_obvious` -- both
  required by the section 5.2 claim gates -- could not have been recorded. Zero
  ratings exist anywhere in the repository, so fixing the field list now changes
  no observation. The scope, the sampling, and the gates are untouched.
- **Instrument freeze:** From the first recorded rating onward the field list,
  the item list, and the gates are frozen. Any later change requires a new dated
  amendment and a separately labelled analysis.
- **Blinding:** The app never shows a model prediction, tweet text, or the
  ground-truth severity label; the label is not carried into the page at all.
  Item order is shuffled per `reviewer_id` so fatigue effects do not align
  across the two raters. Bulk-fill actions are deliberately absent.
- **AI pre-audit boundary:** `reports/v3/manual_review/AI_PREAUDIT.md` records an
  automated visual inspection. It is a coordinator diagnostic. It is not human
  validation, must not be transferred into the manuscript, must not fill
  `RESULTS_TEMPLATE.md`, and unlocks no perceptual claim. Human reviewers must
  stay blind to it until both independent passes are exported.
- **Caveat:** OPEN-002 remains open until two complete independent passes exist,
  the predeclared floor (raw agreement >= 80% and binary kappa >= 0.40 on
  `text_readable` and `critical_damage_obscured`) is evaluated, and every
  disagreement is adjudicated. Until then the manuscript keeps its current
  bounded wording and makes no readability, realism, stealth, plausibility, or
  non-occlusion claim.
- **Paper impact:** None yet. On completion the results enter the appendix and
  replace the incompleteness sentence in Limitations.
- **Supersedes:** None. Narrows only how OPEN-002 is executed.
- **Evidence:** [`docs/HUMAN_EVALUATION.md`](HUMAN_EVALUATION.md),
  `reports/v3/manual_review/PROTOCOL.md`,
  [`scripts/build_human_review_app.py`](../scripts/build_human_review_app.py),
  [`scripts/analyze_human_review.py`](../scripts/analyze_human_review.py).

### D033 - Pre-submission review pass: Holm families stated, framing narrowed

- **Status:** ACCEPTED; PRESENTATION AMENDMENT
- **Date:** 2026-08-31
- **Decision:** Five reader-facing corrections from an external review pass. None
  changes an estimand, denominator, statistic, or result.
  1. **Holm families are now stated in the paper.** Method says each family is one
     model, one outcome definition, and one analysis subset, so the 36 primary
     contrasts form six families of six tests rather than one family of 36. This
     matches the implementation: `src/v3_final_analysis.py` adjusts within
     `groupby(["subset", "metric"])` on each model's own result frame.
  2. **The Introduction no longer argues that a model at this accuracy would be
     deployed.** The sentence claiming such a system "can still be proposed as a
     triage aid" asserted a fact about deployment practice that this study does
     not evidence and that a reviewer could contest. It is replaced by the
     conditional question the paper actually answers: among the decisions a model
     initially gets right, can adversarial content induce safety-relevant downward
     errors? The motivation for why an adversary would bother stays in the threat
     model, where it is argued rather than assumed.
  3. **The overlay figure caption no longer reports model predictions on that
     source.** D025 records that the example was selected partly because two models
     moved from severe to little/no on it. Reporting an outcome for a case selected
     on that outcome, without disclosing the selection, invites a cherry-picking
     objection. The caption now describes construction only; the quantitative
     evidence is Figures 2 and 3.
  4. **The abstract's generalisation is narrowed** from "reproduces across
     off-the-shelf VLM disaster assessment" to "reproduces across all six evaluated
     VLMs". One dataset does not support the domain-level reading.
  5. **Appendix floats are barriered per section** using `placeins` with explicit
     `\FloatBarrier` calls. The `[section]` package option was tried first and
     rejected: it also barriers the main sections and pushed the main content to ten
     pages.
- **Caveat:** Presentation only, made after the results were known. OPEN-002 human
  visual review remains incomplete.
- **Paper impact:** Abstract, Introduction, Method 3.3 and 3.5, appendix float
  placement. Main content still ends on page 9 with references on page 10; the
  appendix gains one page, which is outside the workshop limit. No overfull boxes
  and no undefined references. Every claim boundary was re-verified as still present
  after the edits.
- **Supersedes:** None.
- **Evidence:** `src/v3_final_analysis.py` (Holm grouping),
  [`configs/v3/final_analysis_protocol.yaml`](../configs/v3/final_analysis_protocol.yaml),
  `manuscript/sections/`.

### D034 - Publish model revisions in the paper; withhold host identifiers

- **Status:** ACCEPTED
- **Date:** 2026-08-31
- **Decision:** Report the immutable Hugging Face repository revision for each of
  the five open checkpoints in the appendix model table, abbreviated to twelve
  hexadecimal characters, with the full values reserved for the artifact release.
  State plainly that Gemini 2.5 Flash exposes no equivalent revision, so its
  results are pinned only by model name and run window and could shift if the
  served model changes. Do **not** put the GCP cache host names from
  `docs/SHA.md` into the manuscript.
- **Reason:** A repository name such as `Qwen/Qwen3.5-27B` is mutable and does not
  identify the weights that were actually run; the revision does. This converts a
  reproducibility item the paper previously listed as outstanding into a resolved
  one, and it makes the open/hosted asymmetry visible rather than glossed.
- **Anonymity:** The host names recorded in `docs/SHA.md`
  (`can-crisismmd-*`) contain the author's given name and are a
  deanonymisation vector in a double-blind submission. They stay in the internal
  record only. The compiled PDF was checked and contains no host name or author
  string.
- **Caveat:** The revisions were read from the run caches on the already-running
  VMs rather than from a checked-out repository, and the per-run resolved
  configurations record `git_commit` as unavailable on the remote host. The
  environment lock and data-access instructions remain to be verified for the
  artifact release.
- **Paper impact:** Appendix Table `tab:models` gains the pinned revisions and a
  caption note; the reproducibility paragraph now states what is pinned and what
  is not. Main content still ends on page 9, no overfull boxes.
- **Supersedes:** None.
- **Evidence:** [`docs/SHA.md`](SHA.md), `reports/v3/artifact_lock.json`.

### D035 - Correct the single-factor over-claim in the secondary-ablation lead

- **Status:** ACCEPTED; CORRECTION
- **Date:** 2026-08-31
- **Decision:** The lead sentence of the secondary-ablation subsection claimed the
  four families "each vary one presentation or wording factor while holding the
  payload and cohort fixed". Two sentences later the same paragraph states that
  the three style renderers change contrast, background, occupied area, and
  placement together. The two statements contradict each other. The lead now
  reads: four secondary families probe presentation or wording factors on cohorts
  disjoint from the main 720 sources, and within each family everything except the
  named factor is held fixed, with the per-family detail carried by appendix
  Table `tab:ablation_map`.
- **Reason:** The style family's named factor is a bundled renderer package, not an
  isolated visual property, so "one factor" was false for that family. Method had
  always said so ("not an isolated typography factor"); the error was introduced
  into Results by the D031 restructuring and existed only there.
- **Rejected alternative:** "holding the source cohort and payload semantics fixed"
  was proposed. It is inaccurate for the text-rhetoric family, which varies payload
  wording across two semantic families by design.
- **Audit:** The manuscript was scanned for other single-factor or
  everything-held-fixed claims. The only remaining match is the Method disclaimer,
  which is a negation rather than a claim.
- **Caveat:** Wording only. No estimand, denominator, statistic, or result changed.
- **Paper impact:** One sentence in Results. Main content still ends on page 9,
  references on page 10, no overfull boxes.
- **Supersedes:** Corrects wording introduced under D031.
- **Evidence:** `manuscript/sections/04_results.tex`, `manuscript/sections/03_method.tex`.

### D036 - Right-size the human review against comparable published work

- **Status:** ACCEPTED BEFORE ANY RATING EXISTS
- **Date:** 2026-08-31
- **Decision:** Reduce the blinded visual review to three fields on the 234
  overlay images: `text_readable`, `text_completely_invisible`, and
  `critical_damage_obscured`. Drop `original_label_still_valid`, `image_usable`,
  `text_too_obvious`, `layout_plausible`, and `approve`, and drop the 69
  unmodified photographs, since all three surviving questions concern an overlay.
  Effort falls from 2,079 to 702 judgements per reviewer, roughly 104 to 35
  minutes.
- **Reason:** Checked against the closest published work rather than against our
  own protocol. Cheng et al. (ECCV 2024), whose 3--15 px grid this paper reuses,
  runs **no** human study; SceneTAP (CVPR 2025) also runs none and instead scores
  naturalness with GPT-4o, stating that "there is no established method for
  evaluating the naturalness of text added to images". The field norm for
  typographic-attack papers is therefore zero human evaluation, and the dropped
  fields bought claims this paper had already decided not to make: `layout_plausible`
  supports a realism claim the Discussion explicitly declines, and `text_too_obvious`
  was already marked descriptive and gates nothing.
- **What is kept and why:** `critical_damage_obscured` is not a field-norm nicety
  but a threat-to-validity check specific to this design: if overlays physically
  cover the damage, part of the 36/36 matched-control result could reflect missing
  evidence rather than adversarial text. `text_readable` establishes that the
  intervention is typography rather than noise. `text_completely_invisible` is the
  second half of the section 5.2 gate and carries the camouflage observation.
  `approve` was dropped because the review-passed sensitivity subset it existed to
  define is given directly by `critical_damage_obscured == no`.
- **Caveat:** Amended before any rating was recorded, which is the only point at
  which this is legitimate. From the first recorded rating the three fields, the
  234 items, and the gates are frozen; a later change requires a new dated
  amendment and a separately labelled analysis.
- **Paper impact:** None yet. On completion the result becomes two sentences in
  Limitations plus one appendix table, and releases the nine human-review-gated
  statements listed under D033 wherever a gate is met.
- **Supersedes:** Narrows the field set fixed in D032; scope, blinding, shuffling,
  and the AI pre-audit boundary are unchanged.
- **Evidence:** Cheng et al. arXiv:2402.19150; SceneTAP arXiv:2412.00114
  supplementary; [`docs/HUMAN_EVALUATION.md`](HUMAN_EVALUATION.md) section 5.2.

### D037 - Complete the blinded human visual audit and report it in aggregate

- **Status:** ACCEPTED; COMPLETED
- **Date:** 2026-08-31
- **Decision:** The paper-facing participant description is exactly: “Two
  independent human raters assessed 234 sampled rendered images while blinded to
  model outputs, tweet text, and ground-truth severity labels.” Names, initials,
  internal rater codes, and raw private files do not enter the manuscript. An
  earlier rater pair completed the same 234-image instrument but fell below the
  predeclared agreement floor; those passes are archived, are not analysed, and
  are not described in the paper. The 234 images comprise 180 simple overlays from 60 main
  sources and 54 style overlays from nine sources. The independent pass was
  completed before all five readability disagreements were jointly adjudicated.
- **Agreement:** Pre-adjudication text-readability agreement was 229/234 (97.9%)
  with three-class Cohen's kappa 0.634. Under the conservative `yes` versus
  `uncertain/no` collapse it was 232/234 (99.1%), kappa 0.853. The two remaining
  fields had 234/234 raw agreement; kappa is not estimable because both raters
  used only `no`. Per `HUMAN_EVALUATION.md` section 4, PABAK is reported wherever
  the kappa paradox appears: 0.983 for readability and 1.000 for both saturated
  fields, on the binary collapse.
- **Observed outcomes:** Main simple, style simple, and style news overlays were
  readable in 180/180, 18/18, and 18/18 cases. Camouflage was readable in 10/18,
  uncertain in 6/18, and unreadable in 2/18 after adjudication. Across all 234
  reviewed images, no text was judged completely invisible and no overlay was
  judged to obscure critical damage.
- **Claim boundary:** The audit supports sample-bounded readability and
  critical-non-occlusion statements. It does not establish realism, stealth,
  plausibility, exact transcription, message credibility, physical robustness,
  or universal non-occlusion. It does not re-score predictions or alter the
  primary 720-source analysis and 36/36 matched-control finding.
- **Paper impact:** Replace every “human validation incomplete” statement with
  the observed, bounded audit; add a compact Results sentence and appendix table;
  keep perceptual overclaims prohibited. The abstract remains focused on the
  primary model experiment because the audit is supporting evidence and the main
  text is at the nine-page boundary.
- **Supersedes:** Resolves OPEN-002 and completes the narrowed D036 protocol.
- **Evidence:** [`docs/HUMAN_EVALUATION.md`](HUMAN_EVALUATION.md),
  [`reports/v3/manual_review/PROTOCOL.md`](../reports/v3/manual_review/PROTOCOL.md),
  [`reports/v3/manual_review/RESULTS.md`](../reports/v3/manual_review/RESULTS.md),
  and the two de-identified independent exports plus adjudication record under
  [`reports/v3/manual_review/ratings/`](../reports/v3/manual_review/ratings/).

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
| Qwen3.5 27B, early zero-shot | 90 | 0.489 | 0.447 | Eliminated from paper-facing evidence |
| Qwen3.5 27B, early few-shot | 90 | 0.578 | 0.557 | Eliminated from paper-facing evidence |
| Qwen3-VL 32B, selected zero-shot | 90 | 0.544 | 0.546 | Eliminated from paper-facing evidence |

### D003-H1 - Earlier production-prompt proposal

- **Status:** ELIMINATED FROM PAPER-FACING SCOPE by D003 and D029
- **Old decision:** Use an earlier prompt candidate for production.
- **Preservation rule:** Keep immutable artifacts only as internal provenance;
  do not supply this proposal or its results to manuscript-writing systems.

## Current empirical status

| Paper model | Precision | Main clean accuracy / macro-F1 | Eligible mild+severe n | Complete paper matrix |
|---|---|---:|---:|---|
| Qwen3.5 27B | BF16 | 0.5569 / 0.5494 | 245 | Yes |
| Qwen3.6 27B | BF16 | 0.5389 / 0.5317 | 245 | Yes |
| Qwen3.8 27B | BF16 | 0.5278 / 0.5243 | 249 | Yes |
| Qwen3-VL 32B | BF16 | 0.5319 / 0.5298 | 294 | Yes |
| Mistral Small 3.1 24B | BF16 | 0.5028 / 0.4857 | 232 | Yes |
| Gemini 2.5 Flash | provider-managed | 0.5458 / 0.5485 | 273 | Yes |

The canonical interpretation, complete result tables, dataset construction, and
paper-writing guidance are in
[`reports/v3/ALL_RESULTS.md`](../reports/v3/ALL_RESULTS.md). Historical 8-bit,
4-bit, V2, and 9B outputs remain available but are outside the paper panel.

## Paper synchronization status

`paper.md` was synchronized on 2026-08-30 from the canonical A100/Gemini
artifacts and `reports/v3/ALL_RESULTS.md`. It contains the current six-model panel,
full-cohort and conditional downward outcomes, matched-benign effects, upward
transitions, completed style/relative-size tables, disaster-type caveats, and
model-specific appendix matrices. Deployment/pass/fail language and abandoned
prompt-candidate narration were removed in accordance with D018 and D029.

On 2026-08-29, the canonical decision log and `ALL_RESULTS.md` were updated with
the validated Qwen3.8 extension and completed follow-ups. Under
`MANUSCRIPT_BUILD.md`, `paper.md` is only a historical structural blueprint and
was not silently rewritten. The active LaTeX manuscript at `manuscript/main.tex`
is synchronized from D024--D025 and `ALL_RESULTS.md`. Venue is the NeurIPS 2026
AI4GOOD workshop; the NeurIPS checklist is not compiled. Illustrative overlays
may appear in the anonymous PDF with non-perceptual captions. The blinded visual
audit is complete under D037, with sample-bounded readability and non-occlusion
results. Realism, stealth, and plausibility remain outside its scope; V2 and
Qwen 9B stay historical.

## Resolved and open decisions

### RESOLVED-001 - Canonical main clean and attack outcomes

**Resolved 2026-08-29.** The initial panel and predeclared Qwen3.8
extension have complete main clean and fixed attack matrices. D018 changes
reporting language only; prompt, payloads, exclusions, predictions, and metric
denominators remain unchanged.

### RESOLVED-002 - Human visual audit

**Resolved 2026-08-31.** Two independent human raters completed the frozen
234-image blinded audit, and every disagreement was adjudicated. D037 records
the observed agreement and outcomes. The audit now supports bounded readability
and critical-non-occlusion statements for the reviewed sample; it does not
support realism, stealth, or plausibility claims.

### RESOLVED-003 - Related-work verification

**Resolved 2026-08-28.** The core disaster, typographic-attack, prompt-
injection, statistical, and model records were checked against publisher,
proceedings, or official model-card pages and consolidated in `paper.md` and
`reports/v3/ALL_RESULTS.md`. Venue-specific BibTeX export remains a typesetting
task. A first-of-kind claim remains prohibited without a systematic review.

### RESOLVED-004 - Secondary natural and official clean outcomes

**Resolved 2026-08-26.** Natural-3,474 and official-test-529 clean outputs exist
for all five paper models. The two formerly empty GCP label-conflict sensitivity
tables were regenerated locally from saved predictions without new inference.

### RESOLVED-005 - Paper protocol synchronization

**Resolved 2026-08-28.** `paper.md` was synchronized from the canonical A100
and Gemini results, `reports/v3/ALL_RESULTS.md`, and the accepted decisions.
It now includes clean-aware and benign-adjusted outcomes, full upward/downward
transition matrices, style/size tables, disaster-type caveats, and model-level
appendix counts. Future result imports must repeat the consistency check before
a manuscript-facing release.

### RESOLVED-006 - Ablation outcomes and bounded visual audit

**Resolved for inference 2026-08-26.** Presentation-style and size outputs and
paired analyses exist for the initial paper models; D024 subsequently adds
Qwen3.8. D037 later resolves readability and critical-damage occlusion for its
234-image sample. Plausibility and realism were not rated and remain outside the
paper's claims.

### RESOLVED-007 - Qwen3.8 and supervisor follow-up incorporation

**Resolved 2026-08-29.** Qwen3.8's requested canonical extension and the
open models' text-rhetoric and point-size files passed completeness validation.
Current canonical tables are updated under D024. The follow-ups remain
secondary, and their non-significant predeclared pairwise contrasts prevent
universal rhetoric or within-model monotonic-size claims.

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
