from __future__ import annotations

from pathlib import Path
import re
import unicodedata

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

WHR_FILE = DATA_DIR / "WHR25_Data_Figure_2.1v3.xlsx"
SDR_FILE = DATA_DIR / "SDR2025-data.xlsx"
OUTPUT_FILE = DATA_DIR / "dashboard_dataset.csv"

SDR_SHEET = "Backdated SDG Index"


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

    sdr = pd.read_excel(
        SDR_FILE,
        sheet_name=SDR_SHEET,
        usecols=["id", "Country", "year", "sdgi_s"],
    ).rename(
        columns={
            "id": "iso3",
            "Country": "country_sdr",
            "year": "year",
            "sdgi_s": "sdg_index_score",
        }
    )
    sdr["year"] = pd.to_numeric(sdr["year"], errors="coerce").astype("Int64")
    sdr["sdg_index_score"] = pd.to_numeric(sdr["sdg_index_score"], errors="coerce")
    sdr["country_key"] = sdr["country_sdr"].map(normalize_country)
    sdr["iso3"] = sdr["iso3"].astype(str).str.strip().str.upper()

    # ISO3 lookup from SDR by country name, then enrich with year-specific merge.
    iso_lookup = (
        sdr.dropna(subset=["iso3", "country_key"])
        .drop_duplicates(subset=["country_key", "iso3"])
        .sort_values("country_key")
        .drop_duplicates(subset=["country_key"], keep="first")
    )[["country_key", "iso3"]]

    merged = whr.merge(
        sdr[["country_key", "year", "sdg_index_score", "iso3"]],
        on=["country_key", "year"],
        how="left",
        suffixes=("", "_sdr"),
    )

    merged = merged.merge(iso_lookup, on="country_key", how="left", suffixes=("", "_lookup"))
    merged["iso3"] = merged["iso3"].fillna(merged["iso3_lookup"])
    merged = merged.drop(columns=["iso3_lookup", "country_key"])

    merged = merged[
        ["iso3", "country", "year", "happiness_rank", "life_evaluation_3yr_avg", "sdg_index_score"]
    ].sort_values(["country", "year"])

    return merged


def main() -> None:
    dataset = build_dataset()
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(OUTPUT_FILE, index=False)
    print(f"Wrote {len(dataset)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
