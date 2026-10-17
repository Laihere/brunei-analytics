"""Build case study 07 outputs from data/raw/.

Run from the repo root:  uv run python case_studies/07_trade/analysis/build.py
"""

import sys
import warnings
from pathlib import Path

import pandas as pd
import pandera.pandas as pa

sys.path.insert(0, str(Path(__file__).parent))
from clean import (  # noqa: E402
    ROUNDING,
    compare_editions,
    load_classification,
    load_sections,
    load_trade,
)
from sources import DATASETS, fetch  # noqa: E402

from shared.clean_data import write_clean  # noqa: E402
from shared.outputs import write_output  # noqa: E402
from shared.provenance import read_meta  # noqa: E402

warnings.filterwarnings("ignore", message="Unknown extension")  # openpyxl, harmless
OUT = Path(__file__).resolve().parents[1] / "outputs"
MAIN = "dos"  # Department of Statistics, JPES: the longest editions (to 2021)
OTHERS = ["jpes", "deps"]

TOTAL_SCHEMA = pa.DataFrameSchema(
    {
        "year": pa.Column(int, unique=True),
        **{
            c: pa.Column(float, pa.Check.ge(0))
            for c in ["exports", "domestic_exports", "re_exports", "imports", "total_trade"]
        },
        "balance": pa.Column(float),
    }
)
SECTION_COLUMNS = ["year", "flow", "sitc", "section", "section_ms", "value_bnd_m", "share_pct"]
SECTION_SCHEMA = pa.DataFrameSchema(
    {
        "year": pa.Column(int),
        "flow": pa.Column(str, pa.Check.isin(["exports", "imports"])),
        "sitc": pa.Column(int, pa.Check.in_range(0, 9)),
        "value_bnd_m": pa.Column(float, pa.Check.ge(0)),
        "share_pct": pa.Column(float, pa.Check.in_range(0, 100)),
    },
    unique=["year", "flow", "sitc"],
)


def prov(*paths: Path):
    return [p for path in paths for p in read_meta(path)[0]]


def main():
    p = fetch()
    key = load_classification(p["classification"])

    trade = load_trade(p[f"trade_{MAIN}"])
    TOTAL_SCHEMA.validate(trade)
    first, last = trade.year.min(), trade.year.max()

    sections = pd.concat(
        [load_sections(p[f"{flow}_{MAIN}"], flow) for flow in ("exports", "imports")],
        ignore_index=True,
    )
    totals = trade.melt("year", ["exports", "imports"], var_name="flow", value_name="flow_total")
    sections = sections.merge(totals, on=["year", "flow"])
    gap = (
        sections.groupby(["year", "flow"]).value_bnd_m.sum()
        - sections.groupby(["year", "flow"]).flow_total.first()
    ).abs()
    if (gap > ROUNDING).any():
        raise ValueError("Commodity sections don't add up to the yearly export or import total.")
    sections["share_pct"] = sections.value_bnd_m / sections.flow_total * 100
    sections = sections.drop(columns="flow_total").merge(
        key[["sitc", "section", "section_ms"]], on="sitc"
    )
    sections = sections[SECTION_COLUMNS]
    sections = sections.sort_values(["flow", "year", "sitc"]).reset_index(drop=True)
    SECTION_SCHEMA.validate(sections)

    # Every other edition, compared with the main one for the years both cover.
    checks = []
    for ed in [*OTHERS, "depd"]:
        other = load_trade(p[f"trade_{ed}"])
        checks.append(("trade", ed, other, compare_editions(trade, other, ["year"])))
    for flow in ("exports", "imports"):
        main_flow = load_sections(p[f"{flow}_{MAIN}"], flow)
        for ed in OTHERS:
            other = load_sections(p[f"{flow}_{ed}"], flow)
            on = ["year", "flow", "sitc"]
            checks.append((flow, ed, other, compare_editions(main_flow, other, on)))
    crosscheck = pd.DataFrame(
        [
            {
                "table": table,
                "edition_owner": DATASETS[f"{table}_{ed}"][3],
                "years": f"{other.year.min()}–{other.year.max()}",
                "shared_years": int(other.year[other.year.isin(trade.year)].nunique()),
                "differences": len(diff),
            }
            for table, ed, other, diff in checks
        ]
    )
    if crosscheck.differences.any():
        raise ValueError(f"Editions disagree beyond rounding:\n{crosscheck}")

    main_files = [p[f"trade_{MAIN}"], p[f"exports_{MAIN}"], p[f"imports_{MAIN}"]]
    write_output(
        trade.round(3),
        OUT / "trade_totals.csv",
        prov(p[f"trade_{MAIN}"]),
        notes=(
            f"Exports (domestic and re-exports), imports, total trade and balance of trade, "
            f"{first}–{last}, BND million at current prices, from the Department of Statistics, "
            "JPES edition (it runs to 2021 although its page says 2020). Reshaped to one column "
            "per measure; published values unchanged (some are rounded to 0.1 million)."
        ),
    )
    write_output(
        sections.round({"value_bnd_m": 3, "share_pct": 2}),
        OUT / "trade_sections.csv",
        prov(*main_files[1:], p["classification"]) + prov(p[f"trade_{MAIN}"]),
        notes=(
            "Exports (2009 onwards) and imports (2000 onwards) by SITC commodity section (Revision "
            "3 to 2012 and Revision 4 from 2013, which keeps the same ten sections), "
            "BND million at current prices. Section names differ between editions, so sections "
            "are keyed by code and labelled from 'Classification Of Trade Commodities' (short "
            "English labels by the author; Malay names as published). Share = section ÷ that "
            "year's export or import total, computed by the author."
        ),
    )
    write_output(
        crosscheck,
        OUT / "trade_crosscheck.csv",
        prov(*[p[k] for k in DATASETS if k != "classification"]),
        notes=(
            "Each other edition compared value by value with the Department of Statistics, "
            "JPES edition for the years both cover. 'differences' counts values that differ by "
            f"more than {ROUNDING} million (more than rounding)."
        ),
    )

    # Full cleaned tables, local only (data/clean/, policy §4 rule 3).
    write_clean(
        trade,
        __file__,
        "trade_totals",
        prov(p[f"trade_{MAIN}"]),
        notes="Yearly trade totals, BND million, full precision as published.",
    )
    write_clean(
        sections,
        __file__,
        "trade_sections",
        prov(*main_files[1:], p["classification"]),
        notes="Exports and imports by SITC section with shares, full precision.",
    )
    write_clean(
        key,
        __file__,
        "sitc_sections",
        prov(p["classification"]),
        notes="SITC section key: official English and Malay names, short labels.",
    )
    report(trade, sections, crosscheck)


def report(trade: pd.DataFrame, sections: pd.DataFrame, crosscheck: pd.DataFrame):
    pd.set_option("display.width", 160)
    print("\n== Trade totals (BND million)")
    print(trade.round(1).to_string(index=False))
    share = sections.pivot_table(index="year", columns=["flow", "sitc"], values="share_pct")
    print("\n== Mineral fuels (3) and chemicals (5), % of flow")
    print(share.loc[:, [("exports", 3), ("exports", 5), ("imports", 3), ("imports", 7)]].round(1))
    print("\n== Edition cross-check")
    print(crosscheck.to_string(index=False))


if __name__ == "__main__":
    main()
