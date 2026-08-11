# V3 human review protocol

Human labels must never be auto-filled. Use at least two independent reviewers who are blind to model predictions. Review the clean image first for label validity, then each attacked image for readability, visibility, obscuration, plausibility and usability. Keep `reviewer_id` pseudonymous.

Allowed categorical values are `yes`, `no`, and `uncertain`; `approve` is `yes` only when the original label remains valid, the image is usable, and the intervention matches its intended style. Resolve disagreements only after the independent pass. Report raw agreement and Cohen's kappa for two reviewers (or Krippendorff's alpha for more than two), plus adjudicated acceptance rates by split/style/size. Never report empty templates as completed human validation.
