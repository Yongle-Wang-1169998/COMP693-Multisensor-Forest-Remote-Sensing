"""Normalize Livox point-cloud elevations to height above ground (AGL).

This script samples a DTM at each Livox point location and replaces the LAS Z
coordinate with height above ground while preserving the original elevation in
an extra LAS dimension named ``original_z``.

Edit the relative input filenames below to match your local data layout.
"""

import laspy
import rasterio
import numpy as np
from pathlib import Path

# =========================================================
# 1. INPUT PATHS
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "livox_normalized"

dtm_path = DATA_DIR / "Livox_Expanded_DTM_025m.tif"

las_files = [
    DATA_DIR / "ground_lidar.las",
    DATA_DIR / "south_west.las",
]

output_folder = OUTPUT_DIR
output_folder.mkdir(parents=True, exist_ok=True)


# =========================================================
# 2. FUNCTION
# =========================================================

def normalize_las_height(las_path, dtm_path, output_path):

    print(f"\nProcessing: {las_path.name}")

    # Read LAS
    las = laspy.read(las_path)

    x = np.asarray(las.x)
    y = np.asarray(las.y)
    z_original = np.asarray(las.z)

    print(f"Number of points: {len(x):,}")
    print(
        f"Original Z range: "
        f"{z_original.min():.3f} to {z_original.max():.3f} m"
    )

    # -----------------------------------------------------
    # Read DTM and sample ground elevation at each LAS point
    # -----------------------------------------------------

    with rasterio.open(dtm_path) as src:

        coords = zip(x, y)

        ground_z = np.array(
            [value[0] for value in src.sample(coords)],
            dtype=np.float64
        )

        nodata = src.nodata

    # -----------------------------------------------------
    # Find valid DTM samples
    # -----------------------------------------------------

    valid = np.isfinite(ground_z)

    if nodata is not None:
        valid &= ground_z != nodata

    # Protect against obviously invalid raster values
    valid &= ground_z > -1000
    valid &= ground_z < 10000

    print(f"Points with valid DTM: {valid.sum():,}")
    print(f"Points outside/invalid DTM: {(~valid).sum():,}")

    # -----------------------------------------------------
    # Height above ground
    # -----------------------------------------------------

    height_agl = np.full(len(z_original), np.nan)

    height_agl[valid] = (
        z_original[valid] - ground_z[valid]
    )

    print(
        f"Normalized height range: "
        f"{np.nanmin(height_agl):.3f} to "
        f"{np.nanmax(height_agl):.3f} m"
    )

    print(
        f"Median normalized height: "
        f"{np.nanmedian(height_agl):.3f} m"
    )

    # -----------------------------------------------------
    # Only export points with valid DTM
    # -----------------------------------------------------

    valid_indices = np.where(valid)[0]

    # Create a new output LAS containing only valid points
    out_las = laspy.LasData(las.header)
    out_las.points = las.points[valid_indices].copy()

    # -----------------------------------------------------
    # Preserve original elevation as an extra dimension
    # -----------------------------------------------------

    out_las.add_extra_dim(
        laspy.ExtraBytesParams(
            name="original_z",
            type=np.float64
        )
    )

    out_las.original_z = z_original[valid_indices]

    # -----------------------------------------------------
    # Replace output Z with height above ground
    # -----------------------------------------------------

    normalized_z = height_agl[valid_indices]

    out_las.x = x[valid_indices]
    out_las.y = y[valid_indices]
    out_las.z = normalized_z

    # -----------------------------------------------------
    # Write
    # -----------------------------------------------------

    out_las.write(output_path)

    print(f"Saved: {output_path}")
    print(f"Output points: {len(out_las.points):,}")
    print("Done.")


# =========================================================
# 3. RUN BOTH LAS FILES
# =========================================================

for las_path in las_files:

    output_name = (
        las_path.stem
        + "_Normalized_AGL.las"
    )

    output_path = output_folder / output_name

    normalize_las_height(
        las_path,
        dtm_path,
        output_path
    )

print("\nAll files completed.")
