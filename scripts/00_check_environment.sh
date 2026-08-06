#!/usr/bin/env bash
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
source /home/db21052/anaconda3/etc/profile.d/conda.sh
conda activate vlm_app
mkdir -p reports
{
  echo "timestamp=$(date -Is)"
  echo "workspace=$ROOT"
  conda env list
  python --version
  pip list
  nvidia-smi
} > reports/environment.txt 2>&1
cp reports/environment.txt reports/environment_after.txt
echo "Wrote reports/environment.txt and reports/environment_after.txt using conda env vlm_app"

