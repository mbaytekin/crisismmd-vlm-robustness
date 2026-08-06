#!/usr/bin/env bash
set -euo pipefail

# Optional recovery helper for the large official archive after a connection drop.
# It only targets the named CrisisMMD archive and verifies byte counts before joining.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
source /home/db21052/anaconda3/etc/profile.d/conda.sh
conda activate vlm_app
URL="https://crisisnlp.qcri.org/data/crisismmd/CrisisMMD_v2.0.tar.gz"
TARGET="data/raw/CrisisMMD_v2.0.tar.gz"
TOTAL=1902053684
PREFIX="data/raw/CrisisMMD_v2.0.tar.gz.prefix"
if [[ ! -f "$TARGET" ]]; then echo "missing partial archive: $TARGET" >&2; exit 2; fi
mv "$TARGET" "$PREFIX"
START=$(stat -c '%s' "$PREFIX")
REMAINING=$((TOTAL - START))
if (( REMAINING <= 0 )); then mv "$PREFIX" "$TARGET"; exit 0; fi
N=4
CHUNK=$(((REMAINING + N - 1) / N))
for ((i=0; i<N; i++)); do
  begin=$((START + i * CHUNK))
  end=$((begin + CHUNK - 1))
  if (( end >= TOTAL )); then end=$((TOTAL - 1)); fi
  if (( begin >= TOTAL )); then continue; fi
  part="data/raw/CrisisMMD.v2.0.part.${i}"
  rm -f "$part"
  curl -L --fail --retry 3 --retry-delay 2 --range "$begin-$end" -o "$part" "$URL" >"data/raw/part_${i}.log" 2>&1 &
done
wait
for ((i=0; i<N; i++)); do
  part="data/raw/CrisisMMD.v2.0.part.${i}"
  [[ -f "$part" ]] || continue
  expected=$(python - "$START" "$CHUNK" "$i" "$TOTAL" <<'PY'
import sys
start, chunk, i, total = map(int, sys.argv[1:])
begin = start + i * chunk
end = min(total - 1, begin + chunk - 1)
print(max(0, end - begin + 1))
PY
)
  actual=$(stat -c '%s' "$part")
  [[ "$actual" == "$expected" ]] || { echo "range size mismatch for $part: $actual != $expected" >&2; exit 3; }
done
cat "$PREFIX" data/raw/CrisisMMD.v2.0.part.* > data/raw/CrisisMMD_v2.0.tar.gz.complete
[[ "$(stat -c '%s' data/raw/CrisisMMD_v2.0.tar.gz.complete)" == "$TOTAL" ]] || { echo "final size mismatch" >&2; exit 4; }
mv data/raw/CrisisMMD_v2.0.tar.gz.complete "$TARGET"
rm -f "$PREFIX" data/raw/CrisisMMD.v2.0.part.* data/raw/part_*.log
echo "completed $TARGET ($(stat -c '%s' "$TARGET") bytes)"
