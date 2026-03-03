# About This Dashboard

This dashboard combines two global datasets to let you explore how countries perform over time on:

- **Happiness rank** (lower rank number is better)
- **Life evaluation (3-year average)** from the World Happiness Report
- **Tax revenue (excluding social contributions)** from the UNU-WIDER Government Revenue Dataset

## What the metrics mean

### World Happiness Report metrics

- **Life evaluation (3-year average)** is based on people's answers to the **Cantril Ladder** question (0 to 10), averaged over a three-year period to smooth annual volatility.
- **Happiness rank** orders countries by their average life evaluation for each year.

### Tax metric (UNU-WIDER GRD)

- **Tax revenue (excluding social contributions)** is sourced from the GRD `General` sheet, tax column `Excluding SC`.
- Values are recorded as a share of GDP (ratio). For example, `0.20` is 20% of GDP.
- This is a fiscal structure indicator, not a direct measure of subjective wellbeing.

## How to read the visuals

- **Map**: Shows country-level values for the selected year and selected metric.
- **Time series**: Shows trends over time for one country, or the cross-country average when "All countries" is selected.
- **Scatterplot**: Compares countries on **happiness rank vs tax revenue (excluding social contributions)** for the selected year.

## Interpretation notes

- This dashboard is descriptive. It can reveal patterns, but it does not prove causality.
- Country coverage can differ across years and datasets, so averages and scatter distributions may shift partly because of data availability.
- A country can score strongly on one metric and more weakly on another because these indicators capture different concepts.

## Data sources

- World Happiness Report (2025): https://www.worldhappiness.report/
- WHR data page (Figure 2.1 data): https://www.worldhappiness.report/ed/2025/#appendices-and-data
- UNU-WIDER Government Revenue Dataset: https://www.wider.unu.edu/project/grd-government-revenue-dataset
- GRD data file (2025): https://www.wider.unu.edu/sites/default/files/Data/UNUWIDERGRD_2025.xlsx
