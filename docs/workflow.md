# Processing workflow

## 1. Data preparation

Five principal datasets were used:
1. 2023 airborne LiDAR
2. 2026 DJI Zenmuse L2 UAV LiDAR
3. Livox terrestrial LiDAR
4. FigSpec FS60-C hyperspectral imagery
5. DJI H30T thermal imagery

## 2. Spatial harmonisation

All spatial datasets were processed in NZGD 2000 / New Zealand Transverse Mercator.

Final raster comparisons used:
- 0.5 m cell size
- common study-area extent
- common snap raster
- canopy mask >2 m where appropriate

## 3. LiDAR analysis

Final CHMs were generated for airborne, L2 and Livox LiDAR.

L2 canopy classes:
- <5 m
- 5–15 m
- >15 m

Livox vegetation strata:
- 0–2 m
- 2–5 m
- >5 m

## 4. Horizontal vegetation occupancy

Livox points were represented using 0.25 m × 0.25 m horizontal cells.

Only 10 m × 10 m subplots with at least 90% sampling completeness were retained.

The vegetation-cover calculation was adapted from Telfer et al. (2026).

## 5. Hyperspectral analysis

Indices:
- NDVI
- GNDVI
- NDRE
- PSRI
- WBI

The final spectral products were aligned to the 0.5 m L2 reference grid.

## 6. Thermal analysis

Thermal imagery was aligned to the common canopy grid.

Analyses included:
- Pearson correlation
- linear regression
- Generalized Linear Regression
- Global Moran's I
- sunlit/shaded residual comparison

## 7. Canopy-change analysis

CHM change was calculated as:

CHM Change = L2 CHM (2026) - Airborne CHM (2023)

High-confidence canopy loss required:
- 2023 canopy >2 m
- 2026 canopy ≤2 m
- CHM change ≤−5 m
