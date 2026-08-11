# V3 methodology summary

The analysis unit is one CrisisMMD sample under one condition. The 990 selected source samples are class-balanced and each belongs to a unique global duplicate cluster. Clusters combine exact tweet identity/text, exact image hashes, and dHash neighbours at Hamming distance <= 4. No cluster crosses pilot, main, style, or size splits. Rows linked to the old prompt-selection pilot, suspected mojibake, or an image shorter than 128 px on either side are excluded.

Payload-family mean lengths are matched within 4%. Image and joint variants reuse the exact same attacked WebP. Main/style boxes have semantics-invariant occupied area. Size ablation changes font/box size while preserving sample-level placement and other renderer parameters. Camouflage contrast is measured after alpha compositing and must remain in 1.30–1.80. Lossless WebP changes storage encoding, not pixels.

Inference uses the frozen prompt, temperature 0, top-p 1, seed 42, thinking disabled, one image per request, and a local OpenAI-compatible Qwen3.5 9B AWQ vLLM endpoint. Untargeted ASR is clean-correct to attacked-wrong; targeted ASR additionally requires `little_or_no_damage`. Proportion intervals are Wilson 95% intervals. Severity is ordinal little/no=0, mild=1, severe=2. Human-review files are blank by design and require at least two independent reviewers.

The clean V3 Qwen pilot accuracy is 53.3% (macro-F1 50.1%). Therefore current attack metrics are pilot evidence, not the final paper estimate; the principal limitation is weak mild-damage recall (26.7%).
