"""Generate unique 0.25 m horizontal vegetation cells above 0.5 m.

The script filters AGL-normalized Livox points to heights > 0.5 m and then
counts unique horizontal XY cells. Z is deliberately ignored after filtering:
a 0.25 m × 0.25 m cell contributes once if it contains at least one vegetation
return above 0.5 m.

The output corresponds to N_>0.5 used in the adapted Equation 8 workflow.
"""

import laspy
import numpy as np
from pathlib import Path
import csv

# =========================================================
# SETTINGS
# =========================================================

CELL_SIZE = 0.25           # metres
MIN_HEIGHT = 0.5           # Equation 8 threshold
CHUNK_SIZE = 1_000_000     # read 1 million points at a time


# =========================================================
# INPUT FILES
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "livox_normalized"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "equation8"

las_files = [
    DATA_DIR / "ground_lidar_Normalized_AGL.las",
    DATA_DIR / "south_west_Normalized_AGL.las",
]

output_folder = OUTPUT_DIR
output_folder.mkdir(parents=True, exist_ok=True)


# =========================================================
# FIND COMMON XY ORIGIN
# =========================================================

min_x = np.inf
min_y = np.inf

for las_path in las_files:

    with laspy.open(las_path) as reader:

        min_x = min(
            min_x,
            reader.header.mins[0]
        )

        min_y = min(
            min_y,
            reader.header.mins[1]
        )


# Align origin to 0.25 m grid
origin_x = (
    np.floor(min_x / CELL_SIZE)
    * CELL_SIZE
)

origin_y = (
    np.floor(min_y / CELL_SIZE)
    * CELL_SIZE
)

print("Common horizontal grid origin:")
print(f"X origin = {origin_x:.3f}")
print(f"Y origin = {origin_y:.3f}")


# =========================================================
# PROCESS EACH LAS IN CHUNKS
# =========================================================

chunk_files = []
chunk_number = 0

for las_path in las_files:

    print("\n==========================================")
    print(f"Processing: {las_path.name}")
    print("==========================================")

    with laspy.open(las_path) as reader:

        total_points = reader.header.point_count

        print(
            f"Total points: "
            f"{total_points:,}"
        )

        for points in reader.chunk_iterator(
            CHUNK_SIZE
        ):

            x = np.asarray(points.x)
            y = np.asarray(points.y)
            z = np.asarray(points.z)

            # ---------------------------------------------
            # Keep points above 0.5 m
            # ---------------------------------------------

            valid = (
                np.isfinite(x)
                & np.isfinite(y)
                & np.isfinite(z)
                & (z > MIN_HEIGHT)
            )

            x = x[valid]
            y = y[valid]

            if len(x) == 0:
                continue

            # ---------------------------------------------
            # Convert to horizontal 0.25 m cell indices
            # ---------------------------------------------

            ix = np.floor(
                (x - origin_x)
                / CELL_SIZE
            ).astype(np.int32)

            iy = np.floor(
                (y - origin_y)
                / CELL_SIZE
            ).astype(np.int32)

            horizontal_cells = np.column_stack(
                (ix, iy)
            )

            # ---------------------------------------------
            # Remove duplicates inside this chunk
            #
            # IMPORTANT:
            # We deliberately ignore Z here.
            # If a horizontal 0.25 x 0.25 m cell contains
            # any vegetation return above 0.5 m, it counts
            # once toward horizontal vegetation cover.
            # ---------------------------------------------

            unique_cells = np.unique(
                horizontal_cells,
                axis=0
            )

            # ---------------------------------------------
            # Save temporary chunk
            # ---------------------------------------------

            chunk_path = (
                output_folder
                / (
                    f"eq8_cell_chunk_"
                    f"{chunk_number:04d}.npy"
                )
            )

            np.save(
                chunk_path,
                unique_cells
            )

            chunk_files.append(
                chunk_path
            )

            print(
                f"Chunk {chunk_number:04d}: "
                f"{len(points):,} points -> "
                f"{len(x):,} points >0.5 m -> "
                f"{len(unique_cells):,} "
                f"covered horizontal cells"
            )

            chunk_number += 1


# =========================================================
# MERGE ALL CHUNKS
# =========================================================

print("\n==========================================")
print("Merging horizontal cell chunks...")
print("==========================================")

cell_arrays = []

for chunk_path in chunk_files:

    arr = np.load(chunk_path)

    cell_arrays.append(arr)


all_cells = np.vstack(
    cell_arrays
)

print(
    f"Cell records before final deduplication: "
    f"{len(all_cells):,}"
)


# Remove duplicates across chunks and LAS files
final_cells = np.unique(
    all_cells,
    axis=0
)

print(
    f"Final unique covered horizontal cells: "
    f"{len(final_cells):,}"
)


# =========================================================
# CALCULATE CELL CENTRES
# =========================================================

ix = final_cells[:, 0]
iy = final_cells[:, 1]

centre_x = (
    origin_x
    + (ix + 0.5) * CELL_SIZE
)

centre_y = (
    origin_y
    + (iy + 0.5) * CELL_SIZE
)


# =========================================================
# SAVE CSV
# =========================================================

csv_path = (
    output_folder
    / (
        "Livox_Eq8_CoveredCells_025m_"
        "Above05m_Week10.csv"
    )
)

print("\nWriting CSV...")

with open(
    csv_path,
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "cell_x",
        "cell_y",
        "centre_x",
        "centre_y"
    ])

    for i in range(
        len(final_cells)
    ):

        writer.writerow([
            int(ix[i]),
            int(iy[i]),
            f"{centre_x[i]:.3f}",
            f"{centre_y[i]:.3f}"
        ])


# =========================================================
# SAVE SUMMARY
# =========================================================

summary_path = (
    output_folder
    / "Livox_Equation8_Summary.txt"
)

covered_area = (
    len(final_cells)
    * CELL_SIZE
    * CELL_SIZE
)

with open(
    summary_path,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "Livox Equation 8 horizontal "
        "vegetation cover summary\n"
    )

    f.write(
        "====================================="
        "================\n\n"
    )

    f.write(
        f"Horizontal cell size: "
        f"{CELL_SIZE} m\n"
    )

    f.write(
        f"Minimum vegetation height: "
        f"{MIN_HEIGHT} m\n"
    )

    f.write(
        f"Unique covered horizontal cells "
        f"N0.5: {len(final_cells):,}\n"
    )

    f.write(
        f"Covered horizontal area: "
        f"{covered_area:.3f} m2\n"
    )

    f.write(
        f"Origin X: "
        f"{origin_x:.3f}\n"
    )

    f.write(
        f"Origin Y: "
        f"{origin_y:.3f}\n"
    )


print("\n==========================================")
print("Equation 8 processing complete")
print("==========================================")

print(
    f"N0.5 = "
    f"{len(final_cells):,} "
    f"covered horizontal cells"
)

print(
    f"Covered area = "
    f"{covered_area:,.3f} m2"
)

print("\nCSV saved to:")
print(csv_path)

print("\nSummary saved to:")
print(summary_path)
