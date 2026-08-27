import pandas as pd
import numpy as np


# Converts the raw CSV dataframe into the Golden 8 Features array
def analyze_stroke_data(csv_filepath):
    # 1. Load the data
    df = pd.read_csv(csv_filepath)
    
    # Safety checks for old files
    if "touching" not in df.columns: df["touching"] = True
    
    for col in ["tiltX", "tiltY", "latency"]:
        if col not in df.columns: df[col] = 0
    
    # Calculate the physics features
    df["dt"] = df["time"].diff().fillna(1)
    df.loc[df["dt"] == 0, "dt"] = 1
    
    df["delta_x"] = df["x"].diff().fillna(0)
    df["delta_y"] = df["y"].diff().fillna(0)
    df["distance"] = np.sqrt(df["delta_x"]**2 + df["delta_y"]**2)
    df["velocity"] = df["distance"] / df["dt"]
    df["acceleration"] = df["velocity"].diff().fillna(0) / df["dt"]
    df["jerk"] = df["acceleration"].diff().fillna(0) / df["dt"]
    
    # Extract EXACTLY our Golden 8 array
    golden_df = df[["delta_x", "delta_y", "pressure", "tiltX", "tiltY", "velocity", "acceleration", "jerk", 'latency']]
    
    # Fill any weird math errors (like dividing by zero) with 0
    golden_df = golden_df.fillna(0)
    return golden_df

if __name__ == "__main__":
    # Point this to a CSV file you downloaded from your web app!
    analyze_stroke_data("../data/normal_A_1787739691815.csv")