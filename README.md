# Tax, Happiness Dashboard

A Streamlit dashboard for exploring country-level trends in happiness and tax indicators over time.

## Features

- Interactive world map colored by:
  - Happiness rank
  - Life evaluation (3-year average)
  - Tax revenue (excluding social contributions)
- Country selector with `All countries` option
- Year selector
- Time-series chart for selected metric
- Scatterplot of happiness rank vs tax revenue (excluding social contributions)

## Data Sources

- World Happiness Report 2025
  https://files.worldhappiness.report/WHR25_Data_Figure_2.1v3.xlsx
- UNU-WIDER Government Revenue Dataset 2025
  https://www.wider.unu.edu/sites/default/files/Data/UNUWIDERGRD_2025.xlsx

## Project Structure

- `app.py` - Streamlit dashboard app
- `scripts/build_dashboard_dataset.py` - Builds flat dashboard dataset from source Excel files
- `data/` - Source files and generated dataset
  - `WHR25_Data_Figure_2.1v3.xlsx`
  - `UNUWIDERGRD_2025.xlsx`
  - `dashboard_dataset.csv` (generated)

## Setup

1. Create or activate a Python environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Build Dataset

Run:

```bash
python scripts/build_dashboard_dataset.py
```

This generates:

- `data/dashboard_dataset.csv`

## Run Dashboard

```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in your terminal.

## Notes

- Country names are normalized during merge to align records across sources.
- Tax data is read from `UNUWIDERGRD_2025.xlsx` sheet `General`, using column `X` (`Taxes`, `Excluding SC`).
- If the app says dataset is missing or has outdated columns, run the build script first.
