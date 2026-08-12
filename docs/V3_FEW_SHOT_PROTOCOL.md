# V3 exploratory few-shot protocol

`p4_few_shot` is a post-hoc clean-prompt ablation created after inspecting the
Qwen3.5 27B clean pilot result. It is not part of the original frozen `p3`
confirmatory protocol.

The six demonstrations are synthetic text descriptions, with two examples per
class. They contain no CrisisMMD image, tweet, sample ID, or label and therefore
do not copy pilot or main examples into the prompt. The model still receives
exactly one target image per request.

Use only the 90-sample clean pilot to compare `p4_few_shot` with `frozen_p3`.
Do not inspect attack outcomes while selecting the prompt. If `p4_few_shot` is
selected, lock its text and hash before evaluating the untouched clean main
split. Report the prompt revision as exploratory/post-hoc, publish both pilot
results, and keep the original frozen-prompt result as the confirmatory
baseline. Never replace or overwrite `configs/prompts/frozen_prompt.yaml`.

Run the Qwen3.5 27B pilot ablation while its MLX server is active:

```bash
VLM_BASE_URL=http://127.0.0.1:8080/v1 \
V3_EXPECTED_MODEL_ID=mlx-community/Qwen3.5-27B-8bit \
.venv-mac/bin/python -m src.v3_inference run \
  --run-id v3_qwen35_27b_8bit_p4_few_shot_pilot_seed42 \
  --split pilot \
  --conditions clean \
  --concurrency 1 \
  --prompt-config configs/prompts/p4_few_shot.yaml
```

Then evaluate the unchanged pilot gate:

```bash
.venv-mac/bin/python -m src.v3_clean_gate \
  --run-id v3_qwen35_27b_8bit_p4_few_shot_pilot_seed42 \
  --phase pilot
```

## Qwen3.5 27B pilot result

The 90-sample clean run completed with 90 parsed responses. Relative to
`frozen_p3`, accuracy increased from 0.489 (44/90) to 0.578 (52/90), and macro
F1 increased from 0.447 to 0.557. Little-or-no recall increased from 0.267 to
0.533, mild recall increased from 0.267 to 0.300, and severe recall decreased
slightly from 0.933 to 0.900. Severe predictions decreased from 53 to 45.

In the paired comparison, nine previously incorrect predictions became correct
and one previously correct prediction became incorrect. The exploratory exact
McNemar p-value is 0.0215; it is descriptive rather than confirmatory because
the ablation was designed after inspection of the baseline pilot result.

The prompt passed parse rate and macro-F1 gates, but did not pass the 0.60
accuracy gate or the 0.40 minimum class-recall gate. Do not run it on the clean
main split under the current qualification policy. The remaining bottleneck is
`mild_damage` recall (0.300).
