"""Build case study 09 outputs from data/raw/.

Run from the repo root:  uv run python case_studies/09_retail_prices/analysis/build.py
"""

import sys
import warnings
from pathlib import Path

import pandas as pd
import pandera.pandas as pa

sys.path.insert(0, str(Path(__file__).parent))
from clean import (  # noqa: E402
    duplicate_year_differences,
    load_food,
    load_food_continued,
    load_nonfood,
    repeated_years,
)
from sources import fetch  # noqa: E402

from shared.clean_data import write_clean  # noqa: E402
from shared.outputs import write_output  # noqa: E402
from shared.provenance import read_meta  # noqa: E402

warnings.filterwarnings("ignore", message="Unknown extension")  # openpyxl, harmless
OUT = Path(__file__).resolve().parents[1] / "outputs"
FOOD_BASE, FOOD_LAST = 2013, 2018  # agreed 19 Oct 2026: 2010–2012 repeat for most items
REPEATED = [2010, 2011, 2012]
# Short sentence-case labels for charts; the published name stays in the `item` column
DISPLAY = {
    "Wheat Flour": "Wheat flour",
    "Buffalo Meat": "Buffalo meat",
    "Spanish Mackerel": "Spanish mackerel",
    "Indian Mackerel": "Indian mackerel",
    "Salted Anchovies": "Salted anchovies",
    "Fresh Prawns - Large": "Large fresh prawns",
    "Dried Prawn": "Dried prawns",
    "Pak Choy": "Pak choy",
    "Long Bean": "Long beans",
    "Fresh Chillies": "Fresh chillies",
}
MAX_EDITION_DIFF = 0.05  # B$; larger differences between editions would need a closer look

PRICES = pa.DataFrameSchema(
    {
        "year": pa.Column(int),
        "group": pa.Column(str),
        "label": pa.Column(str),
        "unit": pa.Column(str),
        "price_bnd": pa.Column(float, pa.Check.gt(0)),
    },
    unique=["year", "label"],
)


def prov(path: Path):
    return read_meta(path)[0]


def change_table(df: pd.DataFrame, first: int, last: int, extra: list[str]) -> pd.DataFrame:
    wide = df.pivot_table(index=["group", "label", "unit", *extra], values="price_bnd",
                          columns="year").reset_index()  # fmt: skip
    out = wide[["group", "label", "unit", *extra]].copy()
    out[f"price_{first}"], out[f"price_{last}"] = wide[first], wide[last]
    out["change_pct"] = (wide[last] / wide[first] - 1) * 100
    published_order = {lab: i for i, lab in enumerate(df.label.unique())}
    return out.sort_values("label", key=lambda s: s.map(published_order)).reset_index(drop=True)


def crosscheck(main: pd.DataFrame, other: pd.DataFrame, key: str, edition: str) -> dict:
    m = other.merge(main, on=["year", key], suffixes=("_other", "_main"))
    diff = (m.price_bnd_other - m.price_bnd_main).abs()
    return {
        "edition": edition,
        "years": f"{m.year.min()}–{m.year.max()}",
        "values_compared": len(m),
        "differences": int((diff > 0.005).sum()),
        "max_difference_bnd": round(diff.max(), 3),
    }


def main():
    p = fetch()

    # Food, 2010–2018 (one block per year kept; "-" items dropped: no prices published)
    food, food_groups = load_food(p["food"])
    if not ((food_groups.published_total - food_groups.items_sum).abs() < 0.01).all():
        raise ValueError("Food group rows are no longer the sum of their items: re-inspect.")
    not_published = sorted(food[food.price_bnd.isna()].label.unique())
    if not_published != ["Bread (gramme)", "Rice"]:
        raise ValueError(f"Items without prices changed: {not_published}")
    food = food.dropna(subset=["price_bnd"])
    PRICES.validate(food)
    repeat = repeated_years(food, REPEATED)
    food["repeated_2010_2012"] = food.label.map(repeat)
    base = food[food.year == FOOD_BASE].set_index("label").price_bnd
    food["index_2013"] = food.price_bnd / food.label.map(base) * 100
    food_change = change_table(food, FOOD_BASE, FOOD_LAST, [])

    # Non-food, 2015–2025 (the latest edition; two earlier editions as cross-checks)
    nonfood, _ = load_nonfood(p["nonfood"])
    PRICES.validate(nonfood)
    n0, n1 = int(nonfood.year.min()), int(nonfood.year.max())
    nonfood_change = change_table(nonfood, n0, n1, ["set_price"])

    continued = load_food_continued(p["food_continued"])
    checks = [crosscheck(food, continued, "label", "Food items (Continued), DEPD, 2010–2013")]
    for key, name in [
        ("nonfood_jpes", "Non-food items, Department of Statistics, JPES, 2015–2021"),
        (
            "nonfood_deps",
            "Non-food items, Department of Economic Planning and Statistics, 2015–2018",
        ),
    ]:
        other, _ = load_nonfood(p[key])
        checks.append(crosscheck(nonfood, other, "item", name))
    checks = pd.DataFrame(checks)
    if (checks.max_difference_bnd > MAX_EDITION_DIFF).any():
        raise ValueError(f"Editions differ by more than B${MAX_EDITION_DIFF}:\n{checks}")
    dup = duplicate_year_differences(p["food"])
    food["label"] = food.label.replace(DISPLAY)
    food_change["label"] = food_change.label.replace(DISPLAY)

    write_output(
        food[
            [
                "year",
                "group",
                "label",
                "item",
                "unit",
                "price_bnd",
                "repeated_2010_2012",
                "index_2013",
            ]
        ].round({"price_bnd": 2, "index_2013": 1}),  # fmt: skip
        OUT / "food_prices.csv",
        prov(p["food"]),
        notes=(
            f"Average retail prices of {food.label.nunique()} food items, "
            f"{food.year.min()}–{food.year.max()}, B$, as published. Group header rows, which "
            "hold the sum of their items' prices in unlike units, were dropped; the group is "
            "kept as a column. Rice and bread have no published prices ('-') and are left out. "
            "2013 is listed twice in the file; the second listing was kept (it differs only "
            "for salted anchovies, B$11.80 against B$11.81, and matches the 'Continued' "
            f"edition). 'repeated_2010_2012' marks the {int(repeat.sum())} items whose price is "
            "identical in 2010, 2011 and 2012. Index (2013 = 100) and short labels by the author."
        ),
    )
    write_output(
        food_change.round({"change_pct": 1}),
        OUT / "food_change.csv",
        prov(p["food"]),
        notes=(
            f"Change in each food item's average retail price from {FOOD_BASE} to {FOOD_LAST}, "
            f"%, computed by the author from unrounded prices. {FOOD_BASE} is the base because "
            "most items repeat the same price in 2010–2012."
        ),
    )
    write_output(
        nonfood.round({"price_bnd": 2}),
        OUT / "nonfood_prices.csv",
        prov(p["nonfood"]),
        notes=(
            f"Average retail prices of {nonfood.label.nunique()} non-food items, {n0}–{n1}, "
            "B$, as published. Group header rows (blank in this edition) dropped. "
            "'set_price' marks Government-set tariffs and fees (water, electricity, gas, "
            "passports), as classified by the author; the table itself doesn't say so. "
            "Units as given in the item names; 'unit not stated' where the table gives none."
        ),
    )
    write_output(
        nonfood_change.round({"change_pct": 1}),
        OUT / "nonfood_change.csv",
        prov(p["nonfood"]),
        notes=f"Change in each non-food item's price from {n0} to {n1}, %, computed by the author.",
    )
    write_output(
        checks,
        OUT / "retail_crosscheck.csv",
        prov(p["food_continued"]) + prov(p["nonfood_jpes"]) + prov(p["nonfood_deps"]),
        notes=(
            "Each other edition compared value by value with the main table for the years they "
            "share; a difference is anything above half a cent. Food names matched to the main "
            "table ('Sawi Putih' = Pak Choy)."
        ),
    )

    # Full cleaned tables, local only (data/clean/, policy §4 rule 3).
    write_clean(
        food, __file__, "food_prices", prov(p["food"]),
        notes="Food prices by item and year, with group, unit, repeat flag and index.",
    )  # fmt: skip
    write_clean(
        nonfood, __file__, "nonfood_prices", prov(p["nonfood"]),
        notes="Non-food prices by item and year, with group, unit and set-price flag.",
    )  # fmt: skip
    report(food_change, nonfood_change, checks, dup)


def report(food_change, nonfood_change, checks, dup):
    pd.set_option("display.width", 160)
    print("\n== Food change", FOOD_BASE, "→", FOOD_LAST)
    print(food_change.sort_values("change_pct").round(2).to_string(index=False))
    print("\n== Non-food change")
    print(nonfood_change.round(2).to_string(index=False))
    print("\n== Cross-checks")
    print(checks.to_string(index=False))
    print("\n== 2013 listed twice: differing values")
    print(dup.to_string(index=False))


if __name__ == "__main__":
    main()
