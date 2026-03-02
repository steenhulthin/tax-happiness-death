from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="Happiness Dashboard", layout="wide")

DATASET_PATH = Path("data/dashboard_dataset.csv")

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
        "sdg_index_score",
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
    df["sdg_index_score"] = pd.to_numeric(df["sdg_index_score"], errors="coerce")
    return df.dropna(subset=["country", "year"]).copy()


st.title("World Happiness Map")

if not DATASET_PATH.exists():
    st.error(f"Dataset not found: {DATASET_PATH}")
    st.info("Run `python scripts/build_dashboard_dataset.py` first.")
    st.stop()

df = load_dataset(DATASET_PATH)

countries = sorted(df["country"].dropna().unique().tolist())
selected_country = st.selectbox(
    "Country",
    options=countries,
    index=countries.index("Denmark") if "Denmark" in countries else 0,
)

years = sorted(df["year"].dropna().unique().tolist())
default_year = max(years)
selected_year = st.selectbox("Year", options=years, index=years.index(default_year))

metric_label = st.selectbox("Color by", options=list(METRICS.keys()), index=0)
metric_config = METRICS[metric_label]
metric_col = metric_config["column"]

year_df = df[df["year"] == selected_year].copy()
plot_df = year_df.dropna(subset=[metric_col, "iso3"]).copy()

if plot_df.empty:
    st.warning("No plottable map data for the selected year and metric.")
else:
    hover_data = {
        "country": True,
        "year": True,
        "happiness_rank": ":.0f",
        "life_evaluation_3yr_avg": ":.3f",
        "sdg_index_score": ":.2f",
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
    if not selected_row.empty:
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
    st.plotly_chart(map_fig, use_container_width=True)

country_series = df[df["country"] == selected_country].sort_values("year")
country_series = country_series.dropna(subset=[metric_col, "year"])

st.subheader(f"{selected_country}: {metric_config['label']} Over Time")

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

    st.plotly_chart(line_fig, use_container_width=True)
