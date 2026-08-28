# GCP A100 Workflow

This guide covers the reproducible GCP execution path for the paper-facing V3
experiments. It assumes the `llamaturk`-managed project is exposed to `gcloud`
as project ID `my-project-1517472402986`.

## 1. Authenticate and select the project

```bash
gcloud auth login
gcloud config set project my-project-1517472402986
gcloud auth list
gcloud config get-value project
```

The project name shown in Cloud Console and its CLI project ID can differ. Use
the project ID returned by `gcloud projects list` in commands and billing checks.

## 2. Inspect and start an A100 VM

```bash
gcloud compute instances list \
  --filter='name~crisismmd' \
  --format='table(name,zone.basename(),status,machineType.basename(),guestAccelerators)'

gcloud compute instances start can-crisismmd-a100-80gb-20260824 \
  --zone us-central1-a
```

Connect after the VM reaches `RUNNING`:

```bash
gcloud compute ssh can.baytekin@can-crisismmd-a100-80gb-20260824 \
  --zone us-central1-a
```

The repository is expected at:

```text
/home/can.baytekin/crisismmd-vlm-robustness
```

## 3. Update and validate the remote repository

Run on the VM. Never discard remote result changes merely to update code.

```bash
cd /home/can.baytekin/crisismmd-vlm-robustness
git status --short
git fetch origin
git switch paper-facing-v3-results
git pull --ff-only origin paper-facing-v3-results
scripts/run_v3_gcp_a100.sh --list
scripts/run_v3_gcp_a100.sh --model qwen38 --stage all --dry-run
```

The Qwen3.8 row uses the official `Qwen/Qwen3.8-27B` BF16 checkpoint. The full
protocol is 7,200 main + 1,200 style + 600 size + 3,474 natural clean + 529
official-test clean predictions, or 13,003 requests in total.

## 4. Launch Qwen3.8 as a detached timed job

Run on the VM:

```bash
cd /home/can.baytekin/crisismmd-vlm-robustness
mkdir -p logs/v3/gcp_a100/launchers

nohup env V3_SHUTDOWN_ON_EXIT=1 \
  scripts/run_v3_gcp_timed_job.sh \
    --model qwen38 \
    --stage all \
    --kind both \
    --cohort both \
    --port 8000 \
  > logs/v3/gcp_a100/launchers/qwen38_full.log 2>&1 \
  < /dev/null &

echo $! > logs/v3/gcp_a100/launchers/qwen38_full.pid
```

`nohup` detaches the process from SSH. Closing the laptop connection, changing
Wi-Fi, or losing the hotspot does not stop the VM job. `V3_SHUTDOWN_ON_EXIT=1`
stops compute after success or failure; the persistent boot disk and result
files remain. A stopped VM does not charge GPU/CPU runtime, although persistent
disk storage can still incur a small charge.

## 5. Monitor without interrupting the job

```bash
tail -f /home/can.baytekin/crisismmd-vlm-robustness/logs/v3/gcp_a100/launchers/qwen38_full.log

ps -ef | grep -E 'run_v3_gcp|vllm|v3_inference' | grep -v grep

find /home/can.baytekin/crisismmd-vlm-robustness/logs/v3/gcp_a100/timed_jobs \
  -name timing.json -print
```

Each timed job records start time, end time, duration, host, and return code in
`logs/v3/gcp_a100/timed_jobs/*/timing.json`. Inference is resumable from the
result directory's SQLite cache after an interruption.

## 6. Pull only logs, predictions, and reports

Run on the Mac after the VM is reachable. The existing pull helper excludes
model checkpoints and source images:

```bash
cd ~/Desktop/crisismmd-vlm-robustness

scripts/pull_v3_gcp_results.sh \
  --vm can-crisismmd-a100-80gb-20260824 \
  --zone us-central1-a
```

Before deleting a VM or disk, verify that these local paths contain the expected
prediction counts and timing records:

```text
results/v3/gcp_a100/
reports/v3/gcp_a100/
logs/v3/gcp_a100/
```

## 7. Cost and shutdown checks

```bash
gcloud compute instances list \
  --filter='status=RUNNING AND name~crisismmd' \
  --format='table(name,zone.basename(),status,guestAccelerators)'
```

Stop an idle VM explicitly if automatic shutdown did not occur:

```bash
gcloud compute instances stop can-crisismmd-a100-80gb-20260824 \
  --zone us-central1-a
```

Do not delete the instance or persistent disk until predictions, reports,
timings, and logs have been pulled and validated locally.
