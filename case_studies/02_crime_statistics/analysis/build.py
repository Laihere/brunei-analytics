"""Build case study 02 outputs from data/raw/.

Run from the repo root:  uv run python case_studies/02_crime_statistics/analysis/build.py

A newer edition of the table can be added as one more entry in EDITIONS.
"""

import sys
from pathlib import Path

import pandas as pd
import pandera.pandas as pa

sys.path.insert(0, str(Path(__file__).parent))
from clean import COUNTS, MIN_CASES, OTHER_ACTS, load, load_unmerged  # noqa: E402

from shared.clean_data import write_clean  # noqa: E402
from shared.fetch import download  # noqa: E402
from shared.outputs import write_output  # noqa: E402
from shared.provenance import read_meta  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "outputs"
OWNER = "Royal Brunei Police Force"
EDITIONS = [  # (year, file URL, dataset page)
    (
        "2012",
        "https://www.data.gov.bn/wp-content/uploads/2025/12/2-Crime-Statistics-2012.xlsx",
        "https://www.data.gov.bn/crime-statistics-2/",
    ),
    (
        "2013",
        "https://www.data.gov.bn/wp-content/uploads/2025/12/3-Crime-Statistics-2013.xlsx",
        "https://www.data.gov.bn/crime-statistics/",
    ),
]

_count = pa.Column("Int64", pa.Check.ge(0), nullable=True)
OFFENCE_SCHEMA = pa.DataFrameSchema(
    {
        "year": pa.Column(int),
        "handled_by": pa.Column(str, pa.Check.isin(["police", "other agencies"])),
        "offence": pa.Column(str),
        "offence_ms": pa.Column(str),
        "cases": pa.Column("Int64", pa.Check.ge(MIN_CASES)),  # SOP 7: no small cells
        "solved": _count,
        "arrests": _count,
        "complete": pa.Column(bool),
        "share_of_cases_pct": pa.Column(float, pa.Check.in_range(0, 100)),
        "solved_pct": pa.Column(float, pa.Check.in_range(0, 100), nullable=True),
    },
    unique=["year", "handled_by", "offence"],
)
TOTAL_SCHEMA = pa.DataFrameSchema(
    {
        "year": pa.Column(int),
        "handled_by": pa.Column(str),
        "cases": pa.Column("Int64", pa.Check.gt(0)),
        "solved": pa.Column("Int64", pa.Check.ge(0)),
        "arrests": pa.Column("Int64", pa.Check.ge(0)),
        "solved_pct": pa.Column(float, pa.Check.in_range(0, 100)),
        "cases_change_pct": pa.Column(float, nullable=True),
    },
    unique=["year", "handled_by"],
)


def fetch() -> tuple[list[Path], list]:
    paths = [
        download(
            source="datagovbn",
            file_url=url,
            title="Crime Statistics",
            page_url=page,
            edition=year,
            owner=OWNER,
            coverage=year,
            published="2025-12-17",
        )
        for year, url, page in EDITIONS
    ]
    return paths, [p for path in paths for p in read_meta(path)[0]]


def main():
    paths, sources = fetch()
    rows, totals = load(paths)
    first, last = rows.year.min(), rows.year.max()
    period = f"{first}–{last}"

    rows[COUNTS] = rows[COUNTS].round().astype("Int64")
    group = rows.groupby(["year", "handled_by"])["cases"].transform("sum")
    rows["share_of_cases_pct"] = (rows.cases / group * 100).astype(float).round(2)
    rows["solved_pct"] = (rows.solved / rows.cases * 100).astype(float).round(2)
    OFFENCE_SCHEMA.validate(rows)
    write_output(
        rows,
        OUT / "crime_offences.csv",
        sources,
        notes=(
            f"Cases, cases solved and persons arrested by type of offence, {period}, read from "
            "the stored values of the yearbook tables; rows checked against the published "
            f"totals. Other-agency Acts with fewer than {MIN_CASES} cases in any year merged "
            f"into '{OTHER_ACTS}'. '-' cells read as missing, so 'complete' is False where a "
            "solved or arrest count is a lower bound. Share and solved % computed by the author."
        ),
    )

    totals[COUNTS] = totals[COUNTS].round().astype("Int64")
    totals["solved_pct"] = (totals.solved / totals.cases * 100).astype(float).round(2)
    totals = totals.sort_values(["handled_by", "year"])
    totals["cases_change_pct"] = (
        totals.groupby("handled_by")["cases"].pct_change().astype(float).mul(100).round(2)
    )
    TOTAL_SCHEMA.validate(totals)
    write_output(
        totals.reset_index(drop=True),
        OUT / "crime_totals.csv",
        sources,
        notes=(
            f"Published total rows, {period}, as stored in the source (these count '-' as "
            "zero). Solved % and change on the previous year computed by the author."
        ),
    )
    # Full cleaned tables, local only (data/clean/, policy §4 rule 3). The unmerged rows
    # include Acts with small counts, which the published table merges into "Other Acts".
    unmerged, published_totals = load_unmerged(paths)
    write_clean(
        unmerged,
        __file__,
        "crime_offences_unmerged",
        sources,
        notes=(
            f"Every offence row as published, {period}, before small Acts are merged; checked "
            "against the published totals. '-' cells read as missing."
        ),
    )
    write_clean(
        published_totals,
        __file__,
        "crime_totals",
        sources,
        notes="Published total rows as stored ('-' counted as zero).",
    )
    report(rows, totals)


def report(rows: pd.DataFrame, totals: pd.DataFrame):
    pd.set_option("display.width", 160)
    print("\n== Published totals")
    print(totals.to_string(index=False))
    print("\n== By offence")
    cols = ["year", "handled_by", "offence", "cases", "share_of_cases_pct", "solved_pct"]
    print(rows[cols].to_string(index=False))


if __name__ == "__main__":
    main()
