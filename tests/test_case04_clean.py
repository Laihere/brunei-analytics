"""Checks for case study 04, on small synthetic tables (raw data isn't in CI)."""

import importlib.util

import pandas as pd
import pytest

from shared.paths import CASE_STUDIES

_spec = importlib.util.spec_from_file_location(
    "case04_clean", CASE_STUDIES / "04_fire_occurrences" / "analysis" / "clean.py"
)
clean = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(clean)

NAMES = ["Brunei Muara", "Belait", "Tutong", "Temburong"]


def _fires(tmp_path, years, bump=None, name="f.xlsx"):
    rows = [
        (y, d, 10 * (i + 1) + (bump.get((y, d), 0) if bump else 0))
        for y in years
        for i, d in enumerate(NAMES)
    ]
    path = tmp_path / name
    pd.DataFrame(rows, columns=["Year", "District", "Amount"]).to_excel(path, index=False)
    return path


def test_districts_renamed_and_sorted(tmp_path):
    df = clean.load_fires(_fires(tmp_path, [2010, 2009]))
    assert set(df.district) == {"Brunei-Muara", "Belait", "Tutong", "Temburong"}
    assert df.year.tolist()[:4] == [2009] * 4


def test_missing_district_or_year_is_refused(tmp_path):
    path = tmp_path / "bad.xlsx"
    pd.DataFrame(
        [(2009, d, 1) for d in NAMES[:3]], columns=["Year", "District", "Amount"]
    ).to_excel(path, index=False)
    with pytest.raises(ValueError, match="districts"):
        clean.load_fires(path)
    with pytest.raises(ValueError, match="consecutive"):
        clean.load_fires(_fires(tmp_path, [2009, 2011]))


def test_editions_may_differ_only_in_known_years(tmp_path):
    main = clean.load_fires(_fires(tmp_path, [2012, 2013], name="a.xlsx"))
    known = clean.load_fires(
        _fires(tmp_path, [2012, 2013], bump={(2013, "Belait"): -5}, name="b.xlsx")
    )
    out = clean.compare_editions(main, known).set_index("year")
    assert out.loc[2012, "same_by_district"] and not out.loc[2013, "same_by_district"]
    unknown = clean.load_fires(
        _fires(tmp_path, [2012, 2013], bump={(2012, "Tutong"): 1}, name="c.xlsx")
    )
    with pytest.raises(ValueError, match="2012"):
        clean.compare_editions(main, unknown)


def test_area_is_summed_per_year(tmp_path):
    path = tmp_path / "area.xlsx"
    pd.DataFrame(
        [(2012, "FOREST FIRE ", 10.5), (2012, "GRASS/PEAT FIRE", 2.0)],
        columns=["YEAR", "TYPE", "HECTRES"],
    ).to_excel(path, index=False)
    area = clean.load_area(path)
    assert area.loc[0, "total_ha"] == pytest.approx(12.5)
