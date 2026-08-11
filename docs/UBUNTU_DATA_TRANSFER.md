# Ubuntu external-disk data transfer

This guide moves the ignored/private CrisisMMD research data between Ubuntu
workstations without changing its repository-relative layout. Every file is
recorded in a SHA-256 manifest and verified after copying.

## Fixed disk layout

The current external disk is labeled `YZTB_Vision` and mounted from
`/dev/sda1`. Keep this project under the `can.baytekin` directory:

```text
YZTB_Vision/
└── can.baytekin/
    └── crisismmd-vlm-robustness-data/
        ├── manifest.json
        └── payload/
            ├── data/
            ├── results/
            ├── logs/
            ├── reports/private/
            ├── reports/manual_review/assets/
            └── .model-lock/
```

The transfer script does not include source code, Git-tracked reports, model
caches, or virtual environments. Those arrive through Git or can be downloaded
again.

## Export from this Ubuntu workstation

Connect the disk and confirm its filesystem, mount point, and free space:

```bash
lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINTS
findmnt -nr -S /dev/sda1 -o TARGET,FSTYPE,OPTIONS
df -h /media/db21052/YZTB_Vision
```

Create the owner directory and export all managed research data:

```bash
mkdir -p /media/db21052/YZTB_Vision/can.baytekin
scripts/transfer_research_data.py export \
  /media/db21052/YZTB_Vision/can.baytekin
scripts/transfer_research_data.py verify-disk \
  /media/db21052/YZTB_Vision/can.baytekin
```

Export is incremental: files already present with identical size and SHA-256
are reused. It does not delete older extra files from the disk package.

## Import into another Ubuntu workstation

Clone or update the repository first:

```bash
git clone git@github.com:mbaytekin/crisismmd-vlm-robustness.git
cd crisismmd-vlm-robustness
```

Find the disk mount point. Ubuntu may use a different account name, so do not
assume that `/media/db21052` exists on the new workstation:

```bash
DISK_MOUNT="$(findmnt -nr -S /dev/sda1 -o TARGET)"
test -n "$DISK_MOUNT"
```

Restore the files to their original repository-relative paths and verify them:

```bash
scripts/transfer_research_data.py import \
  "$DISK_MOUNT/can.baytekin"
scripts/transfer_research_data.py verify-repo \
  "$DISK_MOUNT/can.baytekin"
python scripts/freeze_v3_artifacts.py check
```

Import replaces only manifest-listed files whose content differs. It never
deletes additional local files. A warning is printed if the transfer bundle and
the cloned repository point to different Git commits.

## Update the disk after new experiments

Run the export and disk verification again from the workstation containing the
newest data:

```bash
DISK_MOUNT="$(findmnt -nr -S /dev/sda1 -o TARGET)"
scripts/transfer_research_data.py export "$DISK_MOUNT/can.baytekin"
scripts/transfer_research_data.py verify-disk "$DISK_MOUNT/can.baytekin"
```

The bundle currently needs about 21 GiB. Leave additional free space for V3
model outputs before beginning full-set inference.

## Safely disconnect the disk

Close terminals and applications using the disk, then unmount it:

```bash
udisksctl unmount -b /dev/sda1
```

Do not disconnect the disk while export, import, or verification is running.

## Filesystem note

The current disk uses NTFS. Ubuntu has mounted it read/write through `ntfs3`.
macOS can normally read an NTFS disk, which is sufficient for importing this
bundle, but it does not provide native NTFS write support. Do not reformat the
disk without a separate backup because formatting erases its existing content.
