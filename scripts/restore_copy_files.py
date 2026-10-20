#!/usr/bin/env python3
"""
Restore deleted duplicate copy files into a dedicated temporary folder for user review.
Reads the exact list of deleted files recorded prior to removal, copies from the canonical
counterparts in huawei_datasets/, and outputs an inspection manifest.
"""

import argparse
import csv
import os
import shutil
import sys
from typing import List, Tuple

# Base Directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
HUAWEI_DIR = os.path.join(PROJECT_ROOT, "huawei_datasets")
DEFAULT_TEMP_DIR = os.path.join(PROJECT_ROOT, "temp_copy_datasets")
LOG_PATH = "/Users/asthiseta/.gemini/antigravity/brain/507f51a8-ae69-4d47-a546-1188ddee1033/.system_generated/steps/102/output.txt"


def get_copy_file_list(log_path: str = LOG_PATH) -> List[str]:
    """Extract list of copy filenames from the pre-deletion log."""
    if not os.path.isfile(log_path):
        raise FileNotFoundError(f"Step log not found at: {log_path}")

    files = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if "huawei_datasets" in line and " copy." in line:
                clean_name = os.path.basename(line.lstrip("./"))
                files.append(clean_name)
    return sorted(list(set(files)))


def restore_copy_files(
    target_dir: str = DEFAULT_TEMP_DIR,
    source_dir: str = HUAWEI_DIR,
    log_path: str = LOG_PATH,
    dry_run: bool = False,
    verbose: bool = True,
) -> int:
    """
    Restore copy files into target_dir from canonical files in source_dir.
    Creates an inspection manifest for audit.
    """
    copy_files = get_copy_file_list(log_path)
    if verbose:
        mode_str = "[DRY-RUN]" if dry_run else "[EXECUTE]"
        print(f"{mode_str} Restoring {len(copy_files)} copy files to: {target_dir}")
        print(f"{mode_str} Source canonical directory: {source_dir}")

    if not dry_run:
        os.makedirs(target_dir, exist_ok=True)

    manifest_rows = []
    restored_count = 0
    missing_canonical = 0

    for copy_name in copy_files:
        canonical_name = copy_name.replace(" copy.", ".")
        canonical_path = os.path.join(source_dir, canonical_name)
        dest_path = os.path.join(target_dir, copy_name)

        if not os.path.isfile(canonical_path):
            missing_canonical += 1
            manifest_rows.append({
                "copy_filename": copy_name,
                "canonical_filename": canonical_name,
                "size_bytes": 0,
                "status": "MISSING_CANONICAL",
            })
            if verbose:
                print(f"[MISSING] Cannot find canonical: {canonical_name}")
            continue

        size = os.path.getsize(canonical_path)
        manifest_rows.append({
            "copy_filename": copy_name,
            "canonical_filename": canonical_name,
            "size_bytes": size,
            "status": "RESTORED",
        })

        if not dry_run:
            shutil.copy2(canonical_path, dest_path)
            restored_count += 1
        else:
            restored_count += 1

    if not dry_run:
        manifest_path = os.path.join(target_dir, "manifest.csv")
        with open(manifest_path, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["copy_filename", "canonical_filename", "size_bytes", "status"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(manifest_rows)
        if verbose:
            print(f"Audit manifest written to: {manifest_path}")

    if verbose:
        print("-" * 60)
        print("Restoration Summary:")
        print(f"  Total Requested:    {len(copy_files)}")
        print(f"  Restored / Planned: {restored_count}")
        print(f"  Missing Canonical:  {missing_canonical}")

    return restored_count


def main():
    parser = argparse.ArgumentParser(
        description="Restore copy files into a temp folder for review."
    )
    parser.add_argument(
        "--dest",
        type=str,
        default=DEFAULT_TEMP_DIR,
        help=f"Destination directory (default: {DEFAULT_TEMP_DIR})",
    )
    parser.add_argument(
        "--source",
        type=str,
        default=HUAWEI_DIR,
        help=f"Source directory containing canonical files (default: {HUAWEI_DIR})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate restoration without copying files.",
    )

    args = parser.parse_args()
    restore_copy_files(
        target_dir=os.path.abspath(args.dest),
        source_dir=os.path.abspath(args.source),
        dry_run=args.dry_run,
        verbose=True,
    )


if __name__ == "__main__":
    main()
