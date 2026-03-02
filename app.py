import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="UN Country Explorer", layout="wide")

st.title("UN Country Map")
st.caption("Select a country to highlight it on the world map.")

# Use Plotly's built-in 2007 gapminder slice as a stable world country index.
world = px.data.gapminder().query("year == 2007")[["country", "iso_alpha"]].copy()
world = world.rename(columns={"iso_alpha": "iso3"})
world = world.sort_values("country").reset_index(drop=True)

countries = world["country"].tolist()

selected_country = st.selectbox(
    "Country",
    options=countries,
    index=countries.index("Denmark") if "Denmark" in countries else 0,
)

selected_iso3 = world.loc[world["country"] == selected_country, "iso3"].iloc[0]

map_df = world.copy()
map_df["selected"] = (map_df["iso3"] == selected_iso3).astype(int)
map_df["status"] = map_df["selected"].map({0: "Other countries", 1: "Selected country"})

fig = px.choropleth(
    map_df,
    locations="iso3",
    color="status",
    hover_name="country",
    color_discrete_map={
        "Other countries": "#D9D9D9",
        "Selected country": "#D62828",
    },
    projection="natural earth",
)

fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    legend_title_text="",
)

st.plotly_chart(fig, use_container_width=True)
