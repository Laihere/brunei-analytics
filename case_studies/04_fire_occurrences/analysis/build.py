"""Build case study 04 outputs from data/raw/.

Run from the repo root:  uv run python case_studies/04_fire_occurrences/analysis/build.py
"""

import sys
from pathlib import Path

import pandas as pd
import pandera.pandas as pa

sys.path.insert(0, str(Path(__file__).parent))
from clean import DISTRICTS, compare_editions, load_area, load_fires  # noqa: E402

from shared.clean_data import write_clean  # noqa: E402
from shared.fetch import download  # noqa: E402
from shared.outputs import write_output  # noqa: E402
from shared.provenance import read_meta  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "outputs"
FILES = "https://www.data.gov.bn/wp-content/uploads/2025/12/"

DISTRICT_SCHEMA = pa.DataFrameSchema(
    {
        "year": pa.Column(int),
        "district": pa.Column(str, pa.Check.isin(list(DISTRICTS.values()))),
        "fires": pa.Column(int, pa.Check.ge(0)),
        "share_pct": pa.Column(float, pa.Check.in_range(0, 100)),
    },
    unique=["year", "district"],
)
TOTAL_SCHEMA = pa.DataFrameSchema(
    {
        "year": pa.Column(int),
        "fires": pa.Column(int, pa.Check.gt(0)),
        "vs_median": pa.Column(float, pa.Check.gt(0)),
        "forest_ha": pa.Column(float, pa.Check.ge(0), nullable=True),
        "grass_peat_ha": pa.Column(float, pa.Check.ge(0), nullable=True),
        "total_ha": pa.Column(float, pa.Check.ge(0), nullable=True),
    },
    unique=["year"],
)


def fetch():
    main = download(
        source="datagovbn",
        file_url=FILES + "Fire-Occurances-By-Districts.xlsx",
        title="Fire Occurances By Districts",
        page_url="https://www.data.gov.bn/fire-occurances-by-districts/",
        edition="2025",
        owner="Brunei Darussalam Central Bank",
        coverage="2009–2020, annual",
        published="2025-12-03",
    )
    other = download(
        source="datagovbn",
        file_url=FILES + "4-Fire-Occurances-By-Districts.xlsx",
        title="Fire Occurances By Districts",
        page_url="https://www.data.gov.bn/fire-occurances-by-districts-2/",
        edition="2025",
        owner="Brunei Fire and Rescue Department",
        coverage="2009–2013, annual",
        published="2025-12-17",
    )
    area = download(
        source="datagovbn",
        file_url=FILES + "STATISTIC-OF-FOREST-AND-GRASS-FIRE-FROM-2012-TO-2021.xlsx",
        title="Statistic of Forest and Grass/Peat Fire",
        page_url="https://www.data.gov.bn/statistic-of-forest-and-grass-peat-fire/",
        edition="2025",
        owner="Fire and Rescue Department Brunei Darussalam",
        coverage="2012–2021, annual",
        published="2025-12-09",
    )
    return main, other, area


def prov(path: Path):
    return read_meta(path)[0]


def main():
    main_path, other_path, area_path = fetch()
    fires = load_fires(main_path)
    first, last = fires.year.min(), fires.year.max()

    fires["share_pct"] = fires.fires / fires.groupby("year").fires.transform("sum") * 100
    DISTRICT_SCHEMA.validate(fires)
    write_output(
        fires.round({"share_pct": 2}),
        OUT / "fire_by_district.csv",
        prov(main_path),
        notes=(
            f"Fire occurrences by district, {first}–{last}, from the 2009–2020 edition "
            "(owner as listed: Brunei Darussalam Central Bank). 'Brunei Muara' written as "
            "Brunei-Muara. District share of each year's total computed by the author."
        ),
    )

    totals = fires.groupby("year", as_index=False).fires.sum()
    totals["vs_median"] = totals.fires / totals.fires.median()
    area = load_area(area_path)
    totals = totals.merge(area[area.year <= last], on="year", how="left")
    TOTAL_SCHEMA.validate(totals)
    write_output(
        totals.round({"vs_median": 3, "forest_ha": 2, "grass_peat_ha": 2, "total_ha": 2}),
        OUT / "fire_totals.csv",
        prov(main_path) + prov(area_path),
        notes=(
            "Yearly fire occurrences (sum of districts) and each year ÷ the median year. Area "
            "of forest and grass/peat burned (hectares, 2012 onwards) from a separate Fire and "
            "Rescue table, shown beside the counts; the two measures are never added."
        ),
    )

    check = compare_editions(fires, load_fires(other_path))
    write_output(
        check,
        OUT / "fire_crosscheck.csv",
        prov(main_path) + prov(other_path),
        notes=(
            "Yearly totals in the two published editions for the years they share. Identical by "
            "district in 2009–2012; 2013 differs (see DATA_SOURCES.md), and the longer edition "
            "is used."
        ),
    )
    # Full cleaned tables, local only (data/clean/, policy §4 rule 3).
    write_clean(
        fires,
        __file__,
        "fire_by_district",
        prov(main_path),
        notes="Fire occurrences by district and year (2009–2020 edition), with district share.",
    )
    write_clean(
        load_fires(other_path),
        __file__,
        "fire_by_district_other_edition",
        prov(other_path),
        notes="Fire occurrences by district, Fire and Rescue 2009–2013 edition (cross-check).",
    )
    write_clean(
        area, __file__, "area_burned", prov(area_path), notes="Hectares burned by year and type."
    )
    report(fires, totals, check)


def report(fires: pd.DataFrame, totals: pd.DataFrame, check: pd.DataFrame):
    pd.set_option("display.width", 160)
    print("\n== Totals and area burned")
    print(totals.round(2).to_string(index=False))
    x = totals.dropna()
    print(
        f"\nCorrelation, fires vs hectares ({x.year.min()}–{x.year.max()}): "
        f"{x.fires.corr(x.total_ha):.2f}"
    )
    print("\n== District share of all fires")
    print((fires.groupby("district").fires.sum() / fires.fires.sum() * 100).round(1).to_string())
    print("\n== Editions")
    print(check.to_string(index=False))


if __name__ == "__main__":
    main()
