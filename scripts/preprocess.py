import pandas as pd
import numpy as np


def analyze_stroke_data(csv_filepath):
    # 1. Load the data
    df = pd.read_csv(csv_filepath)
    
    # 2. Calculate time differences between rows (Delta Time / dt)
    df['dt'] = df['time'].diff().fillna(0)
    
    # 3. Calculate distance between points (Delta Distance using Pythagorean theorem)
    df['dx'] = df['x'].diff().fillna(0)
    df['dy'] = df['y'].diff().fillna(0)
    
    # 4. Calculate Velocity (Distance / Time)
    # np.where prevents division-by-zero errors if two events fire at the exact same millisecond
    df['distance'] = np.sqrt(df['dx']**2 + df['dy']**2) 
    df['velocity'] = np.where(df['dt'] > 0, df['distance'] / df['dt'], 0)
    
    # Calculate "Writing Duration" 
    # Sum of the 'dt' column, but ONLY for rows where 'touching' == 1
    writing_duration = df['dt'].where(df['touching'] == 1, 0).sum()

    # Calculate "In-Air Pen Duration" (The pause time biomarker)
    # Sum of the 'dt' column, but ONLY for rows where 'touching' == 0
    in_air_duration = df['dt'].where(df['touching'] == 0, 0).sum()
    
    # TODO 3: Print the results!
    print(f"--- Analysis for: {csv_filepath} ---")
    print(f"Total Writing Duration : {writing_duration} ms")
    print(f"Total In-Air Pauses    : {in_air_duration} ms")
    print(f"Average Pen Velocity   : {df['velocity'].mean():.2f} px/ms")
    print("-" * 40)
    
    return df

if __name__ == "__main__":
    # Point this to a CSV file you downloaded from your web app!
    analyze_stroke_data("../data/normal_A_1787739691815.csv")