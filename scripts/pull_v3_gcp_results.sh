#!/usr/bin/env bash
set -uo pipefail

PROJECT="${V3_GCP_PROJECT:-my-project-1517472402986}"
ZONE="${V3_GCP_ZONE:-us-central1-a}"
REMOTE_ROOT="${V3_GCP_REMOTE_ROOT:-/home/can.baytekin/crisismmd-vlm-robustness}"
LOCAL_ROOT="${V3_GCP_LOCAL_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage: scripts/pull_v3_gcp_results.sh [options]

Pull completed or partial GCP predictions, reports, logs, and runtime metadata
to the local repository. It is safe to rerun after an internet interruption.

Options:
  --dry-run   Show the planned gcloud scp commands without transferring.
  -h, --help  Show this help.

The script does not stop VMs or inference processes.
EOF
}

while (( $# )); do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

mkdir -p "$LOCAL_ROOT/results/v3/gcp_a100" "$LOCAL_ROOT/reports/v3/gcp_a100" "$LOCAL_ROOT/logs/v3/gcp_a100"

pull_vm() {
  local vm="$1"
  if ! gcloud compute instances describe "$vm" --project="$PROJECT" --zone="$ZONE" >/dev/null 2>&1; then
    echo "[$vm] instance not found; skipping."
    return 0
  fi
  local remote="$REMOTE_ROOT/results/v3/gcp_a100"
  local target="$LOCAL_ROOT/results/v3"
  mkdir -p "$target"
  echo "[$vm] pulling predictions and reports"
  local cmd=(gcloud compute scp --project="$PROJECT" --zone="$ZONE" --recurse
    "$vm:$remote" "$target")
  if (( DRY_RUN )); then
    printf '  '; printf '%q ' "${cmd[@]}"; printf '\n'
  elif ! "${cmd[@]}"; then
    echo "[$vm] result pull failed; it can be retried later." >&2
    return 1
  fi

  local report_target="$LOCAL_ROOT/reports/v3"
  mkdir -p "$report_target"
  local report_cmd=(gcloud compute scp --project="$PROJECT" --zone="$ZONE" --recurse
    "$vm:$REMOTE_ROOT/reports/v3/gcp_a100" "$report_target")
  if (( DRY_RUN )); then
    printf '  '; printf '%q ' "${report_cmd[@]}"; printf '\n'
  elif ! "${report_cmd[@]}"; then
    echo "[$vm] report pull failed; predictions and logs were pulled and can be reused." >&2
    return 1
  fi

  local log_target="$LOCAL_ROOT/logs/v3"
  mkdir -p "$log_target"
  local log_cmd=(gcloud compute scp --project="$PROJECT" --zone="$ZONE" --recurse
    "$vm:$REMOTE_ROOT/logs/v3/gcp_a100" "$log_target")
  if (( DRY_RUN )); then
    printf '  '; printf '%q ' "${log_cmd[@]}"; printf '\n'
  elif ! "${log_cmd[@]}"; then
    echo "[$vm] log pull failed; predictions were pulled and can be reused." >&2
    return 1
  fi
}

VMS=(
  can-crisismmd-a100-80gb-20260824
  can-crisismmd-qwen32-main
  can-crisismmd-qwen32-ablation
  can-crisismmd-qwen32-clean
  can-crisismmd-qwen35-ablation
  can-crisismmd-mistral-main
  can-crisismmd-mistral-clean
  can-crisismmd-mistral-ablation
)

failed=0
for vm in "${VMS[@]}"; do
  pull_vm "$vm" || failed=$((failed + 1))
done

echo "GCP result pull finished: failed=$failed"
echo "Local results: $LOCAL_ROOT/results/v3/gcp_a100"
(( failed == 0 ))
