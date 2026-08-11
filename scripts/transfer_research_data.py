#!/usr/bin/env python3
"""Move ignored research artifacts through a mounted external disk.

The external disk stores a portable mirror plus a SHA-256 manifest.  Paths in
the mirror are relative to the repository root, so importing on another
computer restores every file to the same project location.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
BUNDLE_NAME = "crisismmd-vlm-robustness-data"
SCHEMA_VERSION = 1
CHUNK_SIZE = 8 * 1024 * 1024
SPACE_MARGIN = 256 * 1024 * 1024

# Git already transfers publication-facing reports and code.  These are the
# ignored/private research artifacts required to resume experiments.
MANAGED_PATHS = (
    "data",
    "results",
    "logs",
    "reports/private",
    "reports/manual_review/assets",
    ".model-lock",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit(repo: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def relative_name(path: Path, repo: Path) -> str:
    return path.relative_to(repo).as_posix()


def git_tracked_files(repo: Path) -> set[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=repo,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return set()
    return {item.decode("utf-8") for item in result.stdout.split(b"\0") if item}


def collect(repo: Path) -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    directories: set[str] = set()
    tracked = git_tracked_files(repo)
    for relative in MANAGED_PATHS:
        target = repo / relative
        if not target.exists():
            continue
        if target.is_symlink():
            raise RuntimeError(f"Managed path must not be a symlink: {target}")
        if target.is_file():
            files.append(target)
            continue
        directories.add(relative)
        for item in target.rglob("*"):
            if item.is_symlink():
                raise RuntimeError(f"Symlinks are not allowed in transfer data: {item}")
            if item.is_dir():
                directories.add(relative_name(item, repo))
            elif item.is_file():
                if relative_name(item, repo) not in tracked:
                    files.append(item)
    return sorted(files, key=lambda path: relative_name(path, repo)), sorted(directories)


def safe_relative(value: str) -> Path:
    parsed = PurePosixPath(value)
    if parsed.is_absolute() or ".." in parsed.parts or not parsed.parts:
        raise RuntimeError(f"Unsafe path in transfer manifest: {value!r}")
    return Path(*parsed.parts)


def validate_disk_argument(disk: Path, repo: Path) -> Path:
    disk = disk.expanduser().resolve()
    repo = repo.resolve()
    if not disk.is_dir():
        raise FileNotFoundError(f"Mounted disk directory does not exist: {disk}")
    if disk == Path(disk.anchor) or disk == Path.home().resolve():
        raise RuntimeError("Pass the external disk mount directory, not / or the home directory.")
    if disk == repo or repo in disk.parents or disk in repo.parents:
        raise RuntimeError("The transfer disk must be outside the Git repository.")
    return disk


def copy_and_hash(source: Path, destination: Path, expected_digest: str | None = None) -> str:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".transfer-part")
    before = source.stat()
    digest = hashlib.sha256()
    try:
        with source.open("rb") as reader, temporary.open("wb") as writer:
            for chunk in iter(lambda: reader.read(CHUNK_SIZE), b""):
                digest.update(chunk)
                writer.write(chunk)
            writer.flush()
            os.fsync(writer.fileno())
        after = source.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise RuntimeError(f"Source changed while it was copied: {source}")
        actual_digest = digest.hexdigest()
        if expected_digest is not None and actual_digest != expected_digest:
            raise RuntimeError(f"Source checksum mismatch: {source}")
        try:
            shutil.copystat(source, temporary)
        except OSError:
            # exFAT and similar cross-platform filesystems may not preserve all
            # Unix metadata. Content integrity is verified independently.
            pass
        os.replace(temporary, destination)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return actual_digest


def enough_space(destination_root: Path, required: int) -> None:
    free = shutil.disk_usage(destination_root).free
    if free < required + SPACE_MARGIN:
        raise RuntimeError(
            f"Insufficient free space at {destination_root}: "
            f"need about {(required + SPACE_MARGIN) / 2**30:.2f} GiB, "
            f"have {free / 2**30:.2f} GiB"
        )


def print_progress(index: int, count: int, copied_bytes: int, total_bytes: int, path: str) -> None:
    percent = 100.0 if total_bytes == 0 else copied_bytes * 100.0 / total_bytes
    print(
        f"[{index:>6}/{count}] {percent:6.2f}% "
        f"({copied_bytes / 2**30:.2f}/{total_bytes / 2**30:.2f} GiB) {path}",
        flush=True,
    )


def write_json_atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".transfer-part")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def export_data(repo: Path, disk: Path) -> None:
    files, directories = collect(repo)
    if not files:
        raise RuntimeError("No managed research data was found to export.")
    bundle = disk / BUNDLE_NAME
    payload_root = bundle / "payload"
    payload_root.mkdir(parents=True, exist_ok=True)
    total_bytes = sum(path.stat().st_size for path in files)
    initially_required = sum(
        path.stat().st_size
        for path in files
        if not (payload_root / path.relative_to(repo)).exists()
        or (payload_root / path.relative_to(repo)).stat().st_size != path.stat().st_size
    )
    enough_space(disk, initially_required)

    records: list[dict[str, object]] = []
    completed_bytes = 0
    copied_files = 0
    for index, source in enumerate(files, start=1):
        relative = source.relative_to(repo)
        relative_text = relative.as_posix()
        destination = payload_root / relative
        size = source.stat().st_size
        digest: str
        if destination.is_file() and destination.stat().st_size == size:
            source_digest = sha256_file(source)
            if sha256_file(destination) == source_digest:
                digest = source_digest
            else:
                enough_space(disk, size)
                digest = copy_and_hash(source, destination)
                copied_files += 1
        else:
            enough_space(disk, size)
            digest = copy_and_hash(source, destination)
            copied_files += 1
        records.append({"path": relative_text, "bytes": size, "sha256": digest})
        completed_bytes += size
        if index == 1 or index == len(files) or index % 250 == 0:
            print_progress(index, len(files), completed_bytes, total_bytes, relative_text)

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "project": "crisismmd-vlm-robustness",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_git_commit": git_commit(repo),
        "source_hostname": socket.gethostname(),
        "managed_paths": list(MANAGED_PATHS),
        "directories": directories,
        "file_count": len(records),
        "total_bytes": total_bytes,
        "files": records,
    }
    write_json_atomic(bundle / "manifest.json", manifest)
    print(
        json.dumps(
            {
                "status": "exported",
                "bundle": str(bundle),
                "files": len(records),
                "copied_files": copied_files,
                "total_gib": round(total_bytes / 2**30, 3),
                "git_commit": manifest["source_git_commit"],
            },
            indent=2,
        )
    )


def load_manifest(disk: Path) -> tuple[Path, dict]:
    bundle = disk / BUNDLE_NAME
    manifest_path = bundle / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Transfer manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise RuntimeError(f"Unsupported transfer schema: {manifest.get('schema_version')}")
    if manifest.get("project") != "crisismmd-vlm-robustness":
        raise RuntimeError(f"Unexpected transfer project: {manifest.get('project')}")
    if int(manifest.get("file_count", -1)) != len(manifest.get("files", [])):
        raise RuntimeError("Transfer manifest file count is inconsistent.")
    return bundle, manifest


def verify_records(root: Path, manifest: dict, label: str) -> None:
    records = manifest["files"]
    total_bytes = int(manifest["total_bytes"])
    completed_bytes = 0
    failures: list[str] = []
    for index, record in enumerate(records, start=1):
        relative = safe_relative(str(record["path"]))
        path = root / relative
        expected_size = int(record["bytes"])
        if not path.is_file():
            failures.append(f"missing: {relative.as_posix()}")
        elif path.stat().st_size != expected_size:
            failures.append(f"size: {relative.as_posix()}")
        elif sha256_file(path) != record["sha256"]:
            failures.append(f"sha256: {relative.as_posix()}")
        completed_bytes += expected_size
        if index == 1 or index == len(records) or index % 250 == 0:
            print_progress(index, len(records), completed_bytes, total_bytes, relative.as_posix())
        if len(failures) >= 20:
            break
    if failures:
        raise RuntimeError({"status": "failed", "target": label, "failures": failures})
    print(json.dumps({"status": "verified", "target": label, "files": len(records)}, indent=2))


def import_data(repo: Path, disk: Path) -> None:
    bundle, manifest = load_manifest(disk)
    payload_root = bundle / "payload"
    records = manifest["files"]
    current_commit = git_commit(repo)
    source_commit = str(manifest.get("source_git_commit", "unavailable"))
    if current_commit != "unavailable" and source_commit not in {"unavailable", current_commit}:
        print(
            f"WARNING: transfer was exported at Git commit {source_commit}, "
            f"but this repository is at {current_commit}.",
            file=sys.stderr,
        )
    for value in manifest.get("directories", []):
        (repo / safe_relative(str(value))).mkdir(parents=True, exist_ok=True)

    required = sum(
        int(record["bytes"])
        for record in records
        if not (repo / safe_relative(str(record["path"]))).is_file()
        or (repo / safe_relative(str(record["path"]))).stat().st_size != int(record["bytes"])
    )
    enough_space(repo, required)
    total_bytes = int(manifest["total_bytes"])
    completed_bytes = 0
    copied_files = 0
    for index, record in enumerate(records, start=1):
        relative = safe_relative(str(record["path"]))
        source = payload_root / relative
        destination = repo / relative
        expected_size = int(record["bytes"])
        expected_digest = str(record["sha256"])
        if not source.is_file() or source.stat().st_size != expected_size:
            raise RuntimeError(f"Missing or truncated disk file: {source}")
        if destination.is_file() and destination.stat().st_size == expected_size:
            if sha256_file(destination) == expected_digest:
                completed_bytes += expected_size
                if index == 1 or index == len(records) or index % 250 == 0:
                    print_progress(index, len(records), completed_bytes, total_bytes, relative.as_posix())
                continue
        enough_space(repo, expected_size)
        copy_and_hash(source, destination, expected_digest=expected_digest)
        copied_files += 1
        completed_bytes += expected_size
        if index == 1 or index == len(records) or index % 250 == 0:
            print_progress(index, len(records), completed_bytes, total_bytes, relative.as_posix())

    verify_records(repo, manifest, "repository")
    print(
        json.dumps(
            {
                "status": "imported",
                "repository": str(repo),
                "files": len(records),
                "copied_files": copied_files,
                "source_git_commit": manifest["source_git_commit"],
            },
            indent=2,
        )
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export, import, or verify ignored CrisisMMD research data."
    )
    parser.add_argument("command", choices=("export", "import", "verify-disk", "verify-repo"))
    parser.add_argument("disk", type=Path, help="Mounted external disk directory")
    parser.add_argument("--repo", type=Path, default=ROOT, help=argparse.SUPPRESS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = args.repo.expanduser().resolve()
    if not (repo / ".git").is_dir():
        raise RuntimeError(f"Not a Git repository: {repo}")
    disk = validate_disk_argument(args.disk, repo)
    if args.command == "export":
        export_data(repo, disk)
    elif args.command == "import":
        import_data(repo, disk)
    else:
        bundle, manifest = load_manifest(disk)
        root = bundle / "payload" if args.command == "verify-disk" else repo
        verify_records(root, manifest, "external disk" if args.command == "verify-disk" else "repository")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
