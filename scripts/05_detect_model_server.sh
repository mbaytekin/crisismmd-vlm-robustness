#!/usr/bin/env bash
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
source /home/db21052/anaconda3/etc/profile.d/conda.sh; conda activate vlm_app
SMOKE=""
if [[ -f data/splits/pilot.csv ]]; then SMOKE="$(python - <<'PY'
import pandas as pd
from pathlib import Path
p=Path('data/splits/pilot.csv')
print(pd.read_csv(p, dtype=str).iloc[0].image_path if p.exists() else '')
PY
)"; fi
if [[ -n "$SMOKE" ]]; then python -m src.model_clients.autodetect --smoke-image "$SMOKE"; else python -m src.model_clients.autodetect; fi

