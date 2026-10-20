#!/usr/bin/env python3
"""
Normalize dataset split naming across repository cohorts.
Standardizes legacy 'Test_*' prefixes to 'Validation_*' to ensure parity with the
current dataset schema (${dataset}_${mode}_${label}_${annotator}_${timestamp}),
and safely eliminates redundant macOS copy artifacts (' copy.').
"""

import argparse
import filecmp
import os
import sys
from typing import Dict, List, Tuple

# Ensure scripts directory is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from config import HUAWEI_DATASET_DIR, DATASET_DIR


def find_split_files(target_dir: str, from_prefix: str = "Test") -> List[str]:
    """
    Locate all files starting with the specified split prefix followed by an underscore.
    """
    if not os.path.isdir(target_dir):
        raise FileNotFoundError(f"Directory not found: {target_dir}")

    matching_files = []
    prefix_pattern = f"{from_prefix.lower()}_"
    for entry in os.scandir(target_dir):
        if entry.is_file() and entry.name.lower().startswith(prefix_pattern):
            matching_files.append(entry.name)

    return sorted(matching_files)


def inspect_copy_duplicates(target_dir: str) -> List[Tuple[str, str, bool]]:
    """
    Identify potential duplicate files containing macOS copy-paste artifacts (' copy.').
    Returns a list of tuples: (copy_filename, canonical_filename, byte_identical).
    """
    duplicates = []
    for entry in os.scandir(target_dir):
        if entry.is_file() and " copy." in entry.name:
            canonical_name = entry.name.replace(" copy.", ".")
            canonical_path = os.path.join(target_dir, canonical_name)
            if os.path.isfile(canonical_path):
                copy_path = entry.path
                is_identical = filecmp.cmp(copy_path, canonical_path, shallow=False)
                duplicates.append((entry.name, canonical_name, is_identical))
            else:
                duplicates.append((entry.name, canonical_name, False))
    return sorted(duplicates)


def remove_copy_duplicates(
    target_dir: str,
    dry_run: bool = False,
    verbose: bool = True,
) -> Dict[str, int]:
    """
    Safely delete duplicate files containing ' copy.' after verifying byte-for-byte
    equivalence with an existing canonical file.
    """
    duplicates = inspect_copy_duplicates(target_dir)
    stats = {
        "total_copy_files": len(duplicates),
        "removed": 0,
        "skipped_missing_canonical": 0,
        "skipped_content_mismatch": 0,
        "errors": 0,
    }

    mode_str = "[DRY-RUN]" if dry_run else "[EXECUTE]"
    if verbose:
        print(f"{mode_str} Duplicate Purge: scanning {target_dir}")
        print(f"{mode_str} Identified copy files: {len(duplicates)}")
        print("-" * 60)

    for copy_name, canonical_name, is_identical in duplicates:
        copy_path = os.path.join(target_dir, copy_name)
        canonical_path = os.path.join(target_dir, canonical_name)

        if not os.path.isfile(canonical_path):
            stats["skipped_missing_canonical"] += 1
            if verbose:
                print(f"[WARNING] Skipping {copy_name}: canonical counterpart {canonical_name} not found.")
            continue

        if not is_identical:
            stats["skipped_content_mismatch"] += 1
            if verbose:
                print(f"[WARNING] Skipping {copy_name}: content differs from {canonical_name}.")
            continue

        if dry_run:
            stats["removed"] += 1
            if verbose and stats["removed"] <= 10:
                print(f"[PURGE PREVIEW] Would remove: {copy_name}")
        else:
            try:
                os.remove(copy_path)
                stats["removed"] += 1
                if verbose and stats["removed"] <= 10:
                    print(f"[REMOVED] Deleted duplicate: {copy_name}")
            except OSError as err:
                stats["errors"] += 1
                if verbose:
                    print(f"[ERROR] Failed to delete {copy_name}: {err}")

    if verbose and stats["removed"] > 10:
        print(f"... and {stats['removed'] - 10} more duplicate files.")

    if verbose:
        print("-" * 60)
        print("Duplicate Removal Summary:")
        print(f"  Total Candidate Copy Files: {stats['total_copy_files']}")
        print(f"  Removed / Previewed:        {stats['removed']}")
        print(f"  Skipped (Missing Canonical): {stats['skipped_missing_canonical']}")
        print(f"  Skipped (Content Mismatch):  {stats['skipped_content_mismatch']}")
        print(f"  Errors:                      {stats['errors']}")

    return stats


def normalize_split_prefixes(
    target_dir: str,
    from_prefix: str = "Test",
    to_prefix: str = "Validation",
    dry_run: bool = False,
    verbose: bool = True,
) -> Dict[str, int]:
    """
    Rename files matching '{from_prefix}_*' to '{to_prefix}_*'.
    Guards against accidental file overwriting.
    """
    files = find_split_files(target_dir, from_prefix=from_prefix)
    stats: Dict[str, int] = {
        "total_matched": len(files),
        "renamed": 0,
        "skipped_collision": 0,
        "errors": 0,
    }

    if verbose:
        mode_str = "[DRY-RUN]" if dry_run else "[EXECUTE]"
        print(f"\n{mode_str} Prefix Normalization: scanning {target_dir}")
        print(f"{mode_str} Target prefix replacement: '{from_prefix}_*' -> '{to_prefix}_*'")
        print(f"{mode_str} Matched candidate files: {len(files)}")
        print("-" * 60)

    from_prefix_len = len(from_prefix)
    for fname in files:
        remainder = fname[from_prefix_len:]
        if remainder.startswith("_"):
            new_fname = f"{to_prefix}{remainder}"
        else:
            new_fname = f"{to_prefix}_{remainder.lstrip('_')}"

        old_path = os.path.join(target_dir, fname)
        new_path = os.path.join(target_dir, new_fname)

        if os.path.exists(new_path) and old_path != new_path:
            stats["skipped_collision"] += 1
            if verbose:
                print(f"[COLLISION] Skipping: {fname} -> {new_fname} already exists.")
            continue

        if dry_run:
            stats["renamed"] += 1
            if verbose and stats["renamed"] <= 10:
                print(f"[RENAME PREVIEW] {fname} -> {new_fname}")
        else:
            try:
                os.rename(old_path, new_path)
                stats["renamed"] += 1
                if verbose and stats["renamed"] <= 10:
                    print(f"[RENAMED] {fname} -> {new_fname}")
            except OSError as err:
                stats["errors"] += 1
                if verbose:
                    print(f"[ERROR] Failed to rename {fname} -> {new_fname}: {err}")

    if verbose and stats["renamed"] > 10:
        print(f"... and {stats['renamed'] - 10} more files.")

    if verbose:
        print("-" * 60)
        print("Prefix Normalization Summary:")
        print(f"  Matched:            {stats['total_matched']}")
        print(f"  Renamed/Previewed:  {stats['renamed']}")
        print(f"  Collisions Skipped: {stats['skipped_collision']}")
        print(f"  Errors:             {stats['errors']}")

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Normalize dataset split naming convention and clean redundant copy files."
    )
    parser.add_argument(
        "--dir",
        type=str,
        default=HUAWEI_DATASET_DIR,
        help=f"Target directory to process (default: {HUAWEI_DATASET_DIR})",
    )
    parser.add_argument(
        "--from-prefix",
        type=str,
        default="Test",
        help="Prefix to match and replace (default: 'Test')",
    )
    parser.add_argument(
        "--to-prefix",
        type=str,
        default="Validation",
        help="Target replacement prefix (default: 'Validation')",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a trial run without modifying files on disk.",
    )
    parser.add_argument(
        "--remove-copies",
        action="store_true",
        help="Safely remove duplicate files containing ' copy.' after verifying byte equality.",
    )
    parser.add_argument(
        "--skip-rename",
        action="store_true",
        help="Skip prefix renaming step.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Execute both duplicate copy removal and split prefix renaming.",
    )

    args = parser.parse_args()
    target_dir = os.path.abspath(args.dir)

    should_remove_copies = args.remove_copies or args.all
    should_rename = not args.skip_rename or args.all

    if not should_remove_copies and not should_rename:
        print("No actions requested. Specify --remove-copies, --all, or omit --skip-rename.")
        sys.exit(0)

    if should_remove_copies:
        remove_copy_duplicates(target_dir=target_dir, dry_run=args.dry_run, verbose=True)

    if should_rename:
        normalize_split_prefixes(
            target_dir=target_dir,
            from_prefix=args.from_prefix,
            to_prefix=args.to_prefix,
            dry_run=args.dry_run,
            verbose=True,
        )


if __name__ == "__main__":
    main()
