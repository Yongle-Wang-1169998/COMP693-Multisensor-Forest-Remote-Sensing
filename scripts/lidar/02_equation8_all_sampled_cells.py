"""Generate unique 0.25 m horizontal Livox cells for N_all.

The script maps all valid Livox points to a common XY grid and keeps one record
per sampled horizontal cell. The resulting cell set is used to calculate
sampling completeness within 10 m × 10 m subplots.

Input LAS files are expected to contain AGL-normalized Z values, although Z is
not used in this N_all calculation.
"""

import laspy
import numpy as np
from pathlib import Path
import csv

# =========================================================
# SETTINGS
# =========================================================

CELL_SIZE = 0.25
CHUNK_SIZE = 1_000_000


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
# PROCESS ALL POINTS
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

            valid = (
                np.isfinite(x)
                & np.isfinite(y)
            )

            x = x[valid]
            y = y[valid]

            if len(x) == 0:
                continue

            # ---------------------------------------------
            # Convert to horizontal 0.25 m cells
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
            # Unique sampled cells within chunk
            # ---------------------------------------------

            unique_cells = np.unique(
                horizontal_cells,
                axis=0
            )

            chunk_path = (
                output_folder
                / (
                    f"eq8_allsampled_chunk_"
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
                f"{len(unique_cells):,} "
                f"sampled horizontal cells"
            )

            chunk_number += 1


# =========================================================
# MERGE ALL CHUNKS
# =========================================================

print("\n==========================================")
print("Merging sampled cell chunks...")
print("==========================================")

cell_arrays = []

for chunk_path in chunk_files:

    arr = np.load(
        chunk_path
    )

    cell_arrays.append(
        arr
    )


all_cells = np.vstack(
    cell_arrays
)

print(
    f"Cell records before final deduplication: "
    f"{len(all_cells):,}"
)


final_cells = np.unique(
    all_cells,
    axis=0
)

print(
    f"Final unique sampled horizontal cells: "
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
    / "Livox_Eq8_AllSampledCells_025m.csv"
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

sampled_area = (
    len(final_cells)
    * CELL_SIZE
    * CELL_SIZE
)

summary_path = (
    output_folder
    / "Livox_Equation8_AllSampled_Summary.txt"
)

with open(
    summary_path,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "Livox Equation 8 all sampled cells summary\n"
    )

    f.write(
        "=========================================\n\n"
    )

    f.write(
        f"Horizontal cell size: "
        f"{CELL_SIZE} m\n"
    )

    f.write(
        f"Unique sampled cells: "
        f"{len(final_cells):,}\n"
    )

    f.write(
        f"Sampled horizontal area: "
        f"{sampled_area:.3f} m2\n"
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
print("All sampled cells processing complete")
print("==========================================")

print(
    f"N_all = "
    f"{len(final_cells):,} cells"
)

print(
    f"Sampled area = "
    f"{sampled_area:,.3f} m2"
)

print("\nCSV saved to:")
print(csv_path)

print("\nSummary saved to:")
print(summary_path)
