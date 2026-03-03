from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="Happiness Dashboard", layout="wide")

DATASET_PATH = Path("data/dashboard_dataset.csv")
DESCRIPTION_PATH = Path("description.md")

METRICS = {
    "Happiness rank": {
        "column": "happiness_rank",
        "label": "Happiness rank",
        "ascending_good": True,
        "color_scale": "RdYlGn_r",
    },
    "Life evaluation (3-year average)": {
        "column": "life_evaluation_3yr_avg",
        "label": "Life evaluation (3-year average)",
        "ascending_good": False,
        "color_scale": "YlGnBu",
    },
    "Tax revenue (excluding social contributions)": {
        "column": "tax_revenue_excl_sc",
        "label": "Tax revenue (excluding social contributions)",
        "ascending_good": False,
        "color_scale": "Viridis",
    },
}


@st.cache_data
def load_dataset(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    expected = {
        "iso3",
        "country",
        "year",
        "happiness_rank",
        "life_evaluation_3yr_avg",
        "tax_revenue_excl_sc",
    }
    missing = expected.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in dataset: {sorted(missing)}")

    df["iso3"] = df["iso3"].astype("string").str.strip().str.upper()
    df.loc[df["iso3"].isin(["", "NAN", "NONE", "<NA>"]), "iso3"] = pd.NA
    df["country"] = df["country"].astype(str).str.strip()
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["happiness_rank"] = pd.to_numeric(df["happiness_rank"], errors="coerce")
    df["life_evaluation_3yr_avg"] = pd.to_numeric(df["life_evaluation_3yr_avg"], errors="coerce")
    df["tax_revenue_excl_sc"] = pd.to_numeric(df["tax_revenue_excl_sc"], errors="coerce")
    return df.dropna(subset=["country", "year"]).copy()


st.title("World Happiness Map")

if not DATASET_PATH.exists():
    st.error(f"Dataset not found: {DATASET_PATH}")
    st.info("Run `python scripts/build_dashboard_dataset.py` first.")
    st.stop()

try:
    df = load_dataset(DATASET_PATH)
except ValueError as exc:
    st.error(str(exc))
    st.info("Run `python scripts/build_dashboard_dataset.py` to rebuild the dataset with tax data.")
    st.stop()

countries = ["All countries"] + sorted(df["country"].dropna().unique().tolist())
years = sorted(df["year"].dropna().unique().tolist())
default_year = max(years)
ctrl_col1, ctrl_col2, ctrl_col3 = st.columns(3)
with ctrl_col1:
    selected_country = st.selectbox(
        "Country",
        options=countries,
        index=countries.index("Denmark") if "Denmark" in countries else 0,
    )
with ctrl_col2:
    selected_year = st.selectbox("Year", options=years, index=years.index(default_year))
with ctrl_col3:
    metric_label = st.selectbox("Color by", options=list(METRICS.keys()), index=0)

metric_config = METRICS[metric_label]
metric_col = metric_config["column"]

year_df = df[df["year"] == selected_year].copy()
plot_df = year_df.dropna(subset=[metric_col, "iso3"]).copy()

main_col, right_col = st.columns([3, 1], gap="large")

with right_col:
    st.subheader("About")
    if DESCRIPTION_PATH.exists():
        st.markdown(DESCRIPTION_PATH.read_text(encoding="utf-8"))
    else:
        st.info(f"Description file not found: {DESCRIPTION_PATH}")

with main_col:
    if plot_df.empty:
        st.warning("No plottable map data for the selected year and metric.")
    else:
        hover_data = {
            "country": True,
            "year": True,
            "happiness_rank": ":.0f",
            "life_evaluation_3yr_avg": ":.3f",
            "tax_revenue_excl_sc": ":.2%",
            "iso3": False,
        }

        map_fig = px.choropleth(
            plot_df,
            locations="iso3",
            color=metric_col,
            hover_name="country",
            hover_data=hover_data,
            color_continuous_scale=metric_config["color_scale"],
            projection="natural earth",
        )

        selected_row = plot_df[plot_df["country"] == selected_country]
        if selected_country != "All countries" and not selected_row.empty:
            map_fig.add_trace(
                go.Choropleth(
                    locations=selected_row["iso3"],
                    z=[1] * len(selected_row),
                    locationmode="ISO-3",
                    colorscale=[[0, "#111111"], [1, "#111111"]],
                    showscale=False,
                    marker_line_color="#111111",
                    marker_line_width=3,
                    hoverinfo="skip",
                )
            )

        map_fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            coloraxis_colorbar_title=metric_config["label"],
        )
        st.plotly_chart(map_fig, width="stretch")

if selected_country == "All countries":
    country_series = (
        df.dropna(subset=[metric_col, "year"])
        .groupby("year", as_index=False)[metric_col]
        .mean()
        .sort_values("year")
    )
    series_title = f"All countries average: {metric_config['label']} Over Time"
else:
    country_series = df[df["country"] == selected_country].sort_values("year")
    country_series = country_series.dropna(subset=[metric_col, "year"])
    series_title = f"{selected_country}: {metric_config['label']} Over Time"

with main_col:
    st.subheader(series_title)

    if country_series.empty:
        st.warning("No time-series data available for the selected country and metric.")
    else:
        line_fig = px.line(
            country_series,
            x="year",
            y=metric_col,
            markers=True,
            labels={"year": "Year", metric_col: metric_config["label"]},
        )
        line_fig.update_traces(line=dict(width=3, color="#D62828"), marker=dict(size=8))
        line_fig.update_layout(margin=dict(l=0, r=0, t=20, b=0))

        if metric_config["ascending_good"]:
            line_fig.update_yaxes(autorange="reversed")

        st.plotly_chart(line_fig, width="stretch")

    st.subheader("Happiness Rank vs Tax Revenue (Excluding Social Contributions)")

    scatter_df = year_df.dropna(subset=["happiness_rank", "tax_revenue_excl_sc"]).copy()
    if scatter_df.empty:
        st.warning("No scatterplot data for the selected year.")
    else:
        scatter_fig = px.scatter(
            scatter_df,
            x="tax_revenue_excl_sc",
            y="happiness_rank",
            hover_name="country",
            labels={
                "tax_revenue_excl_sc": "Tax revenue (excluding social contributions)",
                "happiness_rank": "Happiness rank",
            },
            opacity=0.8,
        )
        scatter_fig.update_traces(marker=dict(size=9, color="#4E79A7"))

        if selected_country != "All countries":
            selected_scatter = scatter_df[scatter_df["country"] == selected_country]
            if not selected_scatter.empty:
                scatter_fig.add_trace(
                    go.Scatter(
                        x=selected_scatter["tax_revenue_excl_sc"],
                        y=selected_scatter["happiness_rank"],
                        mode="markers",
                        marker=dict(size=14, color="#D62828", line=dict(color="black", width=1)),
                        name=selected_country,
                        hovertemplate=(
                            "<b>%{text}</b><br>Tax revenue (excluding SC): %{x:.2%}<br>"
                            "Happiness rank: %{y:.0f}<extra></extra>"
                        ),
                        text=selected_scatter["country"],
                    )
                )

        scatter_fig.update_layout(margin=dict(l=0, r=0, t=20, b=0))
        scatter_fig.update_yaxes(autorange="reversed")
        st.plotly_chart(scatter_fig, width="stretch")

st.markdown("---")
st.caption(
    "Data sources: "
    "[World Happiness Report 2025 data](https://files.worldhappiness.report/WHR25_Data_Figure_2.1v3.xlsx) "
    "(sheet: Data for Figure 2.1) and "
    "[UNU-WIDER GRD 2025 data](https://www.wider.unu.edu/sites/default/files/Data/UNUWIDERGRD_2025.xlsx) "
    "(sheet: General, column: Taxes Excluding SC)."
)
