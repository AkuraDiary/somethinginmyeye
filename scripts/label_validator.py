#!/usr/bin/env python3
"""
Interactive Terminal Label Validator for Elkinematics Handwriting Datasets.
Enables human-in-the-loop inspection and rapid relabeling of samples.
Displays stroke images via native macOS QuickLook preview and renames
the associated triplet (.csv, .png, .meta.json) atomically.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import signal
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

# Base Directories and Config
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from config import DATASET_DIR, HUAWEI_DATASET_DIR


class TerminalLabelValidator:
    def __init__(
        self,
        target_dir: str = DATASET_DIR,
        annotator: Optional[str] = None,
        mode: Optional[str] = None,
        single_char_only: bool = False,
        search_query: Optional[str] = None,
        resume: bool = True,
        viewer: str = "qlmanage",
        reverse: bool = False,
    ):
        self.target_dir = os.path.abspath(target_dir)
        self.annotator_filter = annotator.lower() if annotator and annotator.lower() != "all" else None
        self.mode_filter = mode.lower() if mode and mode.lower() != "all" else None
        self.single_char_only = single_char_only
        self.search_query = search_query.lower() if search_query else None
        self.resume = resume
        self.viewer = viewer
        self.reverse = reverse

        self.state_file = os.path.join(self.target_dir, ".reviewed_labels.json")
        self.reviewed_set = self._load_review_state()
        self.active_viewer_proc: Optional[subprocess.Popen] = None

        # Clean exit on Ctrl+C
        signal.signal(signal.SIGINT, self._handle_interrupt)

    def _load_review_state(self) -> set:
        """Load set of already validated sample basenames."""
        if os.path.isfile(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return set(data)
            except Exception:
                pass
        return set()

    def _save_review_state(self):
        """Persist review progress to disk."""
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(sorted(list(self.reviewed_set)), f, indent=2)
        except Exception as e:
            print(f"[WARNING] Could not save review state: {e}")

    def _handle_interrupt(self, sig, frame):
        """Ensure preview window is closed before exiting."""
        self._close_preview()
        self._save_review_state()
        print("\n\nSession terminated by user. Progress saved.")
        sys.exit(0)

    def _close_preview(self):
        """Terminate active preview process."""
        if self.active_viewer_proc is not None:
            try:
                self.active_viewer_proc.terminate()
                self.active_viewer_proc.wait(timeout=0.5)
            except Exception:
                try:
                    self.active_viewer_proc.kill()
                except Exception:
                    pass
            self.active_viewer_proc = None

    def _open_preview(self, png_path: str):
        """Open floating preview window for image."""
        self._close_preview()
        if not os.path.isfile(png_path):
            return

        if self.viewer == "qlmanage" and sys.platform == "darwin":
            try:
                self.active_viewer_proc = subprocess.Popen(
                    ["/usr/bin/qlmanage", "-p", png_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception as e:
                print(f"[WARNING] Failed to open QuickLook: {e}")
        elif self.viewer == "open" and sys.platform == "darwin":
            try:
                self.active_viewer_proc = subprocess.Popen(
                    ["/usr/bin/open", "-a", "Preview", png_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception as e:
                print(f"[WARNING] Failed to open Preview: {e}")

    @staticmethod
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
            label = "_".join(parts[2:-3])
            has_two_ts = True
        elif parts[-1].isdigit():
            server_ts = parts[-1]
            client_ts = None
            annotator = parts[-2]
            label = "_".join(parts[2:-2])
            has_two_ts = False
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
            "has_two_ts": has_two_ts,
        }

    @staticmethod
    def sanitize_label(label: str) -> str:
        """Sanitize user label for filesystem compatibility."""
        cleaned = re.sub(r'[\/\\:\*\?"<>\|\s]+', '_', label.strip())
        return cleaned.strip("_")

    def collect_samples(self) -> List[Dict[str, Any]]:
        """Scan directory and filter candidate samples for review."""
        if not os.path.isdir(self.target_dir):
            raise FileNotFoundError(f"Target directory not found: {self.target_dir}")

        csv_files = []
        for entry in os.scandir(self.target_dir):
            if entry.is_file() and entry.name.endswith(".csv"):
                csv_files.append(entry.name[:-4])

        samples = []
        for bn in csv_files:
            info = self.parse_filename(bn)
            if not info:
                continue

            # Filtering
            if self.annotator_filter and info["annotator"].lower() != self.annotator_filter:
                continue
            if self.mode_filter and info["mode"].lower() != self.mode_filter:
                continue
            if self.single_char_only and len(info["label"]) > 1:
                continue
            if self.search_query and (self.search_query not in info["label"].lower() and self.search_query not in bn.lower()):
                continue

            samples.append(info)

        samples.sort(key=lambda s: s["base_name"], reverse=self.reverse)
        return samples

    def get_sample_details(self, sample_info: Dict[str, Any]) -> Dict[str, Any]:
        """Read CSV stroke stats and meta.json prompt information."""
        bn = sample_info["base_name"]
        csv_path = os.path.join(self.target_dir, f"{bn}.csv")
        png_path = os.path.join(self.target_dir, f"{bn}.png")
        meta_path = os.path.join(self.target_dir, f"{bn}.meta.json")

        num_points = 0
        latency_ms = 0.0
        if os.path.isfile(csv_path):
            try:
                with open(csv_path, "r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    num_points = len(rows)
                    if rows and "latency" in rows[0]:
                        latency_ms = float(rows[0]["latency"])
            except Exception:
                pass

        meta_prompt = ""
        meta_level = ""
        if os.path.isfile(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta_data = json.load(f)
                    meta_prompt = meta_data.get("prompt", "")
                    meta_level = meta_data.get("task_level", "")
            except Exception:
                pass

        return {
            "num_points": num_points,
            "latency_ms": latency_ms,
            "meta_prompt": meta_prompt,
            "meta_level": meta_level,
            "has_png": os.path.isfile(png_path),
            "has_meta": os.path.isfile(meta_path),
            "png_path": png_path,
            "csv_path": csv_path,
            "meta_path": meta_path,
        }

    def rename_sample(self, sample_info: Dict[str, Any], new_label: str) -> Optional[str]:
        """
        Atomically rename CSV, PNG, and meta.json triplet to new label.
        Updates internal meta.json fields accordingly.
        """
        old_bn = sample_info["base_name"]
        dataset = sample_info["dataset"]
        mode = sample_info["mode"]
        annotator = sample_info["annotator"]
        client_ts = sample_info["client_ts"]
        server_ts = sample_info["server_ts"]

        if sample_info["has_two_ts"]:
            new_bn = f"{dataset}_{mode}_{new_label}_{annotator}_{client_ts}_{server_ts}"
        else:
            new_bn = f"{dataset}_{mode}_{new_label}_{annotator}_{server_ts}"

        if new_bn == old_bn:
            return old_bn

        # Check for destination collision
        target_csv = os.path.join(self.target_dir, f"{new_bn}.csv")
        if os.path.exists(target_csv):
            print(f"[COLLISION ERROR] Target file already exists: {new_bn}.csv")
            return None

        # Rename files
        extensions = [".csv", ".png", ".meta.json"]
        renamed_files = []
        try:
            for ext in extensions:
                old_f = os.path.join(self.target_dir, f"{old_bn}{ext}")
                new_f = os.path.join(self.target_dir, f"{new_bn}{ext}")
                if os.path.isfile(old_f):
                    os.rename(old_f, new_f)
                    renamed_files.append((old_f, new_f))

            # Update meta.json contents if exists
            new_meta_f = os.path.join(self.target_dir, f"{new_bn}.meta.json")
            if os.path.isfile(new_meta_f):
                try:
                    with open(new_meta_f, "r", encoding="utf-8") as f:
                        meta_dict = json.load(f)
                    meta_dict["label"] = new_label
                    meta_dict["base_filename"] = new_bn
                    with open(new_meta_f, "w", encoding="utf-8") as f:
                        json.dump(meta_dict, f, ensure_ascii=False, indent=2)
                except Exception as err:
                    print(f"[WARNING] Could not update meta.json internal fields: {err}")

            return new_bn
        except Exception as err:
            print(f"[RENAME ERROR] Rollback triggered: {err}")
            for old_f, new_f in reversed(renamed_files):
                if os.path.isfile(new_f):
                    os.rename(new_f, old_f)
            return None

    def run(self):
        """Main interactive validation loop."""
        all_samples = self.collect_samples()
        total_matched = len(all_samples)

        if total_matched == 0:
            print(f"No samples matching criteria found in {self.target_dir}.")
            return

        # Filter out reviewed if resume is enabled
        if self.resume:
            pending_samples = [s for s in all_samples if s["base_name"] not in self.reviewed_set]
        else:
            pending_samples = all_samples

        print("=" * 70)
        print("Elkinematics Dataset Label Validator (Terminal Edition)")
        print(f"Target Directory:    {self.target_dir}")
        print(f"Total Matched:       {total_matched}")
        print(f"Already Reviewed:    {len(self.reviewed_set)}")
        print(f"Pending Review:      {len(pending_samples)}")
        print(f"Active Viewer:       {self.viewer} (floating QuickLook window)")
        print("=" * 70)

        idx = 0
        while idx < len(pending_samples):
            sample = pending_samples[idx]
            bn = sample["base_name"]
            details = self.get_sample_details(sample)

            # Open floating image preview
            if details["has_png"]:
                self._open_preview(details["png_path"])

            print("\n" + "-" * 70)
            progress_str = f"[{idx + 1} / {len(pending_samples)} pending | Total {total_matched}]"
            print(f"Sample {progress_str}")
            print(f"Filename:       {bn}.csv")
            print(f"Dataset Split:  {sample['dataset']}")
            print(f"Mode (Class):   {sample['mode']}")
            print(f"Annotator:      {sample['annotator']}")
            print(f"Current Label:  \033[1;36m{sample['label']}\033[0m")
            if details["meta_prompt"]:
                print(f"Meta Prompt:    \033[1;33m{details['meta_prompt']}\033[0m ({details['meta_level']})")
            print(f"Stroke Data:    {details['num_points']} points | Latency: {details['latency_ms']:.1f} ms")
            if not details["has_png"]:
                print("Image Status:   [MISSING PNG PREVIEW]")
            print("-" * 70)
            print("Commands:")
            print("  [Text]  : Type new label and press Enter to rename sample")
            print("  [Enter] : Confirm & keep current label, proceed to next")
            print("  [1]     : Skip this sample (do not mark as reviewed)")
            print("  [2]     : Go back to previous sample")
            print("  [3]     : Delete this sample (corrupt/unusable stroke)")
            print("  [0]     : Save review progress and quit")
            print("-" * 70)

            try:
                user_input = input("Enter choice: ").strip()
            except EOFError:
                break

            if user_input == "0":
                self._close_preview()
                self._save_review_state()
                print("\nReview session saved. Exiting.")
                return

            elif user_input == "1":
                print(f"Skipped: {bn}")
                idx += 1
                continue

            elif user_input == "2":
                if idx > 0:
                    idx -= 1
                    print("Moving back to previous sample.")
                else:
                    print("Already at the first sample.")
                continue

            elif user_input == "3":
                confirm = input(f"Are you sure you want to delete {bn}? (y/N): ").strip().lower()
                if confirm == "y":
                    for ext in [".csv", ".png", ".meta.json"]:
                        fp = os.path.join(self.target_dir, f"{bn}{ext}")
                        if os.path.isfile(fp):
                            os.remove(fp)
                    print(f"[DELETED] Removed {bn} from dataset.")
                    self.reviewed_set.discard(bn)
                    pending_samples.pop(idx)
                    continue
                else:
                    print("Deletion cancelled.")
                    continue

            elif user_input == "":
                # Keep current label
                print(f"[CONFIRMED] Retaining label: '{sample['label']}'")
                self.reviewed_set.add(bn)
                idx += 1

            else:
                # User provided new label
                clean_lbl = self.sanitize_label(user_input)
                if not clean_lbl:
                    print("[WARNING] Invalid empty label. Keeping current.")
                    continue

                new_bn = self.rename_sample(sample, clean_lbl)
                if new_bn:
                    print(f"[SUCCESS] Renamed to: \033[1;32m{new_bn}\033[0m")
                    self.reviewed_set.discard(bn)
                    self.reviewed_set.add(new_bn)
                    sample["base_name"] = new_bn
                    sample["label"] = clean_lbl
                    idx += 1
                else:
                    print("[ERROR] Rename failed. Please re-enter.")
                    continue

        self._close_preview()
        self._save_review_state()
        print("\n" + "=" * 70)
        print("All pending samples in this batch have been reviewed.")
        print("Review state successfully saved.")
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Interactive Terminal Label Validator for Elkinematics Datasets."
    )
    parser.add_argument(
        "--dir",
        type=str,
        default=DATASET_DIR,
        help=f"Target dataset directory to validate (default: {DATASET_DIR})",
    )
    parser.add_argument(
        "--annotator",
        type=str,
        default=None,
        help="Filter samples by annotator (e.g., Hakim, Galang, Yanto, Seta, all)",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default=None,
        help="Filter samples by mode (normal, dyslexia, dysgraphia, all)",
    )
    parser.add_argument(
        "--single-char-only",
        action="store_true",
        help="Filter samples whose current label is a single character (random letter)",
    )
    parser.add_argument(
        "--search",
        type=str,
        default=None,
        help="Filter samples by search substring in label or filename",
    )
    parser.add_argument(
        "--reverse",
        action="store_true",
        help="Iterate in reverse chronological order",
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Ignore previous review progress and re-check all samples",
    )
    parser.add_argument(
        "--reset-history",
        action="store_true",
        help="Clear saved review state history for the target directory",
    )
    parser.add_argument(
        "--viewer",
        type=str,
        default="qlmanage",
        choices=["qlmanage", "open", "none"],
        help="Image preview method: 'qlmanage' (default, macOS QuickLook), 'open' (Preview.app), 'none'",
    )

    args = parser.parse_args()

    target_dir = os.path.abspath(args.dir)
    state_file = os.path.join(target_dir, ".reviewed_labels.json")

    if args.reset_history and os.path.isfile(state_file):
        os.remove(state_file)
        print(f"Cleared review history: {state_file}")

    validator = TerminalLabelValidator(
        target_dir=target_dir,
        annotator=args.annotator,
        mode=args.mode,
        single_char_only=args.single_char_only,
        search_query=args.search,
        resume=not args.no_resume,
        viewer=args.viewer,
        reverse=args.reverse,
    )
    validator.run()


if __name__ == "__main__":
    main()
