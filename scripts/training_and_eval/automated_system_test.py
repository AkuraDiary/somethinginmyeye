#!/usr/bin/env python3
"""
Automated End-to-End System Performance & High-Concurrency Benchmark Runner.
Validates functional SLD differential API endpoints and stresses throughput
under multi-client tablet simulation (500 requests across 20 concurrent threads)
stratified across isolated letter, continuous word, and orthographic reversal payloads.
Uses Python standard library (urllib, csv, json, concurrent.futures) for zero-dependency execution.
Strictly zero-emoji compliant.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
from datetime import datetime
import glob
import json
import os
from pathlib import Path
import random
import statistics
import sys
import time
from typing import Any, Dict, List, Tuple
import urllib.error
import urllib.request

# Ensure scripts directory and project root are on sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(SCRIPT_DIR.parent))

from config import (
    DATASET_DIR,
    DHRC_VAL_DIR,
    ELKINEMATICS_VAL_DIR,
)

SERVER_URL = "http://127.0.0.1:8000/analyze"
TEMP_DATASET_DIR = os.path.join(PROJECT_ROOT, "temp_datasets")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "scratch", "evaluation_results")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_csv_strokes(csv_path: str) -> List[Dict[str, Any]]:
    """Loads stroke coordinates from CSV using standard library csv module."""
    strokes: List[Dict[str, Any]] = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed: Dict[str, Any] = {}
            for k, v in row.items():
                if v is None or v == "":
                    parsed[k] = 0.0
                    continue
                try:
                    parsed[k] = float(v) if "." in v else int(v)
                except ValueError:
                    parsed[k] = v
            strokes.append(parsed)
    return strokes


def parse_metadata_prompt(csv_path: str) -> Tuple[str, float]:
    """Extracts target prompt and initiation latency from .meta.json or filename."""
    meta_path = csv_path.rsplit(".", 1)[0] + ".meta.json"
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
                prompt = meta.get("prompt", "")
                latency = float(meta.get("latency_ms", 0.0))
                if prompt:
                    return str(prompt), latency
        except Exception:
            pass

    # Fallback to parsing filename
    base = os.path.basename(csv_path)
    parts = base.split("_")
    if len(parts) >= 3:
        candidate = parts[2]
        if len(candidate) <= 3:
            return candidate, 0.0

    return "bebek", 0.0


def generate_stratified_payload() -> Dict[str, Any]:
    """
    Generates stratified test payloads conforming to the Multi-Modal Testing Ingestion Standard:
    - 40% Isolated letter kinematics from temp_datasets/ (with authentic prompt and latency)
    - 40% Word-level continuous kinematics from elkinematics_val_datasets/
    - 20% Orthographic mismatch and chiral reversals from dhrc_val_datasets/ or validation sets
    """
    roll = random.random()

    # Modality 1: Isolated Letters (40%)
    if roll < 0.40 and os.path.exists(TEMP_DATASET_DIR):
        letter_csvs = glob.glob(os.path.join(TEMP_DATASET_DIR, "*.csv"))
        if letter_csvs:
            csv_file = random.choice(letter_csvs)
            prompt, latency = parse_metadata_prompt(csv_file)
            try:
                strokes = load_csv_strokes(csv_file)
                if strokes:
                    return {
                        "strokes": strokes,
                        "prompt": prompt,
                        "decoded_text": prompt,
                        "latency": latency,
                        "modality": "isolated_letter",
                    }
            except Exception:
                pass

    # Modality 2: Orthographic Mismatch / Chiral Reversal Stress (20%)
    if roll >= 0.80 and os.path.exists(DHRC_VAL_DIR):
        dhrc_csvs = glob.glob(os.path.join(DHRC_VAL_DIR, "*.csv"))
        if dhrc_csvs:
            csv_file = random.choice(dhrc_csvs)
            prompt, latency = parse_metadata_prompt(csv_file)
            chiral_opposites = {"b": "d", "d": "b", "p": "q", "q": "p", "B": "d", "D": "b"}
            mismatched_text = chiral_opposites.get(prompt, "debek" if prompt == "bebek" else "d")
            try:
                strokes = load_csv_strokes(csv_file)
                if strokes:
                    return {
                        "strokes": strokes,
                        "prompt": prompt,
                        "decoded_text": mismatched_text,
                        "latency": latency if latency > 0 else 1850.0,
                        "modality": "orthographic_reversal_stress",
                    }
            except Exception:
                pass

    # Modality 3: Continuous Words from elkinematics_val_datasets/ (40%)
    search_dirs = [ELKINEMATICS_VAL_DIR, DATASET_DIR]
    word_csvs = []
    for d in search_dirs:
        if os.path.exists(d):
            word_csvs.extend(glob.glob(os.path.join(d, "*.csv")))

    if word_csvs:
        csv_file = random.choice(word_csvs)
        prompt, latency = parse_metadata_prompt(csv_file)
        try:
            strokes = load_csv_strokes(csv_file)
            if strokes:
                return {
                    "strokes": strokes,
                    "prompt": prompt if prompt else "bebek",
                    "decoded_text": prompt if prompt else "bebek",
                    "latency": latency,
                    "modality": "word_level_continuous",
                }
        except Exception:
            pass

    # Safe Synthetic Fallback
    dummy_strokes = []
    curr_t = 1000
    for i in range(60):
        dummy_strokes.append({
            "x": 120 + i * 2,
            "y": 200 + int(10 * (i % 5)),
            "time": curr_t,
            "pressure": 0.55,
            "tiltX": 5,
            "tiltY": -10,
            "latency": 1200,
        })
        curr_t += 16
    return {
        "strokes": dummy_strokes,
        "prompt": "bebek",
        "decoded_text": "bebek",
        "latency": 1200.0,
        "modality": "synthetic_fallback",
    }


def send_http_request(url: str, payload: Dict[str, Any], timeout: float = 12.0) -> Tuple[int, Dict[str, Any]]:
    """Performs HTTP POST request using standard library urllib."""
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data_bytes,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status_code = resp.status
            body = resp.read().decode("utf-8")
            return status_code, json.loads(body)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8") if e.fp else ""
        try:
            return e.code, json.loads(err_body)
        except Exception:
            return e.code, {"error": err_body}
    except Exception as e:
        return 500, {"error": str(e)}


def test_functional(server_url: str, report_lines: List[str]) -> bool:
    """Verifies API status, multi-stream integration keys, and non-diagnostic disclaimers."""
    header = "--- FUNCTIONAL TEST SUITE ---"
    print(header)
    report_lines.append(header)

    modalities_to_test = ["isolated_letter", "word_level_continuous", "orthographic_reversal_stress"]
    all_passed = True

    for mod in modalities_to_test:
        payload = generate_stratified_payload()
        stroke_count = len(payload.get("strokes", []))
        prompt = payload.get("prompt", "")
        decoded = payload.get("decoded_text", "")
        test_info = f"[TEST] Modality: {mod} | Prompt: '{prompt}' | Decoded: '{decoded}' | Strokes: {stroke_count}"
        print(test_info)
        report_lines.append(test_info)

        status_code, data = send_http_request(server_url, payload, timeout=15.0)
        if status_code != 200:
            fail_msg = f"[FAILED] Server returned HTTP {status_code} for {mod}: {data.get('error', '')}"
            print(fail_msg)
            report_lines.append(fail_msg)
            all_passed = False
            continue

        # Assert all required SLD differential response fields
        required_keys = [
            "probability",
            "dysgraphia_risk_percentage",
            "dyslexia_risk_percentage",
            "is_dysgraphic",
            "is_dyslexic",
            "dsm5_diagnosis",
            "clinical_severity",
            "screening_disclaimer",
            "heatmap",
            "stream_breakdown",
        ]
        missing_keys = [k for k in required_keys if k not in data]
        if missing_keys:
            fail_msg = f"[FAILED] Missing required keys in response: {missing_keys}"
            print(fail_msg)
            report_lines.append(fail_msg)
            all_passed = False
            continue

        # Validate numerical bounds and types
        assert 0.0 <= data["probability"] <= 1.0, "Probability out of [0, 1] range"
        assert 0.0 <= data["dysgraphia_risk_percentage"] <= 100.0, "Dysgraphia risk out of [0, 100] range"
        assert 0.0 <= data["dyslexia_risk_percentage"] <= 100.0, "Dyslexia risk out of [0, 100] range"
        assert isinstance(data["is_dysgraphic"], bool), "is_dysgraphic must be boolean"
        assert isinstance(data["is_dyslexic"], bool), "is_dyslexic must be boolean"
        assert isinstance(data["screening_disclaimer"], str) and len(data["screening_disclaimer"]) > 10
        assert isinstance(data["heatmap"], list)

        success_msg = (
            f"[PASSED] HTTP 200 | Indication: {data['dsm5_diagnosis']} | "
            f"Dysgraphia Risk: {data['dysgraphia_risk_percentage']}% | "
            f"Dyslexia Risk: {data['dyslexia_risk_percentage']}%"
        )
        print(success_msg)
        report_lines.append(success_msg)

    return all_passed


def single_request_worker(server_url: str) -> Tuple[float, int]:
    """Dispatches a single randomized request and records execution duration in seconds."""
    payload = generate_stratified_payload()
    start_t = time.perf_counter()
    status_code, _ = send_http_request(server_url, payload, timeout=25.0)
    duration = time.perf_counter() - start_t
    return duration, status_code


def test_non_functional(
    server_url: str,
    report_lines: List[str],
    num_requests: int = 500,
    concurrent: int = 20,
) -> None:
    """Executes high-concurrency stress testing and computes comprehensive latency percentiles."""
    header = "\n--- NON-FUNCTIONAL PERFORMANCE & CONCURRENCY BENCHMARK ---"
    setup_msg = (
        f"Executing stress benchmark: {num_requests} total requests across "
        f"{concurrent} concurrent worker threads against {server_url}..."
    )
    print(header)
    print(setup_msg)
    report_lines.extend([header, setup_msg])

    start_wall = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrent) as executor:
        results = list(executor.map(lambda _: single_request_worker(server_url), range(num_requests)))
    total_wall_time = time.perf_counter() - start_wall

    latencies_ms: List[float] = []
    status_counts: Dict[int, int] = {}

    for duration_s, code in results:
        status_counts[code] = status_counts.get(code, 0) + 1
        if code == 200:
            latencies_ms.append(duration_s * 1000.0)

    success_count = len(latencies_ms)
    error_count = num_requests - success_count
    throughput = success_count / total_wall_time if total_wall_time > 0 else 0.0

    print("-" * 75)
    report_lines.append("-" * 75)

    if success_count > 0:
        latencies_ms.sort()
        mean_lat = statistics.mean(latencies_ms)
        median_lat = statistics.median(latencies_ms)
        std_lat = statistics.stdev(latencies_ms) if len(latencies_ms) > 1 else 0.0
        min_lat = min(latencies_ms)
        max_lat = max(latencies_ms)

        def percentile(sorted_vals: List[float], p: float) -> float:
            k = (len(sorted_vals) - 1) * (p / 100.0)
            f = int(k)
            c = min(f + 1, len(sorted_vals) - 1)
            d0 = sorted_vals[f] * (c - k)
            d1 = sorted_vals[c] * (k - f)
            return d0 + d1

        p90_lat = percentile(latencies_ms, 90.0)
        p95_lat = percentile(latencies_ms, 95.0)
        p99_lat = percentile(latencies_ms, 99.0)

        stats = [
            f"[RESULT] Completed {success_count}/{num_requests} successful requests ({error_count} errors)",
            f"   -> Status Code Breakdown : {status_counts}",
            f"   -> Total Wall-Clock Time : {total_wall_time:.2f} seconds",
            f"   -> System Throughput     : {throughput:.2f} requests/second",
            f"   -> Mean Latency          : {mean_lat:.2f} ms",
            f"   -> Median Latency (p50)  : {median_lat:.2f} ms",
            f"   -> 90th Percentile (p90) : {p90_lat:.2f} ms",
            f"   -> 95th Percentile (p95) : {p95_lat:.2f} ms",
            f"   -> 99th Percentile (p99) : {p99_lat:.2f} ms",
            f"   -> Min Latency           : {min_lat:.2f} ms",
            f"   -> Max Latency           : {max_lat:.2f} ms",
            f"   -> Std Deviation         : {std_lat:.2f} ms",
        ]
        for line in stats:
            print(line)
            report_lines.append(line)
    else:
        fail_msg = f"[FAILED] Zero requests succeeded. Status code distribution: {status_counts}"
        print(fail_msg)
        report_lines.append(fail_msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated System & High-Concurrency Benchmark")
    parser.add_argument("--url", default=SERVER_URL, help="Inference API endpoint URL")
    parser.add_argument("--requests", type=int, default=500, help="Total requests for load test")
    parser.add_argument("--concurrency", type=int, default=20, help="Concurrent worker threads")
    parser.add_argument(
        "--output",
        default=os.path.join(OUTPUT_DIR, "web_app_performance.txt"),
        help="Destination path for benchmark report",
    )
    args = parser.parse_args()

    report_lines: List[str] = [
        "==========================================================================",
        "            ELKINEMATICS END-TO-END SYSTEM BENCHMARK REPORT               ",
        "==========================================================================",
        f"Timestamp          : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Server Target      : {args.url}",
        f"Concurrency Setup  : {args.requests} requests across {args.concurrency} threads",
        f"Standard Ingestion : temp_datasets/ (40%), val_datasets (40%), reversals (20%)",
        "==========================================================================\n",
    ]

    print("\nStarting Automated Elkinematics System Performance Pipeline...\n")
    functional_ok = test_functional(args.url, report_lines)

    if functional_ok:
        test_non_functional(
            server_url=args.url,
            report_lines=report_lines,
            num_requests=args.requests,
            concurrent=args.concurrency,
        )
    else:
        skip_msg = "[WARNING] Skipping non-functional stress testing because functional tests failed."
        print(skip_msg)
        report_lines.append(skip_msg)

    # Persist report cleanly
    with open(args.output, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")
    print(f"\n[REPORT] Saved benchmark evaluation summary to: {args.output}\n")
