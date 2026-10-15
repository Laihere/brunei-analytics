"""Repair logic for case study 01, tested on small synthetic tables (raw data isn't in CI)."""

import importlib.util

import pandas as pd
import pytest

from shared.paths import CASE_STUDIES

_spec = importlib.util.spec_from_file_location(
    "case01_clean", CASE_STUDIES / "01_cost_of_living" / "analysis" / "clean.py"
)
clean = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(clean)

CATS = ["Overall CPI", "Food", "Clothing", "Misc"]
TRUE = {  # true index values
    2021: [100.0, 100.0, 100.0, 100.0],
    2022: [104.0, 110.0, 101.0, 120.0],
    2023: [104.4, 113.3, 100.5, 120.6],
}


def frames(index_rows):
    index = pd.DataFrame(
        [(y, c, v) for y, vals in index_rows.items() for c, v in zip(CATS, vals, strict=True)],
        columns=["year", "category", "index"],
    )
    pct = pd.DataFrame(
        [
            (y, c, (TRUE[y][i] / TRUE[y - 1][i] - 1) * 100)
            for y in (2022, 2023)
            for i, c in enumerate(CATS)
        ],
        columns=["year", "category", "pct_change"],
    )
    return index, pct


def test_repair_undoes_the_published_shift():
    o, f, c, m = TRUE[2023]
    published = {
        2021: TRUE[2021],
        2022: [m, *TRUE[2022][1:]],  # true 2023 Misc lands in 2022 Overall
        2023: [o, o, f, c],  # categories shifted one row down from Food
    }
    out = clean.repair_cpi(*frames(published))
    got = out.pivot(index="year", columns="category", values="index")[CATS]
    assert got.loc[2023].round(2).tolist() == TRUE[2023]
    assert got.loc[2022].round(2).tolist() == TRUE[2022]
    flagged = set(map(tuple, out[out.repaired][["year", "category"]].values))
    assert flagged == {(2022, "Overall CPI"), (2023, "Food"), (2023, "Clothing"), (2023, "Misc")}


def test_repair_refuses_when_data_still_disagrees():
    broken = {2021: TRUE[2021], 2022: TRUE[2022], 2023: TRUE[2023]}
    index, pct = frames(broken)
    index.loc[(index.year == 2021) & (index.category == "Food"), "index"] = 80.0
    with pytest.raises(ValueError, match="still differs"):
        clean.repair_cpi(index, pct)
