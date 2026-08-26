import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, GlobalAveragePooling1D, Dense, Dropout

# Hyperparameters
MAX_TIMESTEPS = 500  # We will standardize all writing samples to 500 time-steps
FEATURES = 3         # We'll feed it 3 features: [velocity, pressure, touching]

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
    # Let's instantiate your brain and print its architecture!
    model = build_model()
    model.summary()