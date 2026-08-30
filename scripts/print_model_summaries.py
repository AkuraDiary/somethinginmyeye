from unified_evaluator import build_v0_baseline, build_v1_xai, build_v2_lstm
from config import MODEL_PATHS
from tensorflow.keras.models import load_model
from config import *

def main():
    print("\n" + "="*65)
    print(" MODEL ARCHITECTURE SUMMARIES FOR JISEBI PAPER ")
    print("="*65)

    print("\n\n1. V0 (BASELINE CNN)")
    v0 = load_model(MODEL_PATHS['v0'])
    # # v0 = build_v0_baseline()
    v0.summary()

    print("\n\n2. V1 (CNN + XAI)")
    v1 = load_model(MODEL_PATHS['v1'])
    # v1 = build_v1_xai()
    v1.summary()

    print("\n\n3. V2 (Bi-LSTM)")
    v2 = load_model(MODEL_PATHS['v2'])
    # v2 = build_v2_lstm()
    v2.summary()

if __name__ == "__main__":
    main()
