import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, GlobalAveragePooling1D, Dense, Dropout
import os
import pandas as pd
import numpy as np
from tensorflow.keras.layers import Input # Fixes that warning!

# Hyperparameters
MAX_TIMESTEPS = 500  # We will standardize all writing samples to 500 time-steps
FEATURES = 3         # We'll feed it 3 features: [velocity, pressure, touching]

def load_and_pad_data(data_dir):
    sequences = []
    labels = []
    
    for filename in os.listdir(data_dir):
        if not filename.endswith('.csv'):
            continue
            
        # 1. Grab the label based on the filename! (1 for dyslexia, 0 for normal)
        label = 1 if filename.startswith("dyslexia") else 0
        
        # 2. Load the CSV
        filepath = os.path.join(data_dir, filename)
        df = pd.read_csv(filepath)
        
        # 1: Calculate the 'velocity' column just like you did in preprocess.py
        df['dt'] = df['time'].diff().fillna(0) # calculate the time differences
        df['velocity'] = np.where(df['dt'] > 0, df['distance'] / df['dt'], 0)
        
        # 3. Extract just the 3 features we want to feed the Neural Network
        # Ensure these are the 3 columns your model expects!
        stroke_data = df[['velocity', 'pressure', 'touching']].values
        
        # 4. Pad or Truncate to MAX_TIMESTEPS (500)
        if len(stroke_data) > MAX_TIMESTEPS:
            stroke_data = stroke_data[:MAX_TIMESTEPS] # Truncate if too long
        else:
            # Pad with zeros if too short
            padding = np.zeros((MAX_TIMESTEPS - len(stroke_data), FEATURES))
            stroke_data = np.vstack((stroke_data, padding))
            
        sequences.append(stroke_data)
        labels.append(label)
        
    # Convert lists to TensorFlow-friendly NumPy arrays
    return np.array(sequences), np.array(labels)

def build_model():
    model = Sequential()
    
    # Add a Conv1D layer. 
    # 32 filters, kernel_size=3, activation='relu', and input_shape=(MAX_TIMESTEPS, FEATURES)
    model.add(Conv1D(filters=32, kernel_size=3, activation='relu'))
    model.add(Input(shape=(MAX_TIMESTEPS, FEATURES)))
    # a MaxPooling1D layer with pool_size=2
    # This downsamples the data, keeping only the most prominent features
    model.add(MaxPooling1D(pool_size=2))
    
    # Add another Conv1D layer. 
    # Give it 64 filters, kernel_size=3, activation='relu' (No input_shape needed this time)
    model.add(Conv1D(filters=64, kernel_size=3, activation='relu'))
    
    # Add a GlobalAveragePooling1D() layer. 
    # This squashes the remaining time-series data into a flat array.
    model.add(GlobalAveragePooling1D())
    
    # Add a standard Dense layer with 64 units/neurons and activation='relu'
    model.add(Dense(64, activation='relu'))
    
    #  Add a Dropout layer with rate=0.5 
    # This randomly turns off 50% of neurons during training to prevent "overfitting" (memorizing the data).
    model.add(Dropout(rate=0.5))
    
    # Add the final Dense layer with 1 unit and activation='sigmoid'
    # Sigmoid forces the final output to be a probability between 0.0 (Normal) and 1.0 (Dyslexic).
    model.add(Dense(1, activation='sigmoid'))
    
    
    # Finally, we compile the model
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    
    return model

if __name__ == "__main__":
    model = build_model()
    model.summary()
    print("Loading data...")
    # Point this to your data collector folder
    X, y = load_and_pad_data("../datasets/") 
    
    print(f"Data loaded! Shape of X: {X.shape}, Shape of y: {y.shape}")
    
    # Train the brain!
    # epochs=20 means it will read your data 20 times to learn the patterns.
    # validation_split=0.2 means it hides 20% of the data to test itself like a pop-quiz.
    print("Starting training...")
    history = model.fit(X, y, epochs=20, validation_split=0.2)
