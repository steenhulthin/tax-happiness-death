# Tax, Happiness & SDG Dashboard 🌍📊

A Streamlit dashboard for exploring country-level trends in happiness and SDG indicators over time.

## Features ✨

- Interactive world map colored by:
  - Happiness rank
  - Life evaluation (3-year average)
  - SDG index score
- Country selector with `All countries` option
- Year selector
- Time-series chart for selected metric
- Scatterplot of happiness rank vs SDG index score

## Data Sources 🔗

- World Happiness Report 2025  
  https://files.worldhappiness.report/WHR25_Data_Figure_2.1v3.xlsx
- Sustainable Development Report 2025  
  https://dashboards.sdgindex.org/static/downloads/files/SDR2025-data.xlsx

## Project Structure 🗂️

- `app.py` - Streamlit dashboard app
- `scripts/build_dashboard_dataset.py` - Builds flat dashboard dataset from source Excel files
- `data/` - Source files and generated dataset
  - `WHR25_Data_Figure_2.1v3.xlsx`
  - `SDR2025-data.xlsx`
  - `dashboard_dataset.csv` (generated)

## Setup ⚙️

1. Create/activate a Python environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Build Dataset 🧱

Run:

```bash
python scripts/build_dashboard_dataset.py
```

This generates:

- `data/dashboard_dataset.csv`

## Run Dashboard 🚀

```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in your terminal (`http://localhost:2000`).

## Notes 📝

- Country names are normalized during merge to align records across sources.
- If the app says dataset is missing, run the build script first.

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
See the [LICENSE](LICENSE) file for the full license text.

Excel files are not covered by the license. See links to data and terms of use for the data in the .md files with similar name.