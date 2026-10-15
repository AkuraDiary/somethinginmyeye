import os
import time
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, auc, accuracy_score, recall_score, precision_score, f1_score
from tensorflow.keras.models import load_model

# Import centralized configuration and data pipeline
from config import MODEL_PATHS, DATASET_DIR, VAL_DATASET_DIR
from universal_pipeline import load_and_scale_universal, get_v0_data, get_v1_data, get_v2_data
from unified_evaluator import build_v0_baseline, build_v1_xai, build_v2_lstm


OUTPUT_DIR = "../evaluation_results"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ==========================================
# SWITCH: Set to True to generate 5.1 Learning Curves (requires brief retraining)
# Set to False to strictly load existing models from disk.
# ==========================================
RETRAIN_FOR_LEARNING_CURVES = True

def plot_learning_curves(histories, titles, train_times=None, infer_times=None):
    """ Learning Curves: Train vs Validation (Loss & Accuracy) - INDIVIDUAL & COMBINED"""
    
    # 1. INDIVIDUAL LEARNING CURVES
    for i, (history, title) in enumerate(zip(histories, titles)):
        safe_title = title.replace(" ", "_").replace("(", "").replace(")", "").replace("+", "plus")
        fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=300)
        
        # Build Title String with Timing if available
        time_str = ""
        if train_times and infer_times and i < len(train_times) and i < len(infer_times):
            time_str = f" | Train Time: {train_times[i]:.2f}s | Inference: {infer_times[i]:.2f}ms"
            
        fig.suptitle(f"{title} Learning Curve{time_str}", fontsize=14, fontweight='bold')
        
        # Accuracy Plot
        axes[0].plot(history.history['accuracy'], label='Train Acc', color='blue', lw=2)
        axes[0].plot(history.history['val_accuracy'], label='Val Acc', color='orange', lw=2, linestyle='--')
        axes[0].set_title("Accuracy")
        axes[0].set_ylabel("Accuracy")
        axes[0].set_xlabel("Epochs")
        axes[0].set_ylim([0, 1.05])
        axes[0].legend()
        axes[0].grid(True, linestyle=':', alpha=0.6)
        
        # Loss Plot
        axes[1].plot(history.history['loss'], label='Train Loss', color='red', lw=2)
        axes[1].plot(history.history['val_loss'], label='Val Loss', color='green', lw=2, linestyle='--')
        axes[1].set_title("Loss")
        axes[1].set_ylabel("Loss")
        axes[1].set_xlabel("Epochs")
        axes[1].legend()
        axes[1].grid(True, linestyle=':', alpha=0.6)

        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f"{safe_title}_Learning_Curve.png"), bbox_inches='tight')
        plt.close()
        
    # 2. COMBINED LEARNING CURVES (2x3 Grid)
    fig, axes = plt.subplots(2, 3, figsize=(15, 8), dpi=300)
    fig.suptitle(" Combined Model Learning Curves (Accuracy & Loss)", fontsize=16, fontweight='bold')
    
    for i, (history, title) in enumerate(zip(histories, titles)):
        
        time_str = ""
        if train_times and infer_times and i < len(train_times) and i < len(infer_times):
            time_str = f"\n(Train: {train_times[i]:.2f}s | Infer: {infer_times[i]:.2f}ms)"
            
        # Accuracy Row
        axes[0, i].plot(history.history['accuracy'], label='Train Acc', color='blue', lw=2)
        axes[0, i].plot(history.history['val_accuracy'], label='Val Acc', color='orange', lw=2, linestyle='--')
        axes[0, i].set_title(f"{title} - Accuracy{time_str}", fontsize=11)
        axes[0, i].set_ylabel("Accuracy" if i == 0 else "")
        axes[0, i].set_ylim([0, 1.05])
        axes[0, i].legend()
        axes[0, i].grid(True, linestyle=':', alpha=0.6)
        
        # Loss Row
        axes[1, i].plot(history.history['loss'], label='Train Loss', color='red', lw=2)
        axes[1, i].plot(history.history['val_loss'], label='Val Loss', color='green', lw=2, linestyle='--')
        axes[1, i].set_title(f"{title} - Loss", fontsize=11)
        axes[1, i].set_ylabel("Loss" if i == 0 else "")
        axes[1, i].set_xlabel("Epochs")
        axes[1, i].legend()
        axes[1, i].grid(True, linestyle=':', alpha=0.6)

    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "Combined_Learning_Curves.png"), bbox_inches='tight')
    plt.close()
    
    print("Saved individual and combined Learning Curves")


def plot_confusion_matrices(cms, titles):
    """Confusion Matrix - INDIVIDUAL"""
    for cm, title in zip(cms, titles):
        safe_title = title.replace(" ", "_").replace("(", "").replace(")", "").replace("+", "plus")
        plt.figure(figsize=(6, 5), dpi=300)
        
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
                    annot_kws={"size": 18, "weight": "bold"},
                    xticklabels=['Typical', 'Atypical'],
                    yticklabels=['Typical', 'Atypical'])
        
        plt.title(f"{title}\nConfusion Matrix", fontsize=14, fontweight='bold')
        plt.ylabel('Actual Classification', fontweight='bold')
        plt.xlabel('System Prediction', fontweight='bold')

        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f"{safe_title}_Confusion_Matrix.png"), bbox_inches='tight')
        plt.close()
    print("✅ Saved individual Confusion Matrices")


def plot_combined_roc(roc_data):
    """5.3 ROC Curve & AUC - INDIVIDUAL AND COMBINED"""
    colors = ['blue', 'green', 'darkorange']
    
    # INDIVIDUAL ROC CURVES
    for (fpr, tpr, roc_auc, label), color in zip(roc_data, colors):
        safe_title = label.replace(" ", "_").replace("(", "").replace(")", "").replace("+", "plus")
        plt.figure(figsize=(7, 6), dpi=300)
        plt.plot(fpr, tpr, color=color, lw=2.5, label=f'{label} (AUC = {roc_auc:.4f})')
        plt.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--', label='Random Guess')
        
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate (1 - Specificity)', fontweight='bold')
        plt.ylabel('True Positive Rate (Sensitivity / Recall)', fontweight='bold')
        plt.title(f'{label} ROC Curve', fontsize=14, fontweight='bold')
        plt.legend(loc="lower right")
        plt.grid(True, linestyle=':', alpha=0.6)
        
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f"{safe_title}_ROC_Curve.png"), bbox_inches='tight')
        plt.close()
    
    # COMBINED ROC CURVE (Standard for papers)
    plt.figure(figsize=(8, 6), dpi=300)
    for (fpr, tpr, roc_auc, label), color in zip(roc_data, colors):
        plt.plot(fpr, tpr, color=color, lw=2.5, label=f'{label} (AUC = {roc_auc:.4f})')
        
    plt.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--', label='Random Guess')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontweight='bold')
    plt.ylabel('True Positive Rate', fontweight='bold')
    plt.title('Combined Receiver Operating Characteristic (ROC-AUC)', fontsize=14, fontweight='bold')
    plt.legend(loc="lower right")
    plt.grid(True, linestyle=':', alpha=0.6)
    
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "Combined_ROC_AUC_Curve.png"), bbox_inches='tight')
    plt.close()
    print("✅ Saved individual and combined ROC Curves")

def process_predictions(model, X, y_raw):
    y_pred_probs = model.predict(X, verbose=0)
    if len(y_pred_probs.shape) == 3:
        y_pred_probs_flat = np.mean(y_pred_probs, axis=1).flatten()
    else:
        y_pred_probs_flat = y_pred_probs.flatten()
        
    y_pred_classes = (y_pred_probs_flat > 0.5).astype(int)
    
    if len(y_raw.shape) >= 2:
        y_true_flat = np.max(y_raw, axis=1).flatten()
    else:
        y_true_flat = y_raw.flatten()
        
    return y_true_flat, y_pred_probs_flat, y_pred_classes

def main():
    print(f"Starting Comprehensive JISEBI Evaluation Pipeline")
    print(f"Retrain for Learning Curves: {RETRAIN_FOR_LEARNING_CURVES}")
    
    from universal_pipeline import load_validation_with_train_scalers, train_with_tuning
    
    print("📁 Loading TRAINING dataset (for scalers and optional retraining)...")
    X_train_seq, X_train_lat, y_train = load_and_scale_universal(DATASET_DIR)
    
    print("📁 Loading VALIDATION dataset (strictly unseen for metrics)...")
    X_val_seq, X_val_lat, y_val = load_validation_with_train_scalers(VAL_DATASET_DIR)
    
    data_maps = [
        ("V0 (CNN Baseline)", MODEL_PATHS['v0'], build_v0_baseline, 
         get_v0_data(X_train_seq, y_train), get_v0_data(X_val_seq, y_val)),
        ("V1 (CNN + XAI)", MODEL_PATHS['v1'], build_v1_xai, 
         get_v1_data(X_train_seq, X_train_lat, y_train), get_v1_data(X_val_seq, X_val_lat, y_val)),
        ("V2 (Bi-LSTM)", MODEL_PATHS['v2'], build_v2_lstm, 
         get_v2_data(X_train_seq, X_train_lat, y_train), get_v2_data(X_val_seq, X_val_lat, y_val))
    ]
    
    cms = []
    roc_data = []
    titles = []
    histories = []
    train_times = []
    infer_times = []

    for name, model_path, build_fn, (X_tr, y_tr), (X_te, y_te) in data_maps:
        print(f"\n🧠 Evaluating {name}...")
        titles.append(name)
        
        if RETRAIN_FOR_LEARNING_CURVES:
            print("   -> Retraining model for 50 epochs with tuning to capture Learning Curves...")
            model = build_fn()
            
            start_train = time.time()
            model, history = train_with_tuning(model, X_tr, y_tr, X_te, y_te)
            train_time = time.time() - start_train
            
            # SAVE THE NEW MODEL SO WE DON'T NEED UNIFIED_EVALUATOR
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            model.save(model_path)
            print(f"   -> 💾 Model successfully saved to {model_path}")
            
            histories.append(history)
            train_times.append(train_time)
            
            print(f"   -> ⏱️ Training Time: {train_time:.2f} seconds")
        else:
            if not os.path.exists(model_path):
                print(f"Error: Model file not found at {model_path}. Skipping.")
                continue
            print(f"   -> Loading existing model from {model_path}...")
            model = load_model(model_path)
            train_times.append(0.0)
        
        # Extract predictions for CM and ROC purely on TEST data
        start_infer = time.time()
        y_true, y_prob, y_class = process_predictions(model, X_te, y_te)
        infer_time_ms = ((time.time() - start_infer) / len(X_te)) * 1000
        infer_times.append(infer_time_ms)
        print(f"   -> ⚡ Inference Time (per sample): {infer_time_ms:.2f} ms")
        
        cm = confusion_matrix(y_true, y_class)
        cms.append(cm)
        
        fpr, tpr, _ = roc_curve(y_true, y_prob)
        roc_auc = auc(fpr, tpr)
        roc_data.append((fpr, tpr, roc_auc, name))
        
        precision = precision_score(y_true, y_class)
        f1 = f1_score(y_true, y_class)
        
        print(f"   -> Acc: {accuracy_score(y_true, y_class)*100:.2f}% | Recall: {recall_score(y_true, y_class)*100:.2f}% | Prec: {precision*100:.2f}% | F1: {f1*100:.2f}% | AUC: {roc_auc:.4f}")

    print("\nGenerating Plots...")
    
    if RETRAIN_FOR_LEARNING_CURVES and len(histories) == 3:
        plot_learning_curves(histories, titles, train_times, infer_times)
        
    if cms and len(cms) == 3:
        plot_confusion_matrices(cms, titles)
    if roc_data:
        plot_combined_roc(roc_data)
    
    print(f"\n Done! Images saved to {OUTPUT_DIR}/")
    if not RETRAIN_FOR_LEARNING_CURVES:
        print("Note: Learning Curves were skipped. Set RETRAIN_FOR_LEARNING_CURVES = True in the script to generate them.")

if __name__ == "__main__":
    main()
