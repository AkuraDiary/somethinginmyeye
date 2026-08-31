import requests
import time
import json
import statistics
import os
import glob
import random
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

SERVER_URL = "http://127.0.0.1:8000/analyze"
OUTPUT_DIR = "../evaluation_results"
DATASET_DIR = "../val_datasets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_random_payload():
    """Picks a random CSV file from the dataset and converts it to JSON payload"""
    csv_files = glob.glob(os.path.join(DATASET_DIR, "*.csv"))
    if not csv_files:
        print("⚠️ No CSV files found in datasets/. Using fallback dummy data.")
        # Fallback dummy data
        dummy_stroke = []
        current_time = 1000
        for i in range(50):
            dummy_stroke.append({
                "x": 100 + i, "y": 200 + i, "time": current_time,
                "pressure": 0.5, "tiltX": 0, "tiltY": 0, "latency": 15
            })
            current_time += 16
        return dummy_stroke

    random_file = random.choice(csv_files)
    df = pd.read_csv(random_file)
    
    # Ensure it's valid for the server payload
    df = df.fillna(0) # handle NaNs
    return df.to_dict(orient='records')

def test_functional(report_lines):
    print("--- FUNCTIONAL TESTING ---")
    report_lines.append("--- FUNCTIONAL TESTING ---")
    try:
        payload = get_random_payload()
        print(f"   -> Testing with real randomized payload ({len(payload)} strokes)")
        response = requests.post(SERVER_URL, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "probability" in data and "is_dyslexic" in data and "heatmap" in data:
                msg = "PASSED: API returned Status 200 and correct JSON structure."
                ai_msg = f"   -> AI Prediction: {data['is_dyslexic']} (Prob: {data['probability']:.4f})"
                print(msg)
                print(ai_msg)
                report_lines.extend([msg, ai_msg])
                return True
            else:
                msg = "❌ FAILED: Missing keys in JSON response."
                print(msg)
                report_lines.append(msg)
        else:
            msg = f"❌ FAILED: Server returned HTTP {response.status_code}"
            print(msg)
            report_lines.append(msg)
    except Exception as e:
        msg = f"❌ FAILED: Connection error. Is the Flask server running? {e}"
        print(msg)
        report_lines.append(msg)
    return False

def single_request():
    start = time.time()
    try:
        payload = get_random_payload()
        resp = requests.post(SERVER_URL, json=payload, timeout=20)
        status = resp.status_code
    except:
        status = 500
    end = time.time()
    return end - start, status

def test_non_functional(report_lines, num_requests=300, concurrent=10):
    header = f"\n--- NON-FUNCTIONAL TESTING (Performance & Load) ---"
    setup_msg = f"Sending {num_requests} requests ({concurrent} concurrent threads) using random real datasets..."
    print(header)
    print(setup_msg)
    report_lines.extend([header, setup_msg])
    
    latencies = []
    success_count = 0
    
    start_total = time.time()
    with ThreadPoolExecutor(max_workers=concurrent) as executor:
        results = list(executor.map(lambda _: single_request(), range(num_requests)))
        
    total_time = time.time() - start_total
    
    for latency, status in results:
        if status == 200:
            latencies.append(latency)
            success_count += 1
            
    if len(latencies) > 0:
        stats = [
            f"PASSED: {success_count}/{num_requests} requests successful.",
            f"   -> Total Test Duration : {total_time:.2f} seconds",
            f"   -> Average Latency     : {statistics.mean(latencies):.4f} seconds/req",
            f"   -> Max Latency         : {max(latencies):.4f} seconds/req",
            f"   -> Min Latency         : {min(latencies):.4f} seconds/req",
            f"   -> System Throughput   : {success_count / total_time:.2f} requests/second"
        ]
        for line in stats:
            print(line)
            report_lines.append(line)
    else:
        msg = "❌ FAILED: No successful requests during load test."
        print(msg)
        report_lines.append(msg)

if __name__ == "__main__":
    report_lines = [
        f"WEB APP EVALUATION REPORT",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "="*40
    ]
    
    print("🚀 Starting Automated Web App Testing Pipeline...\n")
    if test_functional(report_lines):
        # simulate n requests with m concurrent users
        test_non_functional(report_lines, num_requests=500, concurrent=10)
    else:
        print("\nSkipping non-functional tests because functional tests failed.")
        report_lines.append("\n⚠️ Skipping non-functional tests because functional tests failed.")
        
    # Save report
    report_path = os.path.join(OUTPUT_DIR, "web_app_performance.txt")
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))
    print(f"\n📁 Report successfully saved to: {report_path}")
