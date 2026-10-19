"""Retail price tables for case study 09 (synthetic)."""

import importlib.util

import pandas as pd
import pytest

from shared.paths import CASE_STUDIES

_spec = importlib.util.spec_from_file_location(
    "case09_clean", CASE_STUDIES / "09_retail_prices" / "analysis" / "clean.py"
)
clean = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(clean)

HEAD = "       Average Retail Price of Selected Food Item"  # leading spaces as published


def _xlsx(tmp_path, rows, name="f.xlsx"):
    path = tmp_path / name
    pd.DataFrame(rows, columns=["Year", HEAD, "BND Million"]).to_excel(path, index=False)
    return path


def _food_year(year, beef=12.5, flour=1.8):
    return [
        (year, "Rice and Cereals (Per Kilogramme)", flour),
        (year, "Rice", "-"),
        (year, "Wheat Flour ", flour),  # trailing space as published
        (year, "Fresh Meat and Poultry (Per Kilogramme)", beef + 4.4),
        (year, "Beef ", beef),
        (year, "Chicken ", 4.4),
    ]


def test_group_rows_become_a_column_and_their_sums_are_checked(tmp_path):
    food, groups = clean.load_food(_xlsx(tmp_path, _food_year(2018) + _food_year(2017)))
    assert set(food.group) == {"Rice and cereals", "Fresh meat and poultry"}
    assert "Fresh Meat and Poultry (Per Kilogramme)" not in set(food.item)
    assert food[food.label == "Rice"].price_bnd.isna().all()  # "-" is missing, not zero
    assert (groups.published_total - groups.items_sum).abs().max() < 1e-9
    assert food.unit.unique().tolist() == ["per kg"]


def test_a_year_listed_twice_keeps_the_second_listing(tmp_path):
    rows = _food_year(2013, beef=12.4) + _food_year(2013, beef=12.5) + _food_year(2012)
    path = _xlsx(tmp_path, rows)
    food, _ = clean.load_food(path)
    assert food[(food.year == 2013) & (food.label == "Beef")].price_bnd.tolist() == [12.5]
    diff = clean.duplicate_year_differences(path)
    assert set(diff.name) == {"Fresh Meat and Poultry (Per Kilogramme)", "Beef"}


def test_repeated_years_flags_identical_prices(tmp_path):
    rows = _food_year(2010) + _food_year(2011) + _food_year(2012, beef=13.0)
    food, _ = clean.load_food(_xlsx(tmp_path, rows))
    rep = clean.repeated_years(food.dropna(subset=["price_bnd"]), [2010, 2011, 2012])
    assert rep.to_dict() == {"Beef": False, "Chicken": True, "Wheat Flour": True}


def test_nonfood_marks_set_prices_and_refuses_unknown_items(tmp_path):
    rows = [
        (2025, "Housing, Water, Electricity, Gas and Other Fuels", None),
        (2025, "Cement (10 Kilogramme Bag)", 9.23),
        (2025, "Piped Gas", 5),
        (2025, "Miscellaneous Goods and Services", None),
        (2025, "Borneo Biometric Passport", 35),
    ]
    nf, _ = clean.load_nonfood(_xlsx(tmp_path, rows))
    assert nf.set_index("label").set_price.to_dict() == {
        "Cement": False,
        "Piped gas": True,
        "Borneo passport": True,
    }
    with pytest.raises(ValueError, match="label list"):
        clean.load_nonfood(_xlsx(tmp_path, rows + [(2025, "Postage Stamp", 0.5)], "b.xlsx"))
