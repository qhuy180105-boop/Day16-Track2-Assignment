#!/usr/bin/env python3
"""
LightGBM ML Benchmark Script for Credit Card Fraud Detection.
Used in Day16-Track2-Assignment Cloud AI Environment Setup.
"""

import os
import sys
import time
import json
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score, accuracy_score, precision_score, recall_score, f1_score
)

def log(msg):
    print(msg, flush=True)

def find_or_generate_dataset():
    possible_paths = [
        "creditcard.csv",
        "data/creditcard.csv",
        os.path.expanduser("~/ml-benchmark/creditcard.csv"),
        "/home/ubuntu/ml-benchmark/creditcard.csv"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            log(f"[Dataset] Found dataset at: {path}")
            return path, False
            
    log("[Dataset] creditcard.csv not found locally. Generating synthetic dataset matching Credit Card Fraud Detection schema (284,807 rows)...")
    np.random.seed(42)
    n_samples = 284807
    n_fraud = int(n_samples * 0.00172)
    
    # Generate features: Time, V1-V28, Amount
    time_feature = np.sort(np.random.uniform(0, 172792, n_samples))
    amount_feature = np.random.exponential(88.34, n_samples)
    
    features = {}
    features['Time'] = time_feature
    for i in range(1, 29):
        features[f'V{i}'] = np.random.normal(0, 1.0, n_samples)
    features['Amount'] = amount_feature
    
    # Introduce signal into fraud samples
    labels = np.zeros(n_samples, dtype=int)
    fraud_indices = np.random.choice(n_samples, n_fraud, replace=False)
    labels[fraud_indices] = 1
    
    for idx in fraud_indices:
        features['V1'][idx] -= 2.5
        features['V2'][idx] += 2.0
        features['V3'][idx] -= 3.0
        features['V4'][idx] += 2.5
        features['V14'][idx] -= 4.0
        features['V17'][idx] -= 3.5
        features['Amount'][idx] += 120.0

    df = pd.DataFrame(features)
    df['Class'] = labels
    
    os.makedirs("data", exist_ok=True)
    synth_path = "data/creditcard.csv"
    df.to_csv(synth_path, index=False)
    log(f"[Dataset] Synthetic dataset saved to {synth_path} ({df.shape[0]} rows, {df.shape[1]} columns)")
    return synth_path, True

def main():
    log("=" * 60)
    log("  LightGBM Benchmark - Credit Card Fraud Detection")
    log("=" * 60)
    
    # 1. Load Data
    t0 = time.time()
    dataset_path, is_synthetic = find_or_generate_dataset()
    df = pd.read_csv(dataset_path)
    data_load_time = time.time() - t0
    log(f"Dataset shape: {df.shape}")
    log(f"Class distribution:\n{df['Class'].value_counts()}")
    log(f"Data loading time: {data_load_time:.4f} seconds")
    
    X = df.drop(columns=['Class'])
    y = df['Class']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 2. Train LightGBM Model
    log("\nTraining LightGBM model...")
    model = lgb.LGBMClassifier(
        objective='binary',
        metric='auc',
        n_estimators=100,
        learning_rate=0.05,
        num_leaves=31,
        random_state=42,
        n_jobs=-1,
        verbose=-1
    )
    
    t_train_start = time.time()
    model.fit(X_train, y_train)
    training_time = time.time() - t_train_start
    log(f"Training completed in: {training_time:.4f} seconds")
    
    # 3. Evaluate Metrics
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_pred_proba >= 0.5).astype(int)
    
    auc_roc = float(roc_auc_score(y_test, y_pred_proba))
    accuracy = float(accuracy_score(y_test, y_pred))
    precision = float(precision_score(y_test, y_pred, zero_division=0))
    recall = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    best_iteration = int(model.best_iteration_) if hasattr(model, 'best_iteration_') and model.best_iteration_ else 100
    
    # 4. Measure Inference Performance
    single_sample = X_test.iloc[0:1]
    batch_sample = X_test.iloc[:1000]
    
    # Warmup
    _ = model.predict_proba(single_sample)
    
    # Measure 1 row latency (averaged over 100 runs)
    latencies = []
    for _ in range(100):
        t_start = time.perf_counter()
        _ = model.predict_proba(single_sample)
        latencies.append((time.perf_counter() - t_start) * 1000.0)  # ms
    inference_latency_single_row_ms = float(np.mean(latencies))
    
    # Measure 1000 rows throughput
    t_batch_start = time.perf_counter()
    _ = model.predict_proba(batch_sample)
    batch_time_sec = time.perf_counter() - t_batch_start
    throughput_qps = float(1000.0 / batch_time_sec) if batch_time_sec > 0 else 0.0
    
    # Build Output Results
    results = {
        "model": "LightGBM (LGBMClassifier)",
        "dataset": "Credit Card Fraud Detection",
        "is_synthetic": is_synthetic,
        "dataset_size": len(df),
        "train_size": len(X_train),
        "test_size": len(X_test),
        "metrics": {
            "data_load_time_seconds": round(data_load_time, 4),
            "training_time_seconds": round(training_time, 4),
            "best_iteration": best_iteration,
            "auc_roc": round(auc_roc, 6),
            "accuracy": round(accuracy, 6),
            "precision": round(precision, 6),
            "recall": round(recall, 6),
            "f1_score": round(f1, 6),
            "inference_latency_1_row_ms": round(inference_latency_single_row_ms, 4),
            "inference_throughput_1000_rows_qps": round(throughput_qps, 2)
        }
    }
    
    out_file = "benchmark_result.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
        
    log("\n" + "=" * 60)
    log("  Benchmark Summary Results")
    log("=" * 60)
    log(f"| Metric                           | Value                 |")
    log(f"|----------------------------------|-----------------------|")
    log(f"| Data Loading Time                | {data_load_time:.4f} s           |")
    log(f"| Training Time                    | {training_time:.4f} s           |")
    log(f"| Best Iteration                   | {best_iteration}                   |")
    log(f"| AUC-ROC                          | {auc_roc:.6f}              |")
    log(f"| Accuracy                         | {accuracy:.6f}              |")
    log(f"| Precision                        | {precision:.6f}              |")
    log(f"| Recall                           | {recall:.6f}              |")
    log(f"| F1-Score                         | {f1:.6f}              |")
    log(f"| Inference Latency (1 row)        | {inference_latency_single_row_ms:.4f} ms           |")
    log(f"| Inference Throughput (1000 rows) | {throughput_qps:.2f} QPS           |")
    log("=" * 60)
    log(f"Results exported to {out_file}\n")

if __name__ == "__main__":
    main()
