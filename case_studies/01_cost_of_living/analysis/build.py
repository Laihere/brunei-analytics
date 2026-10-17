"""Build case study 01 outputs from data/raw/.

Run from the repo root:  uv run python case_studies/01_cost_of_living/analysis/build.py
"""

import sys
from pathlib import Path

import pandas as pd
import pandera.pandas as pa

sys.path.insert(0, str(Path(__file__).parent))
from clean import OVERALL, load_cpi, load_items, repair_cpi  # noqa: E402

from shared.clean_data import write_clean  # noqa: E402
from shared.outputs import write_output  # noqa: E402
from shared.paths import RAW  # noqa: E402
from shared.provenance import read_meta  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "outputs"
BASE_YEAR = 2019  # last year before the pandemic; changes are shown relative to it

CPI = RAW / "datagovbn/2025/consumer-price-index/Consumer-Price-Index-2025.xlsx"
PCT = RAW / (
    "datagovbn/2025/percentage-change-in-customer-price-index/"
    "Percentage-Change-in-Consumer-Price-Index-2025.xlsx"
)
ITEMS = RAW / (
    "datagovbn/2025/average-retail-price-of-subsidised-items-and-under-price-control/"
    "Average-Retail-Price-of-Subsidised-Items-and-under-Price-Control-2025.xlsx"
)
WB_CPI = RAW / "worldbank/2026/consumer-price-index/FP_CPI_TOTL.csv"
WB_INF = RAW / "worldbank/2026/inflation-consumer-prices/FP_CPI_TOTL_ZG.csv"

INDEX_SCHEMA = pa.DataFrameSchema(
    {
        "year": pa.Column(int, pa.Check.in_range(2015, 2025)),
        "category": pa.Column(str),
        "index": pa.Column(float, pa.Check.in_range(50, 200)),
        "repaired": pa.Column(bool),
        "index_vs_base": pa.Column(float, pa.Check.in_range(50, 200)),
    },
    unique=["year", "category"],
)
ITEM_SCHEMA = pa.DataFrameSchema(
    {
        "year": pa.Column(int, pa.Check.in_range(2015, 2025)),
        "item": pa.Column(str),
        "price_bnd": pa.Column(float, pa.Check.gt(0)),
        "flag": pa.Column(str),
    },
    unique=["year", "item"],
)


def prov(path: Path):
    return read_meta(path)[0]


def main():
    index, pct = load_cpi(CPI, PCT)
    cpi = repair_cpi(index, pct)
    base = cpi[cpi.year == BASE_YEAR].set_index("category")["index"]
    cpi["index_vs_base"] = cpi["index"] / cpi["category"].map(base) * 100
    INDEX_SCHEMA.validate(cpi)

    cpi_sources = prov(CPI) + prov(PCT)
    write_output(
        cpi.round({"index": 3, "index_vs_base": 2}),
        OUT / "cpi_index.csv",
        cpi_sources,
        notes=(
            "Annual CPI by category, 2015–2025. Column 'Weight' renamed to 'index'. "
            "2023 categories and 2022 overall rebuilt as previous year × (1 + published % change) "
            "to fix a one-row shift in the source (flagged 'repaired'). "
            f"'index_vs_base' rebased to {BASE_YEAR} = 100."
        ),
    )

    write_output(
        pct.round({"pct_change": 2}),
        OUT / "cpi_change.csv",
        prov(PCT),
        notes="Published annual % change by category, 2016–2025. Category names trimmed.",
    )

    summary = (
        pct[pct.year == 2025]
        .set_index("category")["pct_change"]
        .rename("change_2025_pct")
        .to_frame()
    )
    summary[f"change_since_{BASE_YEAR}_pct"] = (
        cpi[cpi.year == 2025].set_index("category")["index_vs_base"] - 100
    )
    summary = summary.reset_index().sort_values(f"change_since_{BASE_YEAR}_pct", ascending=False)
    write_output(
        summary.round(2),
        OUT / "cpi_summary_2025.csv",
        cpi_sources,
        notes=(
            "2025 change: published annual % change. Change since "
            f"{BASE_YEAR}: 2025 index ÷ {BASE_YEAR} index, from the repaired series."
        ),
    )

    items = load_items(ITEMS)
    ITEM_SCHEMA.validate(items)
    write_output(
        items,
        OUT / "subsidised_prices.csv",
        prov(ITEMS),
        notes=(
            "Average retail prices (BND), 2015–2025. 'Saloon Car (1,500cc)' excluded (no data "
            "after 2019). Sugar 2024 flagged as implausible. 'Laila Rice' (to 2019) and "
            "'Local Rice' (from 2020) kept as separate series."
        ),
    )

    wb_cpi = pd.read_csv(WB_CPI).rename(columns={"value": "worldbank_index"})
    wb_inf = pd.read_csv(WB_INF).rename(columns={"value": "worldbank_change_pct"})
    overall = cpi[cpi.category == OVERALL][["year", "index", "repaired"]]
    published = pct[pct.category == OVERALL][["year", "pct_change"]]
    check = (
        overall.merge(published, on="year", how="left")
        .merge(wb_cpi, on="year", how="left")
        .merge(wb_inf, on="year", how="left")
        .rename(columns={"index": "datagovbn_index", "pct_change": "datagovbn_change_pct"})
    )
    write_output(
        check.round(3),
        OUT / "cpi_crosscheck.csv",
        cpi_sources + prov(WB_CPI) + prov(WB_INF),
        notes=(
            "Overall CPI from data.gov.bn (repaired) beside World Bank CPI and inflation "
            "(original source: IMF International Financial Statistics). Values unaltered."
        ),
    )
    # Full cleaned tables, local only (data/clean/, policy §4 rule 3).
    write_clean(
        cpi,
        __file__,
        "cpi_index",
        cpi_sources,
        notes=(
            "Annual CPI by category, 2015–2025, full precision, with the 2022–2023 repair "
            "flagged ('repaired') and rebased to 2019 = 100."
        ),
    )
    write_clean(pct, __file__, "cpi_change", prov(PCT), notes="Published annual % change.")
    write_clean(
        items,
        __file__,
        "subsidised_prices",
        prov(ITEMS),
        notes="Average retail prices (BND), long format; saloon car excluded.",
    )
    report(summary, items, check)


def report(summary: pd.DataFrame, items: pd.DataFrame, check: pd.DataFrame):
    pd.set_option("display.width", 140)
    print(f"\n== CPI by category: 2025 change and change since {BASE_YEAR} (%)")
    print(summary.to_string(index=False))
    w = items[items.flag == ""].pivot(index="item", columns="year", values="price_bnd")
    cols = [c for c in (BASE_YEAR, 2022, 2024, 2025) if c in w.columns]
    t = w[cols].copy()
    t[f"2025 vs {BASE_YEAR} %"] = (w[2025] / w[BASE_YEAR] - 1) * 100
    t["2025 vs 2024 %"] = (w[2025] / w[2024] - 1) * 100
    print("\n== Subsidised and price-controlled items (BND)")
    print(t.round(2).sort_values(f"2025 vs {BASE_YEAR} %", ascending=False).to_string())
    print("\n== Overall CPI cross-check")
    print(check.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
