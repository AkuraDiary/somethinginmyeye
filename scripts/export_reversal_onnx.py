"""
Exports the Dual-Head Reversal Model to ONNX format and verifies numerical parity
with ONNX Runtime.
"""
import os
import sys

sys.path.insert(0, 'venv/lib/python3.12/site-packages')
os.environ['KERAS_HOME'] = '/tmp/keras'
os.environ['MPLCONFIGDIR'] = '/tmp/mplconfig'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import numpy as np

import tensorflow as tf
import tf2onnx
import onnx
import onnxruntime as ort

MODEL_KERAS_PATH = "scratch/dual_head_reversal_model.keras"
MODEL_ONNX_PATH = "scratch/dual_head_reversal.onnx"

def export_model_to_onnx():
    print(f"Loading Keras model from: {MODEL_KERAS_PATH}")
    if not os.path.exists(MODEL_KERAS_PATH):
        raise FileNotFoundError(f"Model file not found at: {MODEL_KERAS_PATH}")

    model = tf.keras.models.load_model(MODEL_KERAS_PATH)
    print("Keras model loaded successfully.")

    # Define input signature: (batch_size, 64, 8)
    input_signature = [
        tf.TensorSpec(shape=(None, 64, 8), dtype=tf.float32, name="trajectory_input")
    ]

    print(f"Converting model to ONNX format (opset 15)...")
    onnx_model, _ = tf2onnx.convert.from_keras(
        model, 
        input_signature=input_signature, 
        opset=15,
        output_path=MODEL_ONNX_PATH
    )

    onnx_size_kb = os.path.getsize(MODEL_ONNX_PATH) / 1024.0
    print(f"ONNX model saved to: {MODEL_ONNX_PATH}")
    print(f"Model file size: {onnx_size_kb:.2f} KB")

    # Verify with ONNX Runtime
    print("\nVerifying numerical parity with ONNX Runtime...")
    ort_session = ort.InferenceSession(MODEL_ONNX_PATH)
    
    # Generate test trajectory batch
    test_input = np.random.randn(4, 64, 8).astype(np.float32)

    # 1. Keras prediction
    keras_preds = model.predict(test_input, verbose=0)
    keras_char = keras_preds[0]
    keras_rev = keras_preds[1]

    # 2. ONNX Runtime prediction
    input_name = ort_session.get_inputs()[0].name
    ort_outputs = ort_session.run(None, {input_name: test_input})
    
    # Identify character and reversal outputs by shape
    if ort_outputs[0].shape[-1] == 62:
        ort_char, ort_rev = ort_outputs[0], ort_outputs[1]
    else:
        ort_rev, ort_char = ort_outputs[0], ort_outputs[1]

    diff_char = np.max(np.abs(keras_char - ort_char))
    diff_rev = np.max(np.abs(keras_rev - ort_rev))

    print(f"Max absolute discrepancy (Character Output): {diff_char:.2e}")
    print(f"Max absolute discrepancy (Reversal Output):  {diff_rev:.2e}")

    if diff_char < 1e-4 and diff_rev < 1e-4:
        print("Verification SUCCESS: Perfect numerical parity between Keras and ONNX Runtime!")
    else:
        print("Warning: Discrepancy exceeds standard tolerance.")

    return MODEL_ONNX_PATH

if __name__ == "__main__":
    export_model_to_onnx()
