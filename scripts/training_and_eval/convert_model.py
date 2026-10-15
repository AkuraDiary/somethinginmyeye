import tensorflow as tf

# 1. Load your existing .keras model
keras_model_path = "../models/elkinematicV2.keras"
model = tf.keras.models.load_model(keras_model_path)

# 2. Initialize the TFLite converter
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# --- FIX CODE HERE ---
# Allow TFLite to fall back on standard TF ops for the LSTM layer
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS, # Standard TFLite ops
    tf.lite.OpsSet.SELECT_TF_OPS    # Fallback to TensorFlow ops for LSTM loops
]

# Prevent TFLite from trying to break down the LSTM tensor lists into unsupported formats
converter._experimental_lower_tensor_list_ops = False
# ----------------------

# 3. Enable optimizations
converter.optimizations = [tf.lite.Optimize.DEFAULT]

# 4. Convert and save
tflite_model = converter.convert()

# 5. Save the converted model to a file
tflite_model_path = "../models/elkinematicliteV2.tflite"
with open(tflite_model_path, "wb") as f:
    f.write(tflite_model)

print(f"Success! Model successfully converted and saved to {tflite_model_path}")
