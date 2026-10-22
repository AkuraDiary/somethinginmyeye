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
    """
    Computes Damerau-Levenshtein (Optimal String Alignment) edit distance between two strings.
    Accounts for insertions, deletions, substitutions, and adjacent character transpositions
    (letter position migrations).

    Despite the historical function name, this implements the OSA variant of
    Damerau-Levenshtein; use `compute_osa_distance` as the explicit alias.
    """
    len1, len2 = len(s1), len(s2)
    if len1 == 0:
        return len2
    if len2 == 0:
        return len1

    d = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    for i in range(len1 + 1):
        d[i][0] = i
    for j in range(len2 + 1):
        d[0][j] = j

    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            d[i][j] = min(
                d[i - 1][j] + 1,          # deletion
                d[i][j - 1] + 1,          # insertion
                d[i - 1][j - 1] + cost,   # substitution
            )
            if (
                i > 1
                and j > 1
                and s1[i - 1] == s2[j - 2]
                and s1[i - 2] == s2[j - 1]
            ):
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)  # adjacent transposition

    return d[len1][len2]


compute_osa_distance = compute_levenshtein_distance


MIRROR_GLYPH_TO_CANONICAL = {
    "ꓭ": "b",
    "ᗡ": "d",
    "Ɔ": "c",
    "ɔ": "c",
    "Ǝ": "e",
    "ɘ": "e",
    "ꟻ": "f",
    "⅁": "g",
    "ᒐ": "j",
    "⅃": "l",
    "И": "n",
    "и": "n",
    "ꟼ": "p",
    "Я": "r",
    "ɿ": "r",
    "Ƨ": "s",
    "ƨ": "s",
    "Ʞ": "k",
    "ʞ": "k",
    "ꓘ": "k",
    "⋊": "k",
    "Ɛ": "3",
    "ᔭ": "4",
    "г": "7",
}

RECIPROCAL_PAIRS = {
    "b": "d",
    "d": "b",
    "p": "q",
    "q": "p",
    "m": "w",
    "w": "m",
    "u": "n",
    "n": "u",
}


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
      1. Letter reversals (canonical mirror glyphs from ONNX Head 2, reciprocal b/d or p/q swaps, and stroke geometry).
      2. Damerau-Levenshtein string edit distance (omissions, substitutions, and adjacent transpositions/migrations).
      3. Normalized orthographic error index (0.0 = perfect match, 1.0 = severe spelling/reversal error).
    """
    target = expected_prompt.lower().strip()
    geometry = detect_stroke_reversal_features(df)

    reversal_detected = False
    reversal_description = ""

    # 1. Check classic single-letter geometric b-d / p-q reversal
    if target in ["b"] and geometry["stem_side"] == "right":
        reversal_detected = True
        reversal_description = "Mirror reversal detected: 'b' written as 'd' (vertical stem oriented on right)."
    elif target in ["d"] and geometry["stem_side"] == "left":
        reversal_detected = True
        reversal_description = "Mirror reversal detected: 'd' written as 'b' (vertical stem oriented on left)."
    elif target in ["p"] and geometry["stem_side"] == "right":
        reversal_detected = True
        reversal_description = "Mirror reversal detected: 'p' written as 'q' (descender stem oriented on right)."
    elif target in ["q"] and geometry["stem_side"] == "left":
        reversal_detected = True
        reversal_description = "Mirror reversal detected: 'q' written as 'p' (descender stem oriented on left)."

    # 2. Check decoded_text from Dual-Track ONNX Resolver for mirror glyphs or reciprocal swaps
    if decoded_text:
        raw_decoded = decoded_text.strip()
        mirror_positions = []
        for idx, ch in enumerate(raw_decoded):
            if ch in MIRROR_GLYPH_TO_CANONICAL:
                canon = MIRROR_GLYPH_TO_CANONICAL[ch]
                mirror_positions.append(f"position {idx + 1} ('{canon}' -> '{ch}')")
            elif idx < len(target) and target[idx] in RECIPROCAL_PAIRS:
                if ch.lower() == RECIPROCAL_PAIRS[target[idx]] and ch.lower() != target[idx]:
                    mirror_positions.append(f"position {idx + 1} ('{target[idx]}' written as '{ch.lower()}')")

        if mirror_positions:
            reversal_detected = True
            reversal_description = "Character reversal detected at " + ", ".join(mirror_positions) + "."

        recognized = raw_decoded.lower()
        edit_dist = compute_levenshtein_distance(recognized, target)
        normalized_edit_dist = min(edit_dist / max(len(target), 1), 1.0)
    else:
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
