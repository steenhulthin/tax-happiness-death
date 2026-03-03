from __future__ import annotations

from pathlib import Path
import re
import unicodedata

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

WHR_FILE = DATA_DIR / "WHR25_Data_Figure_2.1v3.xlsx"
TAX_FILE = DATA_DIR / "UNUWIDERGRD_2025.xlsx"
OUTPUT_FILE = DATA_DIR / "dashboard_dataset.csv"

TAX_SHEET = "General"


# Country aliases for common naming mismatches between sources.
COUNTRY_ALIASES: dict[str, str] = {
    "bolivia (plurinational state of)": "bolivia",
    "congo (brazzaville)": "congo",
    "congo (kinshasa)": "democratic republic of the congo",
    "czech republic": "czechia",
    "hong kong s.a.r. of china": "hong kong",
    "iran": "iran, islamic republic of",
    "ivory coast": "cote d'ivoire",
    "kyrgyzstan": "kyrgyz republic",
    "laos": "lao pdr",
    "moldova": "moldova, republic of",
    "north macedonia": "macedonia, the former yugoslav republic of",
    "palestinian territories": "state of palestine",
    "russia": "russian federation",
    "slovakia": "slovak republic",
    "south korea": "korea, republic of",
    "syria": "syrian arab republic",
    "taiwan province of china": "taiwan",
    "tanzania": "tanzania, united republic of",
    "turkey": "turkiye",
    "venezuela": "venezuela, bolivarian republic of",
    "vietnam": "viet nam",
}


def normalize_country(country: str) -> str:
    text = str(country).strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"\s+", " ", text)
    return COUNTRY_ALIASES.get(text, text)


def find_whr_sheet_name() -> str:
    workbook = pd.ExcelFile(WHR_FILE)
    for sheet_name in workbook.sheet_names:
        if "Data for Figure 2.1" in sheet_name:
            return sheet_name
    raise ValueError(
        "Could not find WHR sheet containing 'Data for Figure 2.1' in "
        f"{WHR_FILE.name}. Found: {workbook.sheet_names}"
    )


def build_dataset() -> pd.DataFrame:
    whr_sheet = find_whr_sheet_name()
    whr = pd.read_excel(
        WHR_FILE,
        sheet_name=whr_sheet,
        usecols=["Year", "Rank", "Country name", "Life evaluation (3-year average)"],
    ).rename(
        columns={
            "Year": "year",
            "Rank": "happiness_rank",
            "Country name": "country",
            "Life evaluation (3-year average)": "life_evaluation_3yr_avg",
        }
    )
    whr["year"] = pd.to_numeric(whr["year"], errors="coerce").astype("Int64")
    whr["happiness_rank"] = pd.to_numeric(whr["happiness_rank"], errors="coerce")
    whr["life_evaluation_3yr_avg"] = pd.to_numeric(
        whr["life_evaluation_3yr_avg"], errors="coerce"
    )
    whr["country_key"] = whr["country"].map(normalize_country)

    tax = pd.read_excel(
        TAX_FILE,
        sheet_name=TAX_SHEET,
        skiprows=3,
        usecols=[2, 6, 7, 23],  # C=country, G=iso, H=year, X=Taxes Excluding SC
        names=["country_tax", "iso3", "year", "tax_revenue_excl_sc"],
    )
    tax["year"] = pd.to_numeric(tax["year"], errors="coerce").astype("Int64")
    tax["tax_revenue_excl_sc"] = pd.to_numeric(tax["tax_revenue_excl_sc"], errors="coerce")
    tax["country_key"] = tax["country_tax"].map(normalize_country)
    tax["iso3"] = tax["iso3"].astype(str).str.strip().str.upper()

    tax = tax.dropna(subset=["country_key", "year"]).copy()
    tax = (
        tax.groupby(["country_key", "year"], as_index=False)
        .agg({"tax_revenue_excl_sc": "mean", "iso3": "first"})
        .sort_values(["country_key", "year"])
    )

    # ISO3 lookup from tax data by country name, then enrich with year-specific merge.
    iso_lookup = (
        tax.dropna(subset=["iso3", "country_key"])
        .drop_duplicates(subset=["country_key", "iso3"])
        .sort_values("country_key")
        .drop_duplicates(subset=["country_key"], keep="first")
    )[["country_key", "iso3"]]

    merged = whr.merge(
        tax[["country_key", "year", "tax_revenue_excl_sc", "iso3"]],
        on=["country_key", "year"],
        how="left",
        suffixes=("", "_tax"),
    )

    merged = merged.merge(iso_lookup, on="country_key", how="left", suffixes=("", "_lookup"))
    merged["iso3"] = merged["iso3"].fillna(merged["iso3_lookup"])
    merged = merged.drop(columns=["iso3_lookup", "country_key"])

    merged = merged[
        [
            "iso3",
            "country",
            "year",
            "happiness_rank",
            "life_evaluation_3yr_avg",
            "tax_revenue_excl_sc",
        ]
    ].sort_values(["country", "year"])

    return merged


def main() -> None:
    dataset = build_dataset()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(OUTPUT_FILE, index=False)
    print(f"Wrote {len(dataset)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
