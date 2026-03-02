# About This Dashboard

This dashboard combines two global datasets to let you explore how countries perform over time on:

- **Happiness rank** (lower rank number is better)
- **Life evaluation (3-year average)** from the World Happiness Report
- **SDG index score** from the Sustainable Development Report

## What the metrics mean

### World Happiness Report metrics

- **Life evaluation (3-year average)** is based on people's answers to the **Cantril Ladder** question (0 to 10), averaged over a three-year period to smooth annual volatility.
- **Happiness rank** orders countries by their average life evaluation for each year.
- The World Happiness Report emphasizes that rankings are based on reported life evaluations, not on a weighted wellbeing index assembled by the report team.

### SDG Index metric

- **SDG index score** is a composite score used in the Sustainable Development Report.
- It is scaled from **0 to 100**, where higher values indicate closer progress toward SDG targets.
- The score is designed as a broad measure of distance to SDG achievement, not a direct measure of subjective wellbeing.

## How to read the visuals

- **Map**: Shows country-level values for the selected year and selected metric.
- **Time series**: Shows trends over time for one country, or the cross-country average when "All countries" is selected.
- **Scatterplot**: Compares countries on **happiness rank vs SDG index score** for the selected year.

## Interpretation notes

- This dashboard is descriptive. It can reveal patterns, but it does not prove causality.
- Country coverage can differ across years and datasets, so averages and scatter distributions may shift partly because of data availability.
- A country can score strongly on one metric and more weakly on another because these indicators capture different concepts.

## Data sources

- World Happiness Report (2025): https://www.worldhappiness.report/
- WHR data page (Figure 2.1 data): https://www.worldhappiness.report/ed/2025/#appendices-and-data
- Sustainable Development Report / SDG Index: https://dashboards.sdgindex.org/
- SDR methodology: https://dashboards.sdgindex.org/chapters/methodology/
