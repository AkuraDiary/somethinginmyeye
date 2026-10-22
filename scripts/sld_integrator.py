"""
Specific Learning Disorder (SLD) Differential Integrator.
Synthesizes Kinematic Motoric Stream (Bi-LSTM), Orthographic Decoder (Reversals & Spelling),
and Cognitive Latency to output calibrated differential screening assessments in DSM-5.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import (
    CLASSIFICATION_THRESHOLD,
    COGNITIVE_LATENCY_THRESHOLD_MS,
    ENABLE_GRAMMAR_ANALYSIS,
    KINEMATIC_DYSGRAPHIA_WEIGHT,
    LATENCY_RISK_WEIGHT,
    REVERSAL_PENALTY_WEIGHT,
    SCALER_PATH,
    SPELLING_ERROR_WEIGHT,
)
from orthographic_decoder import evaluate_orthographic_accuracy
from universal_pipeline import unified_predict


def evaluate_syntactic_grammar(text: str, expected_text: str) -> Dict[str, Any]:
    """
    Modular Syntactic Grammar Evaluation.
    Activated when evaluating sentence or phrase level prompts.
    """
    words_input = text.strip().split()
    words_expected = expected_text.strip().split()

    word_count_diff = abs(len(words_input) - len(words_expected))
    grammar_penalty = min(word_count_diff * 0.25, 1.0)

    # Word order coherence check
    order_inversions = 0
    if len(words_input) > 1 and len(words_expected) > 1:
        for idx in range(min(len(words_input), len(words_expected))):
            if words_input[idx] != words_expected[idx]:
                order_inversions += 1

    normalized_syntax_score = min(grammar_penalty + (order_inversions * 0.2), 1.0)

    return {
        "grammar_active": True,
        "syntax_error_score": float(normalized_syntax_score),
        "word_count_expected": len(words_expected),
        "word_count_actual": len(words_input),
        "order_inversions": order_inversions,
    }


def evaluate_sld_differential(
    df: pd.DataFrame,
    model,
    expected_prompt: str = "bebek",
    decoded_text: Optional[str] = None,
    enable_grammar: Optional[bool] = None,
    scaler_path: str = SCALER_PATH,
) -> Dict[str, Any]:
    """
    Computes differential risk scores across Motor Dysgraphia and Dyslexia.
    Returns:
      - dysgraphia_risk_percentage: 0.0 to 100.0%
      - dyslexia_risk_percentage: 0.0 to 100.0%
      - dsm5_diagnosis: Clinically categorized diagnostic string
      - stream_breakdown: Granular features from kinematic and orthographic streams
    """
    if enable_grammar is None:
        enable_grammar = ENABLE_GRAMMAR_ANALYSIS

    # 1. Kinematic Motoric Stream (Bi-LSTM)
    kinematic_score, heatmap_array = unified_predict(
        df=df,
        model=model,
        version="v2",
        scaler_path=scaler_path,
    )

    # 2. Orthographic Stream (Reversals & Spelling)
    ortho_results = evaluate_orthographic_accuracy(
        df=df,
        expected_prompt=expected_prompt,
        decoded_text=decoded_text,
    )

    # 3. Cognitive Latency Stream (Working Memory / Initiation Delay)
    raw_latency_ms = float(df["latency"].iloc[0]) if "latency" in df.columns and len(df) > 0 else 0.0
    if raw_latency_ms > COGNITIVE_LATENCY_THRESHOLD_MS:
        latency_risk = min((raw_latency_ms - 1000.0) / 2000.0, 1.0)
    else:
        latency_risk = max((raw_latency_ms - 500.0) / 2000.0, 0.0)

    # 4. Syntactic Grammar Module (Optional Modular Switch)
    grammar_results: Dict[str, Any] = {"grammar_active": False, "syntax_error_score": 0.0}
    if enable_grammar and len(expected_prompt.split()) > 1:
        recognized_text = ortho_results.get("recognized_text", "")
        grammar_results = evaluate_syntactic_grammar(recognized_text, expected_prompt)

    # 5. Dual-Axis Risk Profiling (Mun & El-Yacoubi, 2026) with Confidence-Gated Arbitration (Kunhoth et al., 2024)
    # Axis 1: Motor Kinematic Risk (Bi-LSTM temporal pooling)
    dysgraphia_risk = kinematic_score * 100.0

    ortho_error = ortho_results["levenshtein_edit_distance"]
    # Reversal penalty is conditionally gated by classifier confidence (tau_rev >= 0.50)
    reversal_flag = 1.0 if ortho_results["reversal_detected"] else 0.0

    if enable_grammar and grammar_results["grammar_active"]:
        dyslexia_raw = (
            ortho_error * 0.35
            + reversal_flag * 0.35
            + latency_risk * 0.15
            + grammar_results["syntax_error_score"] * 0.15
        )
    else:
        # heuristic weighting with confidence gating (Mun & El-Yacoubi (2026))
        dyslexia_raw = (
            ortho_error * SPELLING_ERROR_WEIGHT
            + reversal_flag * REVERSAL_PENALTY_WEIGHT
            + latency_risk * LATENCY_RISK_WEIGHT
        )

    dyslexia_risk = min(max(dyslexia_raw * 100.0, 0.0), 100.0)

    # 6. Screening Indications & Non-Diagnostic Clinical Disclaimers (Mun & El-Yacoubi Standard)
    is_dysgraphic = bool(dysgraphia_risk >= (CLASSIFICATION_THRESHOLD * 100.0))
    is_dyslexic = bool(dyslexia_risk >= (CLASSIFICATION_THRESHOLD * 100.0))

    # Screening indications are probabilistic possibilities, not clinical verdicts.
    if is_dysgraphic and is_dyslexic:
        dsm5_diagnosis = "Potential Indicator: Multi-Domain Screening Risk (Motor & Orthographic)"
        clinical_severity = "Elevated Screening Indication in Multiple Domains"
    elif is_dysgraphic:
        dsm5_diagnosis = "Potential Indicator: Elevated Kinematic Variance (Motor Dysgraphia Risk)"
        clinical_severity = "Elevated Fine-Motor Kinematic Variance"
    elif is_dyslexic:
        dsm5_diagnosis = "Potential Indicator: Spelling / Reversal Variance (Dyslexic Dysgraphia Risk)"
        clinical_severity = "Elevated Orthographic Variance"
    else:
        dsm5_diagnosis = "Within Typical Screening Limits"
        clinical_severity = "Within Typical Limits"

    return {
        "screening_disclaimer": (
            "Automated screening indication only. This result does not constitute a clinical "
            "diagnosis and does not replace formal assessment by a licensed professional."
        ),
        "dsm5_diagnosis": dsm5_diagnosis,
        "clinical_severity": clinical_severity,
        "dysgraphia_risk_percentage": round(float(dysgraphia_risk), 1),
        "dyslexia_risk_percentage": round(float(dyslexia_risk), 1),
        "is_dysgraphic": is_dysgraphic,
        "is_dyslexic": is_dyslexic,
        "cognitive_latency_ms": raw_latency_ms,
        "latency_exceeds_threshold": bool(raw_latency_ms > COGNITIVE_LATENCY_THRESHOLD_MS),
        "reversal_detected": ortho_results["reversal_detected"],
        "reversal_description": ortho_results["reversal_description"],
        "recognized_text": ortho_results["recognized_text"],
        "expected_prompt": ortho_results["expected_prompt"],
        "heatmap": heatmap_array,
        "stream_breakdown": {
            "kinematic_score": round(float(kinematic_score), 4),
            "orthographic_error_score": round(float(ortho_results["orthographic_error_score"]), 4),
            "levenshtein_normalized": round(float(ortho_error), 4),
            "latency_risk_score": round(float(latency_risk), 4),
            "grammar_analysis": grammar_results,
        },
    }
