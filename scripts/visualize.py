import pandas as pd
import matplotlib.pyplot as plt

def main():
    # 1. Read the CSV file using pandas
    file_path = '../data/mock_stroke.csv'
    df = pd.read_csv(file_path)
    
    # 2. Extract the X and Y columns
    x_coords = df['x']
    y_coords = df['y']
    
    # 3. Plot the data
    plt.figure(figsize=(8, 6))
    
    # Use plt.plot() to draw a line connecting the x and y coordinates
    # We will use a marker 'o' to show exactly where the pen was recorded
    plt.plot(x_coords, y_coords, marker='o', linestyle='-', color='b')
    
    # Let's add a title and labels
    plt.title("Kinematic Handwriting Visualization")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    
    # Invert the Y-axis! 
    # (Why? Because computer screens put Y=0 at the top, but normal graphs put it at the bottom. 
    # Handwriting data usually uses the screen's coordinate system).
    plt.gca().invert_yaxis()
    
    # Show the plot
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()