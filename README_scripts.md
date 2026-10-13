# COMP693 GitHub-ready scripts

These files are cleaned versions of the final scripts used to support the COMP693 report.

## LiDAR workflow

1. `01_normalize_livox_height.py`
   - Samples a DTM and converts Livox Z values to height above ground (AGL).
2. `02_equation8_all_sampled_cells.py`
   - Generates unique 0.25 m horizontal cells for all sampled Livox locations (`N_all`).
3. `03_equation8_vegetated_cells.py`
   - Generates unique 0.25 m horizontal cells containing at least one Livox return above 0.5 m (`N_>0.5`).

Subplot aggregation, completeness filtering, joins, and related table calculations were completed in ArcGIS Pro and are documented in the final report.

## Figure scripts

- `figure_4_2_vertical_structure.py`
  - Generates the stacked bar chart of Livox vertical vegetation proportions within L2 canopy-height classes.
- `figure_4_4_correlation_heatmap.py`
  - Generates the 7 × 7 Pearson correlation heatmap from the final correlation coefficients.

## Data paths

The scripts use relative paths such as `data/` and `outputs/`. Raw project datasets are not distributed with the repository.
