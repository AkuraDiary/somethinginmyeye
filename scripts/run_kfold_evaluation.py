import os
import time
import numpy as np
import tensorflow as tf
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import confusion_matrix, roc_curve, auc, accuracy_score, recall_score, precision_score, f1_score
import matplotlib.pyplot as plt
import seaborn as sns

from universal_pipeline import load_and_scale_universal, get_v0_data, get_v1_data, get_v2_data
from unified_evaluator import build_v0_baseline, build_v1_xai, build_v2_lstm
from config import DATASET_DIR

OUTPUT_DIR = "evaluation_results_kfold"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def process_predictions_kfold(model, X_test, y_test_raw):
    y_pred_probs = model.predict(X_test, verbose=0)
    if len(y_pred_probs.shape) == 3:
        y_pred_probs_flat = np.mean(y_pred_probs, axis=1).flatten()
    else:
        y_pred_probs_flat = y_pred_probs.flatten()
        
    y_pred_classes = (y_pred_probs_flat > 0.5).astype(int)
    
    if len(y_test_raw.shape) >= 2:
        y_true_flat = np.max(y_test_raw, axis=1).flatten()
    else:
        y_true_flat = y_test_raw.flatten()
        
    return y_true_flat, y_pred_probs_flat, y_pred_classes

def evaluate_with_kfold(name, build_fn, X_data, y_data, k=5):
    print(f"\n🧠 Running {k}-Fold Cross Validation for {name}...")
    kfold = StratifiedKFold(n_splits=k, shuffle=True, random_state=42)
    
    all_y_true = []
    all_y_prob = []
    all_y_class = []
    
    # Handle single input (V0) vs multiple inputs (V1/V2)
    is_multi_input = isinstance(X_data, list)
    
    if not is_multi_input:
        # For V0, y_data is 1D or 2D
        # StratifiedKFold needs 1D targets for splitting
        if len(y_data.shape) > 1 and y_data.shape[1] > 1:
            y_split_target = np.max(y_data, axis=1).flatten()
        else:
            y_split_target = y_data.flatten()
    else:
        if len(y_data.shape) > 1 and y_data.shape[1] > 1:
            y_split_target = np.max(y_data, axis=1).flatten()
        else:
            y_split_target = y_data.flatten()
            
    fold_no = 1
    
    # Use just the first input array's length to split indices
    split_basis = X_data[0] if is_multi_input else X_data
    
    for train_idx, test_idx in kfold.split(split_basis, y_split_target):
        print(f"   -> Fold {fold_no}/{k}...")
        
        # Split Data
        if is_multi_input:
            X_train = [x[train_idx] for x in X_data]
            X_test = [x[test_idx] for x in X_data]
        else:
            X_train = X_data[train_idx]
            X_test = X_data[test_idx]
            
        y_train, y_test = y_data[train_idx], y_data[test_idx]
        
        # Build fresh model and train
        model = build_fn()
        model.fit(X_train, y_train, epochs=20, batch_size=32, verbose=0)
        
        # Predict on UNSEEN test chunk
        y_true, y_prob, y_class = process_predictions_kfold(model, X_test, y_test)
        
        all_y_true.extend(y_true)
        all_y_prob.extend(y_prob)
        all_y_class.extend(y_class)
        
        fold_no += 1
        
    # Calculate final aggregated metrics
    cm = confusion_matrix(all_y_true, all_y_class)
    acc = accuracy_score(all_y_true, all_y_class)
    recall = recall_score(all_y_true, all_y_class)
    prec = precision_score(all_y_true, all_y_class)
    f1 = f1_score(all_y_true, all_y_class)
    
    fpr, tpr, _ = roc_curve(all_y_true, all_y_prob)
    roc_auc = auc(fpr, tpr)
    
    print(f"\n✅ {name} 5-Fold Results:")
    print(f"   -> Accuracy: {acc*100:.2f}% | Recall: {recall*100:.2f}% | Precision: {prec*100:.2f}% | F1: {f1*100:.2f}% | AUC: {roc_auc:.4f}")
    
    # Save Confusion Matrix image
    plt.figure(figsize=(6, 5), dpi=300)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
                annot_kws={"size": 18, "weight": "bold"},
                xticklabels=['Typical', 'Atypical'],
                yticklabels=['Typical', 'Atypical'])
    plt.title(f"{name} (5-Fold CV)\nConfusion Matrix", fontsize=14, fontweight='bold')
    plt.ylabel('Actual Classification', fontweight='bold')
    plt.xlabel('System Prediction', fontweight='bold')
    plt.tight_layout()
    safe_title = name.replace(" ", "_").replace("(", "").replace(")", "").replace("+", "plus")
    plt.savefig(os.path.join(OUTPUT_DIR, f"{safe_title}_KFold_CM.png"), bbox_inches='tight')
    plt.close()
    
    return fpr, tpr, roc_auc, name

def main():
    print("📁 Loading dataset for 5-Fold CV...")
    X_seq_scaled, X_lat_scaled, y = load_and_scale_universal(DATASET_DIR)
    
    data_maps = [
        ("V0 (CNN Baseline)", build_v0_baseline, get_v0_data(X_seq_scaled, y)),
        ("V1 (CNN + XAI)", build_v1_xai, get_v1_data(X_seq_scaled, X_lat_scaled, y)),
        ("V2 (Bi-LSTM)", build_v2_lstm, get_v2_data(X_seq_scaled, X_lat_scaled, y))
    ]
    
    roc_data = []
    
    for name, build_fn, (X_data, y_data) in data_maps:
        fpr, tpr, roc_auc, label = evaluate_with_kfold(name, build_fn, X_data, y_data, k=5)
        roc_data.append((fpr, tpr, roc_auc, label))
        
    # Plot Combined ROC Curve
    plt.figure(figsize=(8, 6), dpi=300)
    colors = ['blue', 'green', 'darkorange']
    for (fpr, tpr, roc_auc, label), color in zip(roc_data, colors):
        plt.plot(fpr, tpr, color=color, lw=2.5, label=f'{label} (AUC = {roc_auc:.4f})')
        
    plt.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--', label='Random Guess')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontweight='bold')
    plt.ylabel('True Positive Rate', fontweight='bold')
    plt.title('Combined ROC-AUC (5-Fold Cross Validation)', fontsize=14, fontweight='bold')
    plt.legend(loc="lower right")
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "Combined_KFold_ROC_AUC.png"), bbox_inches='tight')
    plt.close()
    print(f"\n🎉 All K-Fold evaluations complete! Images saved to {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
