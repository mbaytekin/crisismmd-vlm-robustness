# Codex prompt: Gemini Batch on the two missing follow-ups

> **Completed 2026-08-30. Do not resubmit.** All five Batch shards succeeded.
> The downloaded files contain 1,080/1,080 and 960/960 parsed rows with no
> request errors. Analyses are under
> `reports/v3/final_analysis/models/gemini_2_5_flash/followups/`.

Read `docs/PAPER_DECISIONS.md` D023, D024, and **D027** first. Then execute this job. Do not reopen the 720-source main experiment. Do not start or stop GCP VMs. Do not commit `.env` or print `GEMINI_API_KEY`.

## What is already done (do not rerun)

Gemini 2.5 Flash is already complete on:

| Split | Manifest | Requests | Status |
|---|---|---:|---|
| `main` | `data/v3/manifests/all_conditions.csv` | 7,200 | DONE |
| `style_ablation` | `data/v3/manifests/style_ablation_conditions.csv` | 1,200 | DONE |
| `size_ablation` | `data/v3/manifests/size_ablation_conditions.csv` | 600 | DONE — this is **relative 3/5/8% height**, not point-size |
| `natural_clean_all` | `data/v3/manifests/natural_clean_all.csv` | 3,474 | DONE |
| `official_test` | `data/v3/manifests/official_test_clean.csv` | 529 | DONE |
| `pilot` | historical | 900 | DO NOT rerun |

Do **not** call `scripts/run_gemini_v3_all.sh`. That would resubmit the canonical splits.

## What is missing (run only these two)

The five open BF16 models already have both follow-ups. Gemini does not.

1. **Text rhetoric** — `split_name=text_rhetoric_ablation`
   - Manifest: `data/v3/manifests/text_rhetoric_ablation_conditions.csv`
   - 120 sources × 9 conditions = **1,080** requests
   - Conditions: `clean`, `benign_direct_label`, `direct_label`, `benign_direct_natural`, `direct_natural`, `benign_misleading_plain`, `misleading_plain`, `benign_misleading_authority`, `misleading_authority`
   - Images are the original CrisisMMD frames; attack is tweet-prefix text.

2. **Point size** — `split_name=size_response_pt`
   - Manifest: `data/v3/manifests/size_response_pt_conditions.csv`
   - Overlays: `data/v3/attacks/size_response_pt/`
   - 60 sources × 16 conditions = **960** requests
   - Conditions: `clean` plus `benign_pt03/06/09/12/15`, `direct_pt03/06/09/12/15`, `misleading_pt03/06/09/12/15`
   - This is **not** `size_ablation`. Relative 3/5/8% is already done for Gemini.

Total new requests: **2,040**. Shard at 500 (`GEMINI_BATCH_SHARD_SIZE` default): rhetoric 3 shards, point-size 2 shards. Submit both splits as Gemini **Batch** jobs and let them run in parallel. Do not use a slow one-request-at-a-time loop.

## Frozen settings (must match canonical Gemini)

- Model: `gemini-2.5-flash`
- Prompt: the content-locked zero-shot rubric recorded in the artifact lock
- Temperature 0, top_p 1, thinking budget 0, max output tokens 512
- Key: repo-root `.env` (`GEMINI_API_KEY`). Never echo it.
- New run tag so you do not overwrite canonical outputs:
  `GEMINI_RUN_TAG=followups-d027-20260830`
- Python: `V3_PYTHON` or `.venv-mac/bin/python`; install `requirements-gemini.txt` if the client is missing.

## Exact commands

From repo root. First audit the frozen manifests; **do not** run `src.v3_followup_ablations prepare` unless a manifest or overlay is actually missing (`prepare` re-renders point-size images).

```bash
export GEMINI_RUN_TAG=followups-d027-20260830
python -m src.v3_followup_ablations check --kind both
```

Expect 1,080 rhetoric rows and 960 point-size rows, status passed.

Prepare + submit **Batch** shards (these two splits were added to `scripts/gemini_v3_batch.py` / `run_gemini_v3_batch.sh`):

```bash
scripts/run_gemini_v3_batch.sh \
  --split text_rhetoric_ablation \
  --model gemini-2.5-flash \
  --run-tag "$GEMINI_RUN_TAG" \
  --shard-size 500 \
  --action all

scripts/run_gemini_v3_batch.sh \
  --split size_response_pt \
  --model gemini-2.5-flash \
  --run-tag "$GEMINI_RUN_TAG" \
  --shard-size 500 \
  --action all
```

Poll until every shard is `JOB_STATE_SUCCEEDED`, then download:

```bash
scripts/run_gemini_v3_batch.sh --split text_rhetoric_ablation --run-tag "$GEMINI_RUN_TAG" --action status
scripts/run_gemini_v3_batch.sh --split size_response_pt --run-tag "$GEMINI_RUN_TAG" --action status
scripts/run_gemini_v3_batch.sh --split text_rhetoric_ablation --run-tag "$GEMINI_RUN_TAG" --action download
scripts/run_gemini_v3_batch.sh --split size_response_pt --run-tag "$GEMINI_RUN_TAG" --action download
```

Expected JSONL:

- `results/v3/gemini_batch/gemini-2.5-flash/followups-d027-20260830/text_rhetoric_ablation/predictions.jsonl` — 1,080 parsed
- `results/v3/gemini_batch/gemini-2.5-flash/followups-d027-20260830/size_response_pt/predictions.jsonl` — 960 parsed

If prepare finds 60 or 120 rows instead of 960/1080, you passed the wrong split or the default condition list was ignored. Stop. Do not submit a partial job.

## Analysis after download

Use the follow-up analyzer, not `scripts/analyze_gemini_v3.sh` (that script has no follow-up paths).

```bash
python -m src.v3_followup_ablations analyze \
  --kind text \
  --predictions results/v3/gemini_batch/gemini-2.5-flash/followups-d027-20260830/text_rhetoric_ablation/predictions.jsonl \
  --manifest data/v3/manifests/text_rhetoric_ablation_conditions.csv \
  --output-dir reports/v3/final_analysis/models/gemini_2_5_flash/followups/text \
  --model-slug gemini_2_5_flash

python -m src.v3_followup_ablations analyze \
  --kind size \
  --predictions results/v3/gemini_batch/gemini-2.5-flash/followups-d027-20260830/size_response_pt/predictions.jsonl \
  --manifest data/v3/manifests/size_response_pt_conditions.csv \
  --output-dir reports/v3/final_analysis/models/gemini_2_5_flash/followups/size \
  --model-slug gemini_2_5_flash
```

Completeness gate (same spirit as D024): exact row counts, unique sample×condition pairs, one prompt hash, `gemini-2.5-flash`, `parse_status=parsed` on every row, no recorded request errors.

## Reporting lock (D027/D028) — numbers do not change the design

- Add Gemini as the sixth-model appendix row. Report it even if null, non-monotonic, or weaker than open models.
- Use the unified six-model follow-up families: rhetoric 0/18 and point-size 0/48. Historical open-only counts are not reader-facing.
- Recompute unweighted appendix means over all six models after both files pass.
- Canonical size story remains relative 3/5/8%. Point-size stays appendix. Do not touch `manuscript/` numbers until this completeness gate passes.
- Do not mix these predictions into the canonical `thinking0-json-v2` result directory.

## When finished

Write a short note with: job names, shard states, parsed counts, Gemini full-cohort downward percentages for rhetoric (4 variants) and point-size (direct/misleading × 5 pt), and Holm results for Gemini only. Do not commit secrets. Do not force-push. Do not stop GCP VMs.
