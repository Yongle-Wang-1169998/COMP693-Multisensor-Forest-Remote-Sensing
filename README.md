# COMP693 Multi-sensor Forest Remote Sensing

This repository contains processing scripts, workflow documentation, and selected figures developed for the COMP693 Independent Project at Lincoln University.

## Project title

Integrating Hyperspectral Imaging and Multi-Scale LiDAR for Forest Structure Analysis

## Overview

The project integrates:

- 2023 airborne LiDAR
- 2026 DJI Zenmuse L2 UAV LiDAR
- Livox terrestrial LiDAR
- FigSpec FS60-C hyperspectral imagery
- DJI H30T thermal imagery

The workflow includes spatial harmonisation, canopy-height modelling, terrestrial vegetation-structure analysis, hyperspectral vegetation-index generation, thermal modelling, and multi-temporal canopy-change detection.

## Main software

- ArcGIS Pro 3.6.2
- CloudCompare 2.13.2
- DJI Terra 5.3.0
- ENVI 5.6
- FigSpec Studio 2.0
- FigSpec Merge 2.0
- Python

## Repository structure

- `scripts/` – Python scripts used for final analyses
- `figures/` – selected figures used in the final report
- `docs/` – workflow notes and variable definitions
- `config/` – example processing configuration
- `sample_data/` – placeholder information for data structure

## Main analyses

### LiDAR integration
- 0.5 m canopy-height model comparison
- DJI L2 vs Livox structural agreement
- Livox vertical vegetation strata
- 10 m × 10 m subplot horizontal vegetation occupancy

### Hyperspectral analysis
- NDVI
- GNDVI
- NDRE
- PSRI
- WBI
- Structure–spectral correlation analysis

### Thermal analysis
- canopy temperature analysis
- NDRE–thermal regression
- GLR model comparison
- Moran's I residual analysis
- sunlit/shaded residual comparison

### Multi-temporal canopy change
- 2023 airborne LiDAR vs 2026 DJI L2
- high-confidence canopy-loss detection
- stable-canopy validation

## Data availability

Raw LiDAR, hyperspectral, thermal, and orthomosaic datasets are not included in this repository because of file size, licensing, and data-access constraints.

The scripts are therefore provided primarily to document and reproduce the analytical workflow when equivalent source data are available.

## Reproducibility

Software versions, processing parameters, raster resolutions, thresholds, and key analysis settings are documented in the final report and in the `docs/` directory.

## Author

Yongle Wang  
COMP693 Independent Project  
Lincoln University
