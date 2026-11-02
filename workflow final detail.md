# COMP693 Multisensor Forest Remote-Sensing Workflow

## 1. Overview

This document summarises the final processing and analysis workflow used in the COMP693 project **Integrating Hyperspectral Imaging and Multi-Scale LiDAR for Forest Structure Analysis** at Brandenburg Coppice, Lincoln University, New Zealand.

The project integrated five principal remote-sensing datasets:

- **2023 airborne LiDAR** — publicly available historical structural reference;
- **2026 DJI Zenmuse L2 UAV LiDAR** — contemporary upper-canopy structure;
- **2026 Livox Mid-70 terrestrial/mobile LiDAR** — lower and intermediate vegetation structure;
- **2026 FigSpec FS60-C hyperspectral imagery** — spectral vegetation condition;
- **2026 DJI Zenmuse H30T thermal imagery** — canopy temperature.

The overall workflow was:

```text
Raw / source data
        ↓
Sensor-specific preprocessing
        ↓
Spatial and vertical alignment
        ↓
0.5 m spatial harmonisation
        ↓
Canopy masking
        ↓
LiDAR structural analyses
        ↓
Hyperspectral and thermal integration
        ↓
2023–2026 canopy-change analysis
        ↓
Validation, quality control, and final outputs
```

The final analyses were performed mainly in **ArcGIS Pro**, **CloudCompare**, **DJI Terra**, **ENVI**, and **Python**.

---

## 2. Study Area and Common Spatial Framework

All final spatial products were restricted to a common study-area boundary covering Brandenburg Coppice.

The common spatial framework used for final raster analyses was:

- Coordinate system: **NZGD 2000 / New Zealand Transverse Mercator 2000 (EPSG:2193)**
- Final raster cell size: **0.5 m**
- Common processing extent: `Study_Area_Final`
- Common alignment / snapping reference: the final DJI L2 CHM
- Contemporary canopy mask: **DJI L2 CHM > 2 m**

The purpose of harmonisation was to ensure that raster cells represented the same ground locations before cross-sensor comparison.

---

## 3. LiDAR Processing

### 3.1 2023 Airborne LiDAR

The 2023 airborne LiDAR dataset was used as the historical structural reference.

The source point cloud was in absolute elevation and therefore could not be treated directly as vegetation height.

In ArcGIS Pro:

1. Ground-classified points were used to generate a DTM.
2. Surface / upper returns were used to generate a DSM.
3. Both rasters were generated at 0.5 m resolution.
4. Canopy height was calculated as:

```text
CHM = DSM - DTM
```

The final cleaned product was:

```text
Airborne_CHM_05m_Final_Clean
```

This dataset was used for cross-platform comparison, historical canopy extent, and the 2023–2026 canopy-change analysis.

---

### 3.2 DJI Zenmuse L2 UAV LiDAR

The DJI Zenmuse L2 point cloud was processed using DJI Terra and subsequently aligned with the project spatial reference.

A consistent vertical offset of approximately **16.03 m** was identified relative to the airborne reference at stable bare-ground locations.

A constant vertical translation was therefore applied:

```text
Z_corrected = Z_L2 - 16.03 m
```

This correction was treated as an **empirical co-registration adjustment**, not as a formally verified vertical-datum transformation.

After alignment:

1. Ground points were used to create a 0.5 m DTM.
2. Surface points were used to create a 0.5 m DSM.
3. The canopy-height model was calculated as:

```text
L2 CHM = L2 DSM - L2 DTM
```

The final product used in most analyses was:

```text
L2_CHM_05m_Final
```

For contemporary multisensor analyses, the canopy mask was defined as:

```text
L2_CHM_05m_Final > 2 m
```

producing:

```text
CanopyMask_2026_GT2m
```

---

### 3.3 Livox Mid-70 Terrestrial / Mobile LiDAR

The terrestrial point cloud was collected using a Livox Mid-70-based mobile scanning workflow and processed using FAST-LIO.

The original Livox point cloud contained absolute elevation values, so point-level ground normalisation was required before vegetation-height analysis.

#### 3.3.1 Livox DTM

A Livox-specific DTM was generated in ArcGIS Pro from the Livox ground-classified points.

Key settings:

- Tool: `LAS Dataset To Raster`
- Value field: `ELEVATION`
- Interpolation: `BINNING / AVERAGE`
- Void fill: `LINEAR`
- Output type: `FLOAT`
- Cell size: **0.25 m**

The resulting DTM was:

```text
Livox_Expanded_DTM_025m.tif
```

#### 3.3.2 Point-Level AGL Normalisation

The script:

```text
scripts/lidar/01_normalize_livox_height.py
```

was retained as part of the final workflow.

For each Livox point, the script sampled the local DTM elevation using the point X/Y coordinate and calculated:

```text
AGL = Z_original - Z_DTM
```

The output LAS Z coordinate therefore represented **height above ground (AGL)** rather than absolute elevation.

The original elevation was preserved in an extra LAS field named:

```text
original_z
```

This normalisation was required before vertical-strata analysis, height-based filtering, and Equation 8 vegetation-cover analysis.

---

## 4. LiDAR Structural Analyses

### 4.1 Cross-Platform Canopy-Height Comparison

The three LiDAR-derived CHMs were harmonised to:

- 0.5 m cell size;
- the same spatial extent;
- the same coordinate system;
- the same raster alignment.

For canopy-only comparison, a common canopy mask was applied to avoid large areas of zero-height ground artificially increasing correlation.

The following statistics were calculated:

- Bias
- Mean Absolute Error (MAE)
- Root Mean Square Error (RMSE)
- Pearson correlation coefficient (r)
- R²

Final comparison results included:

| Comparison | Bias (m) | MAE (m) | RMSE (m) | Pearson r | R² |
|---|---:|---:|---:|---:|---:|
| L2 vs Airborne | +0.449 | 2.142 | 3.192 | 0.867 | 0.751 |
| Livox vs Airborne | -1.514 | 2.903 | 4.019 | 0.788 | 0.620 |

These comparisons were interpreted cautiously because the airborne dataset was acquired in 2023, while the L2 and Livox datasets were acquired in 2026.

---

### 4.2 Contemporary L2–Livox Agreement

For the 2026 datasets, L2 and Livox CHMs were compared within the contemporary canopy mask.

```text
r = 0.815
R² ≈ 0.664
```

This showed strong spatial agreement in contemporary canopy structure while recognising that UAV and terrestrial LiDAR represent different parts of the forest.

---

### 4.3 Vertical-Strata Analysis

The vertical-strata analysis was separate from Equation 8.

#### DJI L2 canopy classes

```text
Low / Open: < 5 m
Medium:     5–15 m
Tall:       > 15 m
```

#### Livox AGL strata

```text
Low vegetation:     0–2 m
Medium vegetation:  2–5 m
High vegetation:    >5 m
```

The Livox AGL point cloud was split into these strata in CloudCompare.

The purpose of the analysis was to compare the proportion of Livox returns from different vegetation layers within each L2 canopy-height class.

---

## 5. Equation 8: Terrestrial Vegetation Cover

The final Equation 8 workflow used **ArcGIS Pro**, not the exploratory Python cell-generation scripts.

### 5.1 Spatial Units

Fixed subplots:

```text
10 m × 10 m = 100 m²
```

Livox horizontal occupancy cells:

```text
0.25 m × 0.25 m
```

A complete 10 × 10 m subplot therefore contained:

```text
40 × 40 = 1600 possible horizontal cells
```

Only fishnet polygons completely within `Study_Area_Final` were retained.

### 5.2 N_all: All Sampled Horizontal Cells

All AGL-normalised Livox points were used.

In ArcGIS Pro:

1. `LAS Point Statistics As Raster`
2. Method: `Point Count`
3. Cell size: `0.25 m`

Output:

```text
Livox_All_Count_025m
```

A binary occupancy raster was created:

```text
Con("Livox_All_Count_025m" > 0, 1)
```

Output:

```text
Livox_All_Presence_025m
```

For each 10 × 10 m subplot, `Zonal Statistics as Table` with `SUM` was used.

```text
N_all = number of unique 0.25 m cells sampled by Livox
```

### 5.3 N_0.5: Vegetated Horizontal Cells

The AGL-normalised Livox point cloud was filtered to retain:

```text
AGL > 0.5 m
```

The filtered point cloud was converted to a 0.25 m point-count raster and then to a binary presence raster:

```text
Livox_GT05_Presence_025m
```

`Zonal Statistics as Table` with `SUM` provided:

```text
N_0.5 = number of unique 0.25 m cells containing at least one point > 0.5 m AGL
```

Multiple points within the same horizontal cell were counted only once.

### 5.4 Completeness and Cover

For each subplot:

```text
Completeness = N_all / 1600
Cover = N_0.5 / 1600
```

Only subplots satisfying:

```text
Completeness >= 0.90
```

were retained.

This produced **72 valid subplots**.

Final vegetation-cover results included:

- Mean cover: **78.92%**
- Median cover: **85.44%**
- Range: **17.56–100%**
- L2 mean canopy height vs Livox cover: **r ≈ 0.515, R² ≈ 0.265**

### Important implementation note

The scripts:

```text
02_equation8_all_sampled_cells.py
03_equation8_vegetated_cells.py
```

were **exploratory / alternative implementations developed during method testing**.

They were **not used for the final Equation 8 results**.

The final `N_all` and `N_0.5` values were calculated in ArcGIS Pro using:

```text
0.25 m occupancy rasters
→ Zonal Statistics
→ 10 × 10 m subplots
```

The script `01_normalize_livox_height.py`, however, remained part of the final workflow.

---

## 6. Hyperspectral Processing

The FS60-C hyperspectral workflow required substantial testing because the manufacturer-provided documentation did not fully match the camera configuration used during this project.

A separate guide was produced:

```text
FS60-C Hyperspectral Camera Practical Workflow and Troubleshooting Guide.pdf
```

This document contains the detailed acquisition, registration, processing, and troubleshooting workflow developed during repeated field experiments.

The present workflow file records only the final analysis path.

### 6.1 Selected Wavelengths

| Extracted band | Wavelength |
|---|---:|
| B1 | 480 nm |
| B2 | 500 nm |
| B3 | 560 nm |
| B4 | 670 nm |
| B5 | 680 nm |
| B6 | 705 nm |
| B7 | 740 nm |
| B8 | 750 nm |
| B9 | 800 nm |
| B10 | 900 nm |
| B11 | 970 nm |

### 6.2 Vegetation Indices

```text
NDVI  = (B9 - B4) / (B9 + B4)
GNDVI = (B9 - B3) / (B9 + B3)
NDRE  = (B9 - B6) / (B9 + B6)
PSRI  = (B5 - B2) / B8
WBI   = B10 / B11
```

For WBI, division-by-zero values were excluded using `SetNull`.

### 6.3 Spatial Harmonisation

The native hyperspectral products were first aggregated using:

```text
Cell factor = 14
Technique   = MEAN
```

The aggregated rasters were then resampled to exactly:

```text
0.5 m
```

using bilinear resampling with:

- Snap raster: final L2 CHM
- Output CRS: EPSG:2193
- Processing extent: `Study_Area_Final`

The contemporary canopy mask was then applied.

Final products included:

```text
NDVI_2026_Canopy_GT2m
GNDVI_2026_Canopy_GT2m
NDRE_2026_Canopy_GT2m
PSRI_2026_Canopy_GT2m
WBI_2026_Canopy_GT2m
```

---

## 7. Structure–Spectral Integration

The final 2026 structural and spectral products were integrated using the ArcGIS `Sample` tool.

Main variables:

```text
L2_CHM_2026_Canopy_GT2m
Livox_CHM_2026_Canopy_GT2m
NDVI_2026_Canopy_GT2m
GNDVI_2026_Canopy_GT2m
NDRE_2026_Canopy_GT2m
PSRI_2026_Canopy_GT2m
WBI_2026_Canopy_GT2m
```

A Pearson correlation matrix was generated using Python / pandas.

Key results:

```text
L2 vs WBI      r = 0.304
L2 vs NDRE     r = 0.292
Livox vs NDRE  r = 0.282
Livox vs WBI   r = 0.253
```

The spectral indices themselves showed much stronger intercorrelation, so they were not interpreted as independent predictors.

---

## 8. Thermal Analysis

The H30T thermal raster was aligned to the same 0.5 m grid and restricted to the contemporary canopy mask.

Final product:

```text
Thermal_2026_Canopy_GT2m
```

The thermal raster was sampled together with L2 CHM, Livox CHM, NDRE, and WBI.

The strongest thermal relationship was with NDRE:

```text
Thermal = 7.437 - 6.447 × NDRE
R² ≈ 0.234
r ≈ -0.484
```

L2 and Livox canopy height showed weaker relationships with temperature.

### 8.1 Spatial Residual Analysis

A feature-class version of the thermal sample dataset was generated so that regression residuals retained X/Y locations.

Global Moran's I was applied to the NDRE-only model residuals.

Result:

```text
Moran's I ≈ 0.811
p < 0.001
```

This indicated strong positive spatial autocorrelation in the unexplained thermal variation.

### 8.2 Sunlit and Shaded Canopy Check

Sunlit and shaded canopy polygons were delineated using contemporary imagery.

Regression residuals were summarised within these polygons.

```text
Mean sunlit residual ≈ +0.608 °C
Mean shaded residual ≈ -1.775 °C
Difference ≈ 2.38 °C
```

This supported the interpretation that illumination / shading remained an important spatial influence after NDRE had already explained part of the thermal variation.

---

## 9. 2023–2026 Canopy-Change Analysis

Canopy change was calculated as:

```text
CHM_Change_2023_2026 =
L2_CHM_2026 - Airborne_CHM_2023
```

### 9.1 High-Confidence Canopy Loss

High-confidence loss required all of the following:

```text
Airborne 2023 CHM > 2 m
L2 2026 CHM <= 2 m
CHM change <= -5 m
```

The intersection defined:

```text
Harvested_HighConfidence_2023_2026
```

A more severe loss layer used:

```text
CHM change <= -10 m
```

Final results included:

- High-confidence loss: **830.25 m² / 0.0830 ha**
- Loss as a proportion of 2023 canopy: **7.26%**
- Severe loss >10 m: **74 m²**
- 2023 mean height in high-confidence area: **6.70 m**
- 2026 mean height in the same area: **0.115 m**
- Mean reduction: approximately **6.59 m**

### 9.2 Stable-Canopy Reference QC

Four independently selected stable-canopy patches were used to characterise normal inter-survey CHM variability.

Stable areas were selected using independent image evidence rather than the change raster itself.

The lowest 5th percentile among the stable patches was approximately:

```text
-0.97 m
```

while the substantial-loss threshold was:

```text
-5 m
```

This supported the use of -5 m as a conservative loss threshold.

---

## 10. Validation

Detected canopy-loss areas were checked using:

- 2023 historical remote-sensing observations;
- 2026 UAV imagery / orthomosaic;
- field inspection;
- observed cleared areas and remaining tree stumps.

These independent observations were used to support interpretation of the high-confidence canopy-loss layer.

---

## 11. Final Reproducibility Resources

Recommended repository structure:

```text
COMP693-Multisensor-Forest-Remote-Sensing/
│
├── README.md
├── requirements.txt
│
├── docs/
│   ├── workflow.md
│   ├── data_availability.md
│   ├── software_versions.md
│   ├── variable_dictionary.md
│   └── references.md
│
├── scripts/
│   ├── lidar/
│   │   └── 01_normalize_livox_height.py
│   │
│   ├── exploratory/
│   │   ├── 02_equation8_all_sampled_cells.py
│   │   └── 03_equation8_vegetated_cells.py
│   │
│   └── figures/
│       ├── figure_4_2_vertical_structure.py
│       └── figure_4_4_correlation_heatmap.py
│
└── guides/
    └── FS60-C_Hyperspectral_Camera_Practical_Workflow_and_Troubleshooting_Guide.pdf
```

The `02` and `03` scripts should not be described as part of the final Equation 8 implementation. If retained, they should be clearly labelled as exploratory or alternative implementations.

---

## 12. Software

Main software used:

- ArcGIS Pro
- CloudCompare
- DJI Terra
- ENVI
- FigSpec / CHNSpec processing software
- Python
- laspy
- rasterio
- NumPy
- pandas
- matplotlib

Exact versions are documented separately in:

```text
docs/software_versions.md
```

---

## 13. Interpretation Notes

1. The 2023 airborne LiDAR and 2026 datasets were acquired at different times and from different viewing geometries.
2. The 16.03 m L2 correction was an empirical co-registration adjustment and should not be presented as a formally established vertical-datum transformation.
3. Terrestrial and UAV LiDAR are complementary rather than interchangeable because they sample different forest layers.
4. Spectral indices and canopy height represent different dimensions of vegetation condition and structure.
5. Thermal relationships were affected by illumination and spatial context.
6. The canopy-change analysis used conservative criteria and independent validation to reduce false interpretation of cross-sensor differences as real vegetation loss.
7. Equation 8 was ultimately implemented using ArcGIS Pro occupancy rasters and zonal statistics, not the exploratory Python cell-generation scripts.
