"""Generate Figure 4.4: Pearson correlation heatmap.

The correlation coefficients were calculated from the final analysis outputs
and are supplied directly to this plotting script.
"""

import numpy as np
import matplotlib.pyplot as plt

labels = [
    "L2 CHM",
    "Livox CHM",
    "NDVI",
    "GNDVI",
    "NDRE",
    "PSRI",
    "WBI",
]

corr = np.array([
    [1.000,  0.815,  0.129,  0.147,  0.292, -0.182,  0.304],
    [0.815,  1.000,  0.133,  0.165,  0.282, -0.165,  0.253],
    [0.129,  0.133,  1.000,  0.916,  0.921, -0.864,  0.324],
    [0.147,  0.165,  0.916,  1.000,  0.936, -0.647,  0.269],
    [0.292,  0.282,  0.921,  0.936,  1.000, -0.774,  0.282],
    [-0.182, -0.165, -0.864, -0.647, -0.774,  1.000, -0.312],
    [0.304,  0.253,  0.324,  0.269,  0.282, -0.312,  1.000],
])

fig, ax = plt.subplots(figsize=(9, 7))

im = ax.imshow(corr, vmin=-1, vmax=1, cmap="coolwarm")

ax.set_xticks(np.arange(len(labels)))
ax.set_yticks(np.arange(len(labels)))
ax.set_xticklabels(labels, rotation=45, ha="right")
ax.set_yticklabels(labels)

for i in range(corr.shape[0]):
    for j in range(corr.shape[1]):
        value = corr[i, j]
        text_color = "white" if abs(value) > 0.5 else "black"
        ax.text(
            j,
            i,
            f"{value:.3f}",
            ha="center",
            va="center",
            color=text_color,
            fontsize=10,
        )

cbar = fig.colorbar(im, ax=ax)
cbar.set_label("Pearson correlation coefficient", rotation=90)

ax.set_title("Pearson Correlation Matrix of Structural and Spectral Variables", pad=15)

plt.tight_layout()
plt.savefig("Figure_4_4_correlation_heatmap.png", dpi=300, bbox_inches="tight")
plt.show()

