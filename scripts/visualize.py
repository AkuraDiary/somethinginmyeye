import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main():
  # 1. Read the CSV file
  file_path = "../datasets/normal_A.csv"
  df = pd.read_csv(file_path)

  # Normalize 'touching' to boolean
  df["touching"] = df["touching"].astype(bool)

  # 2. Derive instantaneous velocity from coordinates and time
  df["dt"] = df["time"].diff().fillna(0)
  df["dx"] = df["x"].diff().fillna(0)
  df["dy"] = df["y"].diff().fillna(0)
  df["speed"] = np.where(
      df["dt"] > 0, np.sqrt(df["dx"] ** 2 + df["dy"] ** 2) / df["dt"], 0
  )

  # 3. Set up the visualization grid
  fig = plt.figure(figsize=(15, 8))
  gs = fig.add_gridspec(2, 2, width_ratios=[1.3, 1])

  # --- Panel 1: 2D Spatial Trajectory ---
  ax_traj = fig.add_subplot(gs[:, 0])

  # Plot continuous path including in-air movements (pen lifts)
  ax_traj.plot(
      df["x"],
      df["y"],
      color="lightgray",
      linestyle=":",
      linewidth=1.2,
      label="In-air Trajectory",
      zorder=1,
  )

  # Filter on-surface points (touching == True)
  on_surface = df[df["touching"]]

  # Scale point sizes dynamically based on pressure
  min_p, max_p = df["pressure"].min(), df["pressure"].max()
  if max_p > min_p:
    point_sizes = (
        15 + 120 * (on_surface["pressure"] - min_p) / (max_p - min_p)
    )
  else:
    point_sizes = 30

  # Scatter plot colored by time progression
  scatter = ax_traj.scatter(
      on_surface["x"],
      on_surface["y"],
      c=on_surface["time"],
      s=point_sizes,
      cmap="viridis",
      alpha=0.85,
      edgecolors="none",
      label="Pen-down (Size = Pressure)",
      zorder=2,
  )

  cbar = fig.colorbar(scatter, ax=ax_traj, orientation="horizontal", pad=0.08)
  cbar.set_label("Time Progression (s)")

  ax_traj.set_title("Handwriting Trajectory & Temporal Sequence", fontsize=12)
  ax_traj.set_xlabel("X Coordinate")
  ax_traj.set_ylabel("Y Coordinate")
  ax_traj.invert_yaxis()  # Invert to match screen coordinate origin (top-left)
  ax_traj.grid(True, linestyle="--", alpha=0.5)
  ax_traj.legend(loc="upper right")

  # --- Panel 2: Pressure Profile over Time ---
  ax_press = fig.add_subplot(gs[0, 1])
  ax_press.plot(
      df["time"],
      df["pressure"],
      color="#1f77b4",
      linewidth=1.5,
      label="Pressure",
  )
  ax_press.fill_between(
      df["time"],
      0,
      df["pressure"],
      where=df["touching"],
      color="#1f77b4",
      alpha=0.25,
      label="Pen Touching Surface",
  )
  ax_press.set_title("Pen Pressure & Contact vs. Time", fontsize=12)
  ax_press.set_ylabel("Pressure")
  ax_press.grid(True, linestyle="--", alpha=0.5)
  ax_press.legend(loc="upper right")

  # --- Panel 3: Kinematic Speed over Time ---
  ax_speed = fig.add_subplot(gs[1, 1], sharex=ax_press)
  ax_speed.plot(
      df["time"],
      df["speed"],
      color="#ff7f0e",
      linewidth=1.2,
      label="Instantaneous Speed",
  )
  ax_speed.set_title("Writing Speed vs. Time", fontsize=12)
  ax_speed.set_xlabel("Time (s)")
  ax_speed.set_ylabel("Speed (units/s)")
  ax_speed.grid(True, linestyle="--", alpha=0.5)
  ax_speed.legend(loc="upper right")

  plt.tight_layout()
  plt.show()


if __name__ == "__main__":
  main()