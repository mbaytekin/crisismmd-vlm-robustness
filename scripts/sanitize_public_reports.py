#!/usr/bin/env python3
"""Remove redistributable-source text from publication-facing HTML reports."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORTS = [ROOT / "reports" / "v2" / "audit" / "audit_gallery.html"]
TWEET_BLOCK = re.compile(
    r'<div class="tweets">.*?</div>(?=</article>)',
    flags=re.DOTALL,
)
PUBLIC_REPLACEMENT = (
    '<div class="tweets public-redacted"><p><b>Source text omitted in the public '
    'artifact.</b> Rebuild the private local gallery from a legally obtained '
    'CrisisMMD copy to inspect the original and condition text.</p></div>'
)
SOURCE_TEXT_MARKERS = ("https://t.co/", "RT @", "Clean tweet</b><pre>", "Condition tweet</b><pre>")


def sanitize(path: Path) -> tuple[int, str]:
    original = path.read_text(encoding="utf-8")
    sanitized, replacements = TWEET_BLOCK.subn(PUBLIC_REPLACEMENT, original)
    return replacements, sanitized


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    paths = [p if p.is_absolute() else ROOT / p for p in args.paths] or DEFAULT_REPORTS
    failed = False
    for path in paths:
        replacements, sanitized = sanitize(path)
        leaked = [marker for marker in SOURCE_TEXT_MARKERS if marker in sanitized]
        if args.check:
            if replacements or leaked:
                print(f"FAIL {path.relative_to(ROOT)} replacements_needed={replacements} markers={leaked}")
                failed = True
            else:
                print(f"PASS {path.relative_to(ROOT)}")
            continue
        path.write_text(sanitized, encoding="utf-8")
        print(f"sanitized {path.relative_to(ROOT)} tweet_blocks={replacements}")
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
