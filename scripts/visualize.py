import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm
from matplotlib.collections import LineCollection

def main():
    file_path = "../sample/sample_dyslexia.csv"
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"⚠️ Error: Could not find {file_path}. Please update the file_path in the script.")
        return

    # Ensure backward compatibility
    if "touching" in df.columns:
        df["touching"] = df["touching"].astype(bool)
    else:
        df["touching"] = True

    for col in ["tiltX", "tiltY", "latency"]:
        if col not in df.columns: 
            df[col] = 0

    initial_latency = df["latency"].iloc[0]

    # FIX ISSUE 2: LATENCY RED LINE RESTORED
    # Set time=0 to the exact moment they clicked "Start". 
    # The first physical touch happens at `time = initial_latency`
    prompt_start_time = df["time"].iloc[0] - initial_latency
    df["time"] = df["time"] - prompt_start_time

    # Derive Features
    df["dt"] = df["time"].diff().fillna(1)
    df.loc[df["dt"] == 0, "dt"] = 1
    
    df["delta_x"] = df["x"].diff().fillna(0)
    df["delta_y"] = df["y"].diff().fillna(0)
    df["distance"] = np.sqrt(df["delta_x"] ** 2 + df["delta_y"] ** 2)
    
    df["velocity"] = df["distance"] / df["dt"]
    df["acceleration"] = df["velocity"].diff().fillna(0) / df["dt"]
    df["jerk"] = df["acceleration"].diff().fillna(0) / df["dt"]

    df["vel_norm"] = df["velocity"] / (df["velocity"].abs().max() + 1e-5)
    df["acc_norm"] = df["acceleration"] / (df["acceleration"].abs().max() + 1e-5)
    df["jerk_norm"] = df["jerk"] / (df["jerk"].abs().max() + 1e-5)

    # --- RESTORED 3-PANEL LAYOUT (Un-squished) ---
    fig = plt.figure(figsize=(16, 8))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.2, 1])

    on_surface = df[df["touching"]]
    
    # Pressure size scaling
    min_p, max_p = df["pressure"].min(), df["pressure"].max()
    if max_p - min_p < 1e-5:
        point_sizes = np.full(len(on_surface), 50)
    else:
        point_sizes = 10 + 290 * ((on_surface["pressure"] - min_p) / (max_p - min_p))**2

    # 1. BIG GRAPH: Spatial Map (Merged Time Dots + Accel Line)
    ax_traj = fig.add_subplot(gs[:, 0])
    
    # 1A. Background Dotted line for In-Air hovers
    ax_traj.plot(df["x"], df["y"], color="lightgray", linestyle=":", linewidth=1.5, zorder=1, label="In-Air Path")

    # 1B. The Momentum Line (Colored by Accel/Decel)
    # We only draw the line connecting points that are physically touching the screen
    touching_mask = df["touching"].values
    segments, accel_vals = [], []
    xs, ys, accs = df["x"].values, df["y"].values, df["acceleration"].values
    
    for i in range(len(df) - 1):
        if touching_mask[i] and touching_mask[i+1]:
            segments.append([(xs[i], ys[i]), (xs[i+1], ys[i+1])])
            accel_vals.append(accs[i+1])
            
    if segments:
        accel_max = np.percentile(np.abs(accel_vals), 95) + 1e-5
        norm = TwoSlopeNorm(vmin=-accel_max, vcenter=0, vmax=accel_max)
        lc = LineCollection(segments, cmap='coolwarm', norm=norm, linewidths=3.5, zorder=4)
        lc.set_array(np.array(accel_vals))
        ax_traj.add_collection(lc)
        cbar_line = fig.colorbar(lc, ax=ax_traj, pad=0.02)
        cbar_line.set_label("Line Momentum: Blue (Decel) to Red (Accel)")

    # 1C. The Dots (Colored by Time, Sized by Pressure)
    # Added a white edge to the dots so they don't get lost in the colored line!
    sc1 = ax_traj.scatter(
        on_surface["x"], on_surface["y"],
        c=on_surface["time"], cmap="viridis", s=point_sizes,
        edgecolors="white", linewidths=0.5, zorder=3
    )
    cbar_dots = fig.colorbar(sc1, ax=ax_traj, pad=0.08, orientation="horizontal")
    cbar_dots.set_label("Dot Time: Progression (ms)")
    
    ax_traj.set_title("Merged Spatial Map (Line=Momentum, Dots=Time/Pressure)", fontsize=14, fontweight='bold')
    ax_traj.invert_yaxis()
    ax_traj.grid(True, linestyle="--", alpha=0.5)

    # 2. Pen Dynamics Graph
    ax_dyn = fig.add_subplot(gs[0, 1])
    ax_dyn.plot(df["time"], df["pressure"], color="#1f77b4", linewidth=2, label="Pressure")
    ax_dyn.plot(df["time"], df["tiltX"]/90, color="purple", linewidth=1.5, alpha=0.7, label="Tilt X")
    ax_dyn.plot(df["time"], df["tiltY"]/90, color="green", linewidth=1.5, alpha=0.7, label="Tilt Y")
    ax_dyn.fill_between(
        df["time"], 0, 1, where=df["touching"], 
        color="gray", alpha=0.2, transform=ax_dyn.get_xaxis_transform(), label="Pen Touching"
    )
    # THE RED LATENCY LINE
    ax_dyn.axvline(x=initial_latency, color="crimson", linestyle="--", linewidth=2, label="First Touch")
    
    ax_dyn.set_title("Pen Dynamics & Hardware Sensors", fontsize=12, fontweight='bold')
    ax_dyn.set_ylabel("Normalized Range (0 to 1)")
    ax_dyn.grid(True, linestyle="--", alpha=0.5)
    ax_dyn.legend(loc="upper right", fontsize=9)

    # 3. Kinematics Graph
    ax_kin = fig.add_subplot(gs[1, 1], sharex=ax_dyn)
    ax_kin.plot(df["time"], df["vel_norm"], color="#ff7f0e", linewidth=1.5, label="Velocity (Speed)")
    ax_kin.fill_between(df["time"], 0, df["vel_norm"], color="#ff7f0e", alpha=0.3)
    ax_kin.plot(df["time"], df["acc_norm"], color="#2ca02c", linewidth=1.5, label="Acceleration")
    ax_kin.plot(df["time"], df["jerk_norm"], color="#d62728", linewidth=1.5, alpha=0.8, label="Jerk (Micro-stutters)")
    
    # THE RED LATENCY LINE
    ax_kin.axvline(x=initial_latency, color="crimson", linestyle="--", linewidth=2, label="First Touch")

    ax_kin.set_title("Kinematics (Normalized Smoothness)", fontsize=12, fontweight='bold')
    ax_kin.set_xlabel("Time (ms) from Prompt Start")
    ax_kin.set_ylabel("Relative Intensity (-1 to 1)")
    ax_kin.grid(True, linestyle="--", alpha=0.5)
    ax_kin.legend(loc="upper right", fontsize=9)

    plt.suptitle(
        "Dysgraphia Clinical Dashboard\n"
        f"Subject initiated the first touch {initial_latency:.0f} ms after the given prompt started.", 
        fontsize=16, fontweight='bold'
    )
    plt.tight_layout(rect=[0, 0.03, 1, 0.92]) # slight adjustment for the 2-line title
    plt.show()

if __name__ == "__main__":
    main()
