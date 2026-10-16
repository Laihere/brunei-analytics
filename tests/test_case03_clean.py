"""Reshaping, checks and period averages for case study 03, on small synthetic tables
(raw data isn't in CI)."""

import importlib.util

import pandas as pd
import pytest

from shared.paths import CASE_STUDIES

_spec = importlib.util.spec_from_file_location(
    "case03_clean", CASE_STUDIES / "03_road_casualties" / "analysis" / "clean.py"
)
clean = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(clean)


def _police(tmp_path, records):
    path = tmp_path / "road.xlsx"
    pd.DataFrame(records, columns=["Year", "Type", "Amount"]).to_excel(path, index=False)
    return path


def _records(years):
    out = []
    for i, y in enumerate(years):
        out += [(y, "Injuries", 100 + i), (y, "Accidents ", 1000), (y, "Deaths", 10 + i)]
    return out


def test_long_table_becomes_one_row_per_year(tmp_path):
    roads = clean.load_police(_police(tmp_path, _records([2011, 2010, 2009])))
    assert roads.columns.tolist() == ["year", "accidents", "injuries", "deaths"]
    assert roads.year.tolist() == [2009, 2010, 2011]
    assert roads.set_index("year").loc[2009, "injuries"] == 102  # newest first in the source


def test_missing_year_or_measure_is_refused(tmp_path):
    with pytest.raises(ValueError, match="consecutive"):
        clean.load_police(_police(tmp_path, _records([2009, 2011])))
    records = _records([2009, 2010])[:-1]  # 2010 has no deaths
    with pytest.raises(ValueError, match="missing a measure"):
        clean.load_police(_police(tmp_path, records))


def test_period_ratio_uses_totals_not_average_of_ratios(tmp_path):
    roads = pd.DataFrame(
        {
            "year": [2009, 2010, 2011],
            "accidents": [100, 300, 200],
            "injuries": [50, 30, 40],
            "deaths": [1, 2, 3],
        }
    )
    p = clean.periods(clean.add_ratios(roads)).iloc[0]
    assert p.period == "2009–2011"
    assert p.injuries_per_100_accidents == pytest.approx(120 / 600 * 100)


def test_years_must_split_into_whole_periods():
    roads = pd.DataFrame({"year": [2009, 2010], "accidents": 1, "injuries": 1, "deaths": 1})
    with pytest.raises(ValueError, match="periods"):
        clean.periods(roads)


def test_fire_rescue_years_are_filled_and_summed(tmp_path):
    path = tmp_path / "fr.xlsx"
    rows = [
        ["YEAR", "TYPE OF CALL", "DEAD", "INJURED"],
        [2013, "CAR ACCIDENT", 11, 107],
        [None, "CAR ACCIDENT INVOLVING FIRE", 0, 2],
        [2012, "CAR ACCIDENT", 16, 141],
        [None, "CAR ACCIDENT INVOLVING FIRE", 1, 0],
    ]
    pd.DataFrame([[None] * 4, *rows]).to_excel(path, index=False, header=False)
    fr = clean.load_fire_rescue(path).set_index("year")
    assert fr.loc[2012].tolist() == [17, 141]
    assert fr.loc[2013].tolist() == [11, 109]
