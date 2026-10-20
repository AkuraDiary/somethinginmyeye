#!/usr/bin/env python3
"""
High-Performance Multi-Model Dataset Reconciliation & Partitioning Engine.
Supports idempotent, incremental synchronization:
  - Skips already transferred, up-to-date files (zero redundant I/O)
  - Updates modified recordings when source timestamps or byte sizes change
  - Reconciles orphaned files (removes stale target files when samples are relabeled or deleted)
  - Enforces model routing:
      * dhrc_train_datasets/ & dhrc_val_datasets/ (Strictly isolated Latin letters)
      * elkinematics_train_datasets/ & elkinematics_val_datasets/ (Full Kinematic Battery)
  - Enforces DSM-5 Zero-Digit Orthographic Invariant
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple

# Base Directories and Config
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from config import (
    DATASET_DIR,
    HUAWEI_DATASET_DIR,
    DHRC_TRAIN_DIR,
    DHRC_VAL_DIR,
    ELKINEMATICS_TRAIN_DIR,
    ELKINEMATICS_VAL_DIR,
)

TARGET_DESTINATIONS = {
    "dhrc_train": DHRC_TRAIN_DIR,
    "dhrc_val": DHRC_VAL_DIR,
    "elkinematics_train": ELKINEMATICS_TRAIN_DIR,
    "elkinematics_val": ELKINEMATICS_VAL_DIR,
}

DATASET_EXTENSIONS = (".csv", ".png", ".meta.json")


def parse_filename(base_name: str) -> Optional[Dict[str, Any]]:
    """
    Deconstruct standard dataset filename schema:
    ${dataset}_${mode}_${label}_${annotator}_${client_ts}_${server_ts}
    or legacy single timestamp:
    ${dataset}_${mode}_${label}_${annotator}_${timestamp}
    """
    parts = base_name.split("_")
    if len(parts) < 4:
        return None

    dataset = parts[0]
    mode = parts[1]

    if parts[-1].isdigit() and parts[-2].isdigit():
        server_ts = parts[-1]
        client_ts = parts[-2]
        annotator = parts[-3]
        lbl_len = len(parts) - 5
        label = "_".join(parts[2 : 2 + lbl_len])
    elif parts[-1].isdigit():
        server_ts = parts[-1]
        client_ts = None
        annotator = parts[-2]
        lbl_len = len(parts) - 4
        label = "_".join(parts[2 : 2 + lbl_len])
    else:
        return None

    return {
        "base_name": base_name,
        "dataset": dataset,
        "mode": mode,
        "label": label,
        "annotator": annotator,
        "client_ts": client_ts,
        "server_ts": server_ts,
    }


def collect_source_samples(source_dirs: List[str]) -> List[Tuple[str, Dict[str, Any]]]:
    """
    Scan source directories and retrieve unique sample triplets.
    Returns list of tuples: (source_dir, sample_metadata).
    """
    samples = []
    seen_bases: Set[str] = set()

    for s_dir in source_dirs:
        if not os.path.isdir(s_dir):
            print(f"[WARNING] Source directory does not exist: {s_dir}")
            continue

        for entry in os.scandir(s_dir):
            if entry.is_file() and entry.name.endswith(".csv"):
                bn = entry.name[:-4]
                if bn in seen_bases:
                    print(f"[WARNING] Duplicate base name across sources: {bn}")
                    continue

                info = parse_filename(bn)
                if info is None:
                    print(f"[WARNING] Skipping unparseable file: {entry.name}")
                    continue

                seen_bases.add(bn)
                samples.append((s_dir, info))

    return samples


def is_file_up_to_date(src_path: str, dst_path: str) -> bool:
    """
    Check if destination file exists and is identical in size and mtime to source.
    """
    if not os.path.isfile(dst_path):
        return False
    try:
        s_stat = os.stat(src_path)
        d_stat = os.stat(dst_path)
        # Check size equality and mtime tolerance (1 second)
        return s_stat.st_size == d_stat.st_size and abs(s_stat.st_mtime - d_stat.st_mtime) < 1.0
    except OSError:
        return False


def clean_target_directory(target_dir: str, verbose: bool = True):
    """Purge all dataset files (.csv, .png, .meta.json) from target directory."""
    if not os.path.isdir(target_dir):
        os.makedirs(target_dir, exist_ok=True)
        return

    removed = 0
    for entry in os.scandir(target_dir):
        if entry.is_file() and entry.name.endswith(DATASET_EXTENSIONS):
            os.remove(entry.path)
            removed += 1
    if verbose and removed > 0:
        print(f"[CLEAN] Purged {removed} old files from {os.path.basename(target_dir)}/")


def prune_orphans(
    dest_dir: str,
    expected_filenames: Set[str],
    dry_run: bool = False,
    verbose: bool = True,
) -> int:
    """
    Remove orphaned dataset files in destination directory that no longer
    correspond to any source file (e.g. after a relabel or delete operation).
    """
    if not os.path.isdir(dest_dir):
        return 0

    orphans_removed = 0
    dir_name = os.path.basename(dest_dir)

    for entry in os.scandir(dest_dir):
        if entry.is_file() and entry.name.endswith(DATASET_EXTENSIONS):
            if entry.name not in expected_filenames:
                orphans_removed += 1
                if verbose:
                    action_tag = "[PRUNE PREVIEW]" if dry_run else "[PRUNED ORPHAN]"
                    print(f"{action_tag} {dir_name}/{entry.name}")
                if not dry_run:
                    try:
                        os.remove(entry.path)
                    except OSError as err:
                        print(f"[ERROR] Failed to prune {entry.path}: {err}")

    return orphans_removed


def reconcile_and_sync(
    source_dirs: List[str],
    dry_run: bool = False,
    force: bool = False,
    clean: bool = False,
    prune: bool = True,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Reconcile and synchronize source datasets with destination training/validation cohorts.
    Optimized to skip existing files and prune stale orphans.
    """
    for d in TARGET_DESTINATIONS.values():
        os.makedirs(d, exist_ok=True)

    if clean and not dry_run:
        for d in TARGET_DESTINATIONS.values():
            clean_target_directory(d, verbose=verbose)

    samples = collect_source_samples(source_dirs)

    # Track expected files for each destination to reconcile orphans
    expected_files: Dict[str, Set[str]] = {k: set() for k in TARGET_DESTINATIONS}

    stats: Dict[str, Any] = {
        "total_source_samples": len(samples),
        "skipped_digits": 0,
        "copied_new": 0,
        "updated_modified": 0,
        "skipped_up_to_date": 0,
        "pruned_orphans": 0,
        "cohort_samples": defaultdict(int),
        "class_counts": defaultdict(lambda: {"typical": 0, "atypical": 0}),
    }

    mode_prefix = "[DRY-RUN]" if dry_run else "[SYNC]"
    if verbose:
        print("=" * 80)
        print(f"{mode_prefix} Multi-Model Dataset Reconciliation & Sync")
        print(f"Sources:          {', '.join(source_dirs)}")
        print(f"Unique Samples:   {len(samples)}")
        print(f"Reconcile Mode:   {'Force Re-copy' if force else 'Incremental Skip-Existing'}")
        print(f"Orphan Pruning:   {'Enabled' if prune else 'Disabled'}")
        print("=" * 80)

    for src_dir, info in samples:
        bn = info["base_name"]
        label = info["label"]
        dataset_split = info["dataset"].lower()
        mode_str = info["mode"].lower()

        # Enforce Zero-Digit Invariant
        if label.isdigit():
            stats["skipped_digits"] += 1
            continue

        is_train = "train" in dataset_split
        is_val = "val" in dataset_split or "test" in dataset_split
        if not (is_train or is_val):
            continue

        is_letter = len(label) == 1 and label.isalpha()
        is_typical = "normal" in mode_str

        targets_for_sample: List[str] = []

        # 1. Elkinematics Suite (All non-digit kinematic recordings)
        elk_key = "elkinematics_train" if is_train else "elkinematics_val"
        targets_for_sample.append(elk_key)
        stats["cohort_samples"][elk_key] += 1
        stats["class_counts"][elk_key]["typical" if is_typical else "atypical"] += 1

        # 2. DHRC Suite (Strictly isolated Latin letters)
        if is_letter:
            dhrc_key = "dhrc_train" if is_train else "dhrc_val"
            targets_for_sample.append(dhrc_key)
            stats["cohort_samples"][dhrc_key] += 1
            stats["class_counts"][dhrc_key]["typical" if is_typical else "atypical"] += 1

        # Record expected files and copy/sync
        extensions = [".csv", ".png", ".meta.json"]
        for target_key in targets_for_sample:
            dest_dir = TARGET_DESTINATIONS[target_key]
            for ext in extensions:
                fname = f"{bn}{ext}"
                src_path = os.path.join(src_dir, fname)
                dest_path = os.path.join(dest_dir, fname)

                if os.path.isfile(src_path):
                    expected_files[target_key].add(fname)

                    if force:
                        if not dry_run:
                            shutil.copy2(src_path, dest_path)
                        stats["copied_new"] += 1
                    elif is_file_up_to_date(src_path, dest_path):
                        stats["skipped_up_to_date"] += 1
                    else:
                        is_update = os.path.isfile(dest_path)
                        if not dry_run:
                            shutil.copy2(src_path, dest_path)
                        if is_update:
                            stats["updated_modified"] += 1
                            if verbose and stats["updated_modified"] <= 5:
                                print(f"[UPDATE] Overwriting modified sample: {target_key}/{fname}")
                        else:
                            stats["copied_new"] += 1
                            if verbose and stats["copied_new"] <= 5:
                                print(f"[COPY] Added new sample: {target_key}/{fname}")

    # Reconcile and prune orphans in target directories
    if prune:
        for target_key, dest_dir in TARGET_DESTINATIONS.items():
            num_pruned = prune_orphans(
                dest_dir=dest_dir,
                expected_filenames=expected_files[target_key],
                dry_run=dry_run,
                verbose=verbose,
            )
            stats["pruned_orphans"] += num_pruned

    if verbose:
        print("\n" + "=" * 80)
        print("RECONCILIATION & SYNC SUMMARY:")
        print("=" * 80)
        print(f"Total Source Samples Evaluated:  {stats['total_source_samples']}")
        print(f"Skipped Numerals (Zero-Digit):  {stats['skipped_digits']}")
        print(f"Files Already Up-to-Date (Skip): {stats['skipped_up_to_date']}")
        print(f"New Files Copied:                {stats['copied_new']}")
        print(f"Modified Files Updated:          {stats['updated_modified']}")
        print(f"Orphaned Files Pruned:           {stats['pruned_orphans']}")
        print("-" * 80)
        print(f"{'Target Cohort':<28} | {'Total Samples':<14} | {'Typical (0)':<12} | {'Atypical (1)':<12}")
        print("-" * 80)
        for key in ["dhrc_train", "dhrc_val", "elkinematics_train", "elkinematics_val"]:
            tot = stats["cohort_samples"][key]
            c_typ = stats["class_counts"][key]["typical"]
            c_atyp = stats["class_counts"][key]["atypical"]
            print(f"{key:<28} | {tot:<14} | {c_typ:<12} | {c_atyp:<12}")
        print("=" * 80)

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Reconcile and incrementally synchronize training/validation cohorts."
    )
    parser.add_argument(
        "--sources",
        nargs="+",
        default=[DATASET_DIR, HUAWEI_DATASET_DIR],
        help=f"Source directories to aggregate (default: {DATASET_DIR} {HUAWEI_DATASET_DIR})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate reconciliation and display diffs without writing files.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-copy of all files regardless of existence or timestamps.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Purge all files in destination folders before synchronizing.",
    )
    parser.add_argument(
        "--no-prune",
        action="store_true",
        help="Do not prune orphaned files that no longer exist in sources.",
    )

    args = parser.parse_args()

    reconcile_and_sync(
        source_dirs=args.sources,
        dry_run=args.dry_run,
        force=args.force,
        clean=args.clean,
        prune=not args.no_prune,
        verbose=True,
    )


if __name__ == "__main__":
    main()
