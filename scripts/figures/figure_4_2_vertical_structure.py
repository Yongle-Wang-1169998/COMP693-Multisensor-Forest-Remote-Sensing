"""Generate Figure 4.2: Livox vertical vegetation structure by L2 canopy-height class.

The percentages are the final values reported in the COMP693 final report.
"""

import matplotlib.pyplot as plt
import numpy as np

classes = ["Low/Open (<5 m)", "Medium (5–15 m)", "Tall (>15 m)"]

low = np.array([85.04, 44.50, 32.13])   # Livox 0–2 m
mid = np.array([13.87, 36.34, 29.93])   # Livox 2–5 m
high = np.array([1.09, 19.16, 37.94])   # Livox >5 m

x = np.arange(len(classes))
width = 0.7

fig, ax = plt.subplots(figsize=(10, 6))

b1 = ax.bar(x, low, width, label="Low vegetation (0–2 m)")
b2 = ax.bar(x, mid, width, bottom=low, label="Medium vegetation (2–5 m)")
b3 = ax.bar(x, high, width, bottom=low + mid, label="High vegetation (>5 m)")

for i in range(len(x)):
    ax.text(x[i], low[i] / 2, f"{low[i]:.2f}%", ha="center", va="center", fontsize=10)
    ax.text(x[i], low[i] + mid[i] / 2, f"{mid[i]:.2f}%", ha="center", va="center", fontsize=10)
    ax.text(
        x[i],
        low[i] + mid[i] + high[i] / 2,
        f"{high[i]:.2f}%",
        ha="center",
        va="center",
        fontsize=10,
    )

ax.set_xticks(x)
ax.set_xticklabels(classes, fontsize=11)
ax.set_ylim(0, 100)
ax.set_ylabel("Vegetation proportion (%)", fontsize=12)
ax.set_xlabel("L2 canopy-height class", fontsize=12)
ax.set_title("Livox Vertical Vegetation Structure by L2 Canopy Height Class", fontsize=15)

ax.set_yticks(np.arange(0, 101, 10))
ax.set_yticklabels([f"{i}%" for i in range(0, 101, 10)])
ax.grid(axis="y", linestyle="--", alpha=0.4)
ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False)

ax.text(
    1.02,
    -0.08,
    "Livox: terrestrial LiDAR\nL2: UAV-mounted DJI Zenmuse L2 LiDAR",
    transform=ax.transAxes,
    fontsize=10,
    va="top",
)

plt.tight_layout()
plt.savefig("Figure_4_2_vertical_structure.png", dpi=300, bbox_inches="tight")
plt.show()

