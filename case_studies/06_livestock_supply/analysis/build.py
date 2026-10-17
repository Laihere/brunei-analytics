"""Build case study 06 outputs from data/raw/.

Run from the repo root:  uv run python case_studies/06_livestock_supply/analysis/build.py
"""

import sys
import warnings
from pathlib import Path

import pandas as pd
import pandera.pandas as pa

sys.path.insert(0, str(Path(__file__).parent))
from clean import PRODUCTS, compare_editions, read_table, slaughter_check, supply  # noqa: E402

from shared.clean_data import write_clean  # noqa: E402
from shared.fetch import download  # noqa: E402
from shared.outputs import write_output  # noqa: E402
from shared.provenance import read_meta  # noqa: E402

warnings.filterwarnings("ignore", message="Unknown extension")  # openpyxl, harmless
OUT = Path(__file__).resolve().parents[1] / "outputs"
FILES = "https://www.data.gov.bn/wp-content/uploads/2025/12/"
NEW_OWNER = "Agriculture and Agrifood Department"
OLD_OWNER = "Department of Agriculture and Agrifood, Ministry of Primary Resources and Tourism"
# key: (2020 file, title, slug, coverage), (2015 file, title, slug, coverage) or None
TABLES = {
    "chicken": (
        (
            "Broiler-Industry-1992-2020.xlsx",
            "BROILER INDUSTRY YEAR 1992-2020",
            "broiler-industry-year-1992-2020",
            "1992–2020, annual",
        ),
        (
            "Broiler-Industry-1992-2015.xlsx",
            "Broiler Industry, 1992-2015",
            "broiler-industry-1992-2015",
            "1992–2015, annual",
        ),
    ),
    "eggs": (
        (
            "Egg-Industry-1992-2020.xlsx",
            "Egg Industry, Year 1992-2020",
            "egg-industry-year-1992-2020",
            "1992–2020, annual",
        ),
        (
            "Egg-Industry-1992-2015.xlsx",
            "Egg Industry, 1992-2015",
            "egg-industry-1992-2015",
            "1992–2015, annual",
        ),
    ),
    "beef": (
        (
            "Beef-Industry-1995-2020.xlsx",
            "Beef Industry, Year 1995-2020",
            "beef-industry-year-1995-2020",
            "1995–2020, annual",
        ),
        (
            "Beef-Industry-1995-2015.xlsx",
            "Beef Industry, 1995-2015",
            "beef-industry-1995-2015",
            "1995–2015, annual",
        ),
    ),
    "chicks": (
        (
            "Day-Old-Chick-Industry-2001-2020.xlsx",
            "Day Old Chick Industry Year 2001-2020",
            "day-old-chick-industry-year-2001-2020",
            "2001–2020, annual",
        ),
        (
            "Day-Old-Chick-Industry-2001-2015.xlsx",
            "Day Old Chick Industry, 2001-2015",
            "day-old-chick-industry-2001-2015",
            "2001–2015, annual",
        ),
    ),
    "hatching_eggs": (
        (
            "Fertilized-Eggs-Industry-2001-2020.xlsx",
            "Fertilized Eggs Industry , Year 2011-2020",
            "fertilized-eggs-industry-year-2011-2020",
            "2001–2020, annual",
        ),
        (
            "Fertilized-Eggs-Industry-2001-2015.xlsx",
            "Fertilized Eggs Industry, 2011-2015",
            "fertilized-eggs-industry-2011-2015",
            "2001–2015, annual",
        ),
    ),
}
SLAUGHTER = (
    "Number-of-Slaughtered-Broilers-2011-2020.xlsx",
    "Number Of Slaughtered Broilers, 2011-2020",
    "number-of-slaughtered-broilers-2011-2020",
    "2011–2020, monthly",
)
KNOWN_REVISIONS = {"chicken": {2015: "imports revised in the 2020 edition (DATA_SOURCES issue 1)"}}

SUPPLY_SCHEMA = pa.DataFrameSchema(
    {
        "year": pa.Column(int),
        "product": pa.Column(str, pa.Check.isin(list(PRODUCTS))),
        "local": pa.Column(float, pa.Check.ge(0)),
        "imports": pa.Column(float, pa.Check.ge(0)),
        "local_share_pct": pa.Column(float, pa.Check.in_range(0, 100)),
    },
    unique=["year", "product"],
)


def get(file: str, title: str, slug: str, coverage: str, edition: str, owner: str, published: str):
    return download(
        source="datagovbn",
        file_url=FILES + file,
        title=title,
        page_url=f"https://www.data.gov.bn/{slug}/",
        edition=edition,
        owner=owner,
        coverage=coverage,
        published=published,
    )


def prov(*paths: Path):
    return [p for path in paths for p in read_meta(path)[0]]


def main():
    new = {k: get(*t[0], "2020", NEW_OWNER, "2025-12-04") for k, t in TABLES.items()}
    old = {k: get(*t[1], "2015", OLD_OWNER, "2025-12-11") for k, t in TABLES.items()}
    slaughter = get(*SLAUGHTER, "2020", NEW_OWNER, "2025-12-04")

    revisions = pd.concat(
        [compare_editions(new[k], old[k], KNOWN_REVISIONS.get(k)) for k in TABLES],
        ignore_index=True,
    )
    data = pd.concat([supply(k, new[k]) for k in TABLES], ignore_index=True)
    SUPPLY_SCHEMA.validate(data)
    write_output(
        data.round(
            {
                "local": 3,
                "imports": 3,
                "imports_alive": 3,
                "imports_chilled_frozen": 3,
                "local_share_pct": 2,
            }
        ),
        OUT / "livestock_supply.csv",
        prov(*new.values()),
        notes=(
            "Local production and imports by year from the Agriculture and Agrifood "
            "Department's 2020 editions. Local share = local ÷ (local + imports), computed by "
            "the author; no export figures are published, so it is not a full "
            "self-sufficiency ratio. Egg values are yearly despite the 'Monthly' label. Beef "
            "starts in 2000 (imports n/a before) and sums live and chilled & frozen imports; "
            "chilled & frozen imports are first recorded in 2005."
        ),
    )

    check = slaughter_check(slaughter, data[data["product"] == "chicken"])
    write_output(
        check.round(3),
        OUT / "chicken_slaughter_check.csv",
        prov(slaughter, new["chicken"]),
        notes=(
            "Birds slaughtered per year (published totals) beside local chicken meat. Tonnes "
            "equal birds × 1.5 kg in every year, so local chicken meat is estimated from bird "
            "counts. 2018's months sum to 9,608 birds less than the total (October repeats "
            "September); the total is used."
        ),
    )

    write_output(
        revisions,
        OUT / "edition_revisions.csv",
        prov(*new.values(), *old.values()),
        notes="Values that differ between the 2020 and 2015 editions for the years both cover.",
    )
    # Full cleaned tables, local only (data/clean/, policy §4 rule 3).
    write_clean(
        data,
        __file__,
        "livestock_supply",
        prov(*new.values()),
        notes="Local production, imports and local share by year and product (2020 editions).",
    )
    write_clean(
        read_table(slaughter).rename_axis("year").reset_index(),
        __file__,
        "broilers_slaughtered_monthly",
        prov(slaughter),
        notes="Birds slaughtered by month and the published yearly total, 2011–2020.",
    )
    report(data, check, revisions)


def report(data: pd.DataFrame, check: pd.DataFrame, revisions: pd.DataFrame):
    pd.set_option("display.width", 160)
    share = data.pivot(index="year", columns="product", values="local_share_pct")
    print("\n== Local share of supply (%)")
    print(share.round(1).to_string())
    print("\n== Slaughter check")
    print(check.round(3).to_string(index=False))
    print("\n== Edition revisions")
    print(revisions.to_string(index=False))


if __name__ == "__main__":
    main()
