"""Build case study 03 outputs from data/raw/.

Run from the repo root:  uv run python case_studies/03_road_casualties/analysis/build.py
"""

import sys
from pathlib import Path

import pandas as pd
import pandera.pandas as pa

sys.path.insert(0, str(Path(__file__).parent))
from clean import PERIOD_YEARS, add_ratios, load_fire_rescue, load_police, periods  # noqa: E402

from shared.fetch import download  # noqa: E402
from shared.outputs import write_output  # noqa: E402
from shared.provenance import read_meta  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "outputs"
FR_PAGE = "https://www.data.gov.bn/statistics-of-road-traffic-accidents/"
FR_FILES = "https://www.data.gov.bn/wp-content/uploads/2025/12/"

_count = pa.Column(int, pa.Check.ge(0))
ROAD_SCHEMA = pa.DataFrameSchema(
    {
        "year": pa.Column(int, pa.Check.in_range(2000, 2030)),
        "accidents": pa.Column(int, pa.Check.gt(0)),
        "injuries": _count,
        "deaths": _count,
        "injuries_per_100_accidents": pa.Column(float, pa.Check.in_range(0, 100)),
        "deaths_per_1000_accidents": pa.Column(float, pa.Check.in_range(0, 1000)),
    },
    unique=["year"],
)


def fetch():
    police = download(
        source="datagovbn",
        file_url="https://www.data.gov.bn/wp-content/uploads/2025/12/1-Road-Casualities.xlsx",
        title="Road Casualties",
        page_url="https://www.data.gov.bn/road-casualties/",
        edition="2025",
        owner="Royal Brunei Police Force",
        coverage="2009–2017, annual",
        published="2025-12-17",
    )
    fire_rescue = download(
        source="datagovbn",
        file_url=FR_FILES + "STATISTIC-OF-ROAD-TRAFFIC-ACCIDENTS-FROM-2012-TO-2021.xlsx",
        title="Statistics of Road Traffic Accidents",
        page_url=FR_PAGE,
        edition="2025",
        owner="Fire and Rescue Department Brunei Darussalam",
        coverage="2012–2021, annual",
        published="2025-12-09",
    )
    return police, fire_rescue


def prov(path: Path):
    return read_meta(path)[0]


def main():
    police_path, fr_path = fetch()
    roads = add_ratios(load_police(police_path))
    ROAD_SCHEMA.validate(roads)
    first, last = roads.year.min(), roads.year.max()
    write_output(
        roads.round({"injuries_per_100_accidents": 2, "deaths_per_1000_accidents": 2}),
        OUT / "road_casualties.csv",
        prov(police_path),
        notes=(
            f"Accidents, injuries and deaths by year, {first}–{last}, reshaped from one "
            "'Type' column to one column per measure (accidents count events; injuries and "
            "deaths count people). Injuries per 100 accidents and deaths per 1,000 accidents "
            "computed by the author."
        ),
    )

    avg = periods(roads)
    write_output(
        avg.round(2),
        OUT / "road_periods.csv",
        prov(police_path),
        notes=(
            f"Yearly averages over {PERIOD_YEARS}-year periods. Period ratios are total "
            "injuries (or deaths) ÷ total accidents in the period."
        ),
    )

    fr = load_fire_rescue(fr_path)
    check = roads[["year", "injuries", "deaths"]].merge(
        fr, on="year", how="inner", suffixes=("_police", "_fire_rescue")
    )
    check["within_police_total"] = (check.deaths_fire_rescue <= check.deaths_police) & (
        check.injuries_fire_rescue <= check.injuries_police
    )
    if not check.within_police_total.all():
        raise ValueError("Fire and Rescue counts exceed the police totals in some year.")
    write_output(
        check,
        OUT / "road_crosscheck.csv",
        prov(police_path) + prov(fr_path),
        notes=(
            "Police deaths and injuries beside Fire and Rescue's (accidents its crews attended, "
            "both call types summed), for the overlapping years. Fire and Rescue's counts are a "
            "subset, so they must not exceed the police totals."
        ),
    )
    report(roads, avg, check)


def report(roads: pd.DataFrame, avg: pd.DataFrame, check: pd.DataFrame):
    pd.set_option("display.width", 160)
    print("\n== By year")
    print(roads.round(1).to_string(index=False))
    print(f"\n== {PERIOD_YEARS}-year averages")
    print(avg.round(1).to_string(index=False))
    print("\n== Cross-check with Fire and Rescue")
    print(check.to_string(index=False))


if __name__ == "__main__":
    main()
