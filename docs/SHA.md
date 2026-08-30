# GCP Model Snapshot SHA Records

**Recorded:** 2026-08-31

These snapshot identifiers were read from the Hugging Face cache on the
already-running GCP A100 VMs. They correspond to the upstream CUDA checkpoints
used for the canonical open-model runs. They are recorded here for provenance;
the remote repository itself has no `.git` directory.

| Paper model | Model ID | Snapshot / commit SHA | GCP cache host checked |
|---|---|---|---|
| Qwen3.5 27B BF16 | `Qwen/Qwen3.5-27B` | `fc05daec18b0a78c049392ed2e771dde82bdf654` | `can-crisismmd-qwen35-ablation` |
| Qwen3.6 27B BF16 | `Qwen/Qwen3.6-27B` | `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` | `can-crisismmd-a100-80gb-20260824` |
| Qwen3.8 27B BF16 | `Qwen/Qwen3.8-27B` | `1d4bf0f2ff6012fd82039f2fa52739d0dd7c60c0` | `can-crisismmd-a100-80gb-20260824` |
| Qwen3-VL 32B BF16 | `Qwen/Qwen3-VL-32B-Instruct` | `0cfaf48183f594c314753d30a4c4974bc75f3ccb` | `can-crisismmd-qwen32-main` |
| Mistral Small 3.1 24B BF16 | `mistralai/Mistral-Small-3.1-24B-Instruct-2503` | `68faf511d618ef198fef186659617cfd2eb8e33a` | `can-crisismmd-mistral-main` |

## Related provenance

- Runtime family: upstream CUDA checkpoints, BF16, vLLM on one NVIDIA A100
  80GB GPU.
- The per-run resolved configurations record the model ID and manifest SHA;
  their `git_commit` field is `unavailable` on the remote VM.
- Gemini 2.5 Flash is hosted and has no Hugging Face snapshot SHA; its model
  identity is recorded separately in the canonical reports.
- The local repository artifact lock also records Git commit
  `0586fb872ce4785c6445ecbfd84731eff3c0862d`; this is the code/protocol lock,
  not a replacement for the model snapshot identifiers above.

