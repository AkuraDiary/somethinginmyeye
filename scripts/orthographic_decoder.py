"""
Orthographic and Character Reversal Decoder for Dyslexia Screening.
Analyzes stroke trajectory geometry, detects letter reversals (such as b-d, p-q confusion),
and computes phonological spelling error distances against expected target prompts.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


def compute_levenshtein_distance(s1: str, s2: str) -> int:
    """Computes standard edit distance between two strings."""
    if len(s1) < len(s2):
        return compute_levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def detect_stroke_reversal_features(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Extracts geometric stroke indicators to detect mirror reversals (b vs d, p vs q).
    Evaluates:
      - Stem location: X-coordinate of vertical strokes relative to the bounding box center.
      - Loop location: Center of curvature/loops relative to the stem.
      - Horizontal stroke progression: Mean horizontal direction vectors.
    """
    if len(df) < 5 or "x" not in df.columns or "y" not in df.columns:
        return {
            "has_reversal": False,
            "stem_side": "unknown",
            "loop_side": "unknown",
            "reversal_confidence": 0.0,
        }

    x = df["x"].values
    y = df["y"].values

    x_min, x_max = np.min(x), np.max(x)
    y_min, y_max = np.min(y), np.max(y)
    width = max(x_max - x_min, 1.0)
    height = max(y_max - y_min, 1.0)

    x_center = (x_min + x_max) / 2.0
    y_center = (y_min + y_max) / 2.0

    # Identify vertical segments (potential stems)
    dx = np.diff(x)
    dy = np.diff(y)
    angles = np.arctan2(np.abs(dy), np.abs(dx)) * 180.0 / np.pi
    vertical_mask = angles > 60.0

    stem_side = "unknown"
    if np.any(vertical_mask):
        vert_x = x[:-1][vertical_mask]
        mean_vert_x = np.mean(vert_x)
        if mean_vert_x < x_center - 0.05 * width:
            stem_side = "left"
        elif mean_vert_x > x_center + 0.05 * width:
            stem_side = "right"
        else:
            stem_side = "center"

    # Identify loop curvature centroid
    horizontal_mask = angles < 30.0
    loop_side = "unknown"
    if np.any(horizontal_mask):
        horiz_x = x[:-1][horizontal_mask]
        mean_horiz_x = np.mean(horiz_x)
        if mean_horiz_x > x_center:
            loop_side = "right"
        elif mean_horiz_x < x_center:
            loop_side = "left"

    return {
        "stem_side": stem_side,
        "loop_side": loop_side,
        "width_height_ratio": float(width / height),
        "x_center": float(x_center),
        "y_center": float(y_center),
    }


def evaluate_orthographic_accuracy(
    df: pd.DataFrame,
    expected_prompt: str,
    decoded_text: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Evaluates phonological and spelling accuracy against expected prompt.
    Checks:
      1. Letter reversals (e.g. prompt 'b' written with loop on left -> mirror reversal).
      2. String edit distance between recognized character/word and expected prompt.
      3. Normalized orthographic error index (0.0 = perfect match, 1.0 = severe spelling/reversal error).
    """
    target = expected_prompt.lower().strip()
    geometry = detect_stroke_reversal_features(df)

    reversal_detected = False
    reversal_description = ""

    # Check classic b-d reversal
    if target in ["b"]:
        if geometry["stem_side"] == "right":
            reversal_detected = True
            reversal_description = "Mirror reversal detected: 'b' written as 'd' (vertical stem oriented on right)."
    elif target in ["d"]:
        if geometry["stem_side"] == "left":
            reversal_detected = True
            reversal_description = "Mirror reversal detected: 'd' written as 'b' (vertical stem oriented on left)."
    elif target in ["p"]:
        if geometry["stem_side"] == "right":
            reversal_detected = True
            reversal_description = "Mirror reversal detected: 'p' written as 'q' (descender stem oriented on right)."
    elif target in ["q"]:
        if geometry["stem_side"] == "left":
            reversal_detected = True
            reversal_description = "Mirror reversal detected: 'q' written as 'p' (descender stem oriented on left)."


    # Calculate edit distance if decoded text provided, otherwise infer from reversal
    if decoded_text:
        recognized = decoded_text.lower().strip()
        edit_dist = compute_levenshtein_distance(recognized, target)
        normalized_edit_dist = min(edit_dist / max(len(target), 1), 1.0)
    else:
        # Default estimation based on reversal flag and geometric properties
        if reversal_detected:
            normalized_edit_dist = 0.8
            recognized = target[::-1] if len(target) > 1 else ("d" if target == "b" else "b")
        else:
            normalized_edit_dist = 0.0
            recognized = target

    reversal_penalty = 0.4 if reversal_detected else 0.0
    orthographic_error_score = min(normalized_edit_dist + reversal_penalty, 1.0)

    return {
        "expected_prompt": target,
        "recognized_text": recognized,
        "reversal_detected": reversal_detected,
        "reversal_description": reversal_description,
        "levenshtein_edit_distance": normalized_edit_dist,
        "orthographic_error_score": float(orthographic_error_score),
    }
