# Audit gallery data policy

`audit_gallery.html` is the publication-facing, source-text-redacted audit view.
It keeps sample identifiers, payload metadata, visual paths, predictions, and
aggregate audit findings, but does not redistribute CrisisMMD tweet text.

The image links resolve only in a local checkout where CrisisMMD and generated
attack images have been prepared. A private full-text gallery may be retained
under `reports/private/`, which is excluded from Git.

Run the public-artifact guard before committing:

```bash
python scripts/sanitize_public_reports.py --check
```
