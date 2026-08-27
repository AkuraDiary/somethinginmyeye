import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def main():
    # 1. Read the CSV file
    file_path = "../sample/sample_normal.csv"
    
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"⚠️ Error: Could not find {file_path}. Please update the file_path in the script.")
        return

    if "touching" in df.columns:
        df["touching"] = df["touching"].astype(bool)
    else:
        df["touching"] = True

    if "tiltX" not in df.columns: df["tiltX"] = 0
    if "tiltY" not in df.columns: df["tiltY"] = 0
    if "latency" not in df.columns: df["latency"] = 0

    initial_latency = df["latency"].iloc[0]
    latency_timestamp = df["time"].iloc[0]

    df["dt"] = df["time"].diff().fillna(1)
    df.loc[df["dt"] == 0, "dt"] = 1
    
    df["delta_x"] = df["x"].diff().fillna(0)
    df["delta_y"] = df["y"].diff().fillna(0)
    df["distance"] = np.sqrt(df["delta_x"] ** 2 + df["delta_y"] ** 2)
    
    df["velocity"] = df["distance"] / df["dt"]
    df["acceleration"] = df["velocity"].diff().fillna(0) / df["dt"]
    df["jerk"] = df["acceleration"].diff().fillna(0) / df["dt"]

    # 4. Set up the Dashboard Layout
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(4, 2, width_ratios=[1.2, 1])

    on_surface = df[df["touching"]]
    min_p, max_p = df["pressure"].min(), df["pressure"].max()
    point_sizes = 15 + 120 * (on_surface["pressure"] - min_p) / (max_p - min_p + 0.001)

    # --- Panel 1A: Trajectory by TIME (Top Left) ---
    ax_time = fig.add_subplot(gs[0:2, 0])
    ax_time.plot(df["x"], df["y"], color="lightgray", linestyle=":", linewidth=1.2, zorder=1)
    sc_time = ax_time.scatter(
        on_surface["x"], on_surface["y"],
        c=on_surface["time"], s=point_sizes, cmap="viridis",
        alpha=0.85, edgecolors="none", zorder=2
    )
    cbar_time = fig.colorbar(sc_time, ax=ax_time, orientation="horizontal", pad=0.02)
    cbar_time.set_label("Time Progression (ms)")
    ax_time.set_title("Trajectory (Color = Time progression)", fontsize=12, fontweight='bold')
    ax_time.invert_yaxis()
    ax_time.grid(True, linestyle="--", alpha=0.5)

    # --- Panel 1B: Trajectory by VELOCITY (Bottom Left) ---
    # ax_vel_map = fig.add_subplot(gs[2:4, 0], sharex=ax_time, sharey=ax_time)
    # ax_vel_map.plot(df["x"], df["y"], color="lightgray", linestyle=":", linewidth=1.2, zorder=1)
    # sc_vel = ax_vel_map.scatter(
    #     on_surface["x"], on_surface["y"],
    #     c=on_surface["velocity"], s=point_sizes, cmap="plasma",
    #     alpha=0.85, edgecolors="none", zorder=2
    # )
    # cbar_vel = fig.colorbar(sc_vel, ax=ax_vel_map, orientation="horizontal", pad=0.02)
    # cbar_vel.set_label("Velocity (px/ms)")
    # ax_vel_map.set_title("Trajectory (Color = Writing Speed)", fontsize=12, fontweight='bold')
    # # Y-axis already inverted via sharey=ax_time
    # ax_vel_map.grid(True, linestyle="--", alpha=0.5)

    # --- Panel 2: Pressure & Pen Tilt ---
    ax_press = fig.add_subplot(gs[0, 1])
    ax_press.plot(df["time"], df["pressure"], color="#1f77b4", linewidth=1.5, label="Pressure")
    ax_press.plot(df["time"], df["tiltX"]/90, color="purple", linewidth=1.0, alpha=0.5, label="Tilt X (Scaled)")
    ax_press.plot(df["time"], df["tiltY"]/90, color="green", linewidth=1.0, alpha=0.5, label="Tilt Y (Scaled)")
    ax_press.axvline(x=latency_timestamp, color="crimson", linestyle="--", label=f"Latency: {initial_latency:.0f} ms")
    ax_press.set_title("Pen Dynamics (Pressure & Tilt)", fontsize=11, fontweight='bold')
    ax_press.grid(True, linestyle="--", alpha=0.5)
    ax_press.legend(loc="upper right", fontsize=8)

    # --- Panel 3: Velocity ---
    ax_vel = fig.add_subplot(gs[1, 1], sharex=ax_press)
    ax_vel.plot(df["time"], df["velocity"], color="#ff7f0e", linewidth=1.2, label="Velocity")
    ax_vel.set_title("Writing Speed", fontsize=11, fontweight='bold')
    ax_vel.grid(True, linestyle="--", alpha=0.5)

    # --- Panel 4: Acceleration ---
    ax_acc = fig.add_subplot(gs[2, 1], sharex=ax_press)
    ax_acc.plot(df["time"], df["acceleration"], color="#2ca02c", linewidth=1.2, label="Acceleration")
    ax_acc.set_title("Momentum (Acceleration)", fontsize=11, fontweight='bold')
    ax_acc.grid(True, linestyle="--", alpha=0.5)

    # --- Panel 5: Jerk (Smoothness) ---
    ax_jerk = fig.add_subplot(gs[3, 1], sharex=ax_press)
    ax_jerk.plot(df["time"], df["jerk"], color="#d62728", linewidth=1.2, label="Jerk (Micro-stutters)")
    ax_jerk.set_title("Smoothness (Jerk)", fontsize=11, fontweight='bold')
    ax_jerk.set_xlabel("Time (ms)")
    ax_jerk.grid(True, linestyle="--", alpha=0.5)

    plt.suptitle("Dysgraphia Kinematic Analysis Dashboard", fontsize=16, fontweight='bold')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

if __name__ == "__main__":
    main()
