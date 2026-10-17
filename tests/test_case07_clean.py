"""Trade totals, commodity sections and edition comparison for case study 07 (synthetic)."""

import importlib.util

import pandas as pd
import pytest

from shared.paths import CASE_STUDIES

_spec = importlib.util.spec_from_file_location(
    "case07_clean", CASE_STUDIES / "07_trade" / "analysis" / "clean.py"
)
clean = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(clean)


def _xlsx(tmp_path, name, rows, columns):
    path = tmp_path / name
    pd.DataFrame(rows, columns=columns).to_excel(path, index=False)
    return path


def _totals(tmp_path, balance=3.0, name="t.xlsx"):
    rows = [
        (2021, "Exports", 10.0),
        (2021, "Domestic Exports", 9.0),
        (2021, "Re-Exports", 1.0),
        (2021, "Imports", 7.0),
        (2021, "Total Trade", 17.0),
        (2021, "Balance of Trade", balance),
    ]
    return _xlsx(tmp_path, name, rows, ["Year", "Item", "BND Million "])


def test_trade_totals_become_one_column_per_measure(tmp_path):
    df = clean.load_trade(_totals(tmp_path))
    assert df.columns.tolist() == [
        "year", "exports", "domestic_exports", "re_exports", "imports", "total_trade", "balance"
    ]  # fmt: skip
    assert df.iloc[0].balance == 3.0


def test_trade_totals_must_add_up_within_rounding(tmp_path):
    clean.load_trade(_totals(tmp_path, balance=3.1))  # rounded to 0.1: fine
    with pytest.raises(ValueError, match="balance"):
        clean.load_trade(_totals(tmp_path, balance=4.0, name="bad.xlsx"))


def test_depd_edition_gets_exports_and_total_from_its_parts(tmp_path):
    rows = [
        (2013, "Export (Domestic Exports)", 9.0),
        (2013, "Export (Re-Exports)", 1.0),
        (2013, "Imports", 4.0),
        (2013, "Balance of Trade", 6.0),
    ]
    df = clean.load_trade(_xlsx(tmp_path, "d.xlsx", rows, ["Year", "Item", "Amount"]))
    assert df.iloc[0].exports == 10.0 and df.iloc[0].total_trade == 14.0


@pytest.mark.parametrize(
    "name, code",
    [
        ("Food", 0),
        ("Food and Live animals", 0),
        ("Crude Materials, Inedible", 2),
        ("Mineral fuels, Lubricants and Related Materials", 3),
        ("Animal and Vegetable Oils and Fats", 4),
        ("Vegetables Oil and Animals Fats", 4),
        ("Manufactured Goods by Materials", 6),
        ("Miscellaneous Manufactured Articles", 8),
        ("Miscellaneous Transaction and Commodities\nNot Elsewhere Classified", 9),
    ],
)
def test_section_names_from_every_edition_map_to_one_code(name, code):
    assert clean.sitc_code(name) == code


def test_unknown_section_stops_the_build():
    with pytest.raises(ValueError, match="Unknown commodity section"):
        clean.sitc_code("Services")


PUBLISHED = [  # Department of Statistics, JPES import table names
    "Food",
    "Beverages and Tobacco",
    "Crude Materials, Inedible",
    "Mineral fuels",
    "Animal and Vegetable Oils and Fats",
    "Chemicals",
    "Manufactured Goods",
    "Machinery and Transport Equipments",
    "Miscellaneous Manufactured Articles",
    "Miscellaneous Transaction",
]


def _sections(total=None, drop=None):
    rows = [(2021, PUBLISHED[c], float(c + 1)) for c in range(10) if c != drop]
    if total is not None:
        rows.insert(0, (2021, "Total Import", total))
    return rows


def test_import_sections_are_checked_against_total_import_row(tmp_path):
    cols = ["Year", "Total Import by Commodity Section", "BND Million"]
    ok = clean.load_sections(_xlsx(tmp_path, "i.xlsx", _sections(total=55.0), cols), "imports")
    assert len(ok) == 10 and ok.value_bnd_m.sum() == 55.0
    with pytest.raises(ValueError, match="Total Import"):
        clean.load_sections(_xlsx(tmp_path, "j.xlsx", _sections(total=60.0), cols), "imports")
    with pytest.raises(ValueError, match="missing a section"):
        clean.load_sections(_xlsx(tmp_path, "k.xlsx", _sections(drop=4), cols), "imports")


def test_editions_differ_only_beyond_rounding():
    main = pd.DataFrame({"year": [2018, 2019], "exports": [8446.785, 9886.2]})
    other = pd.DataFrame({"year": [2018, 2019], "exports": [8446.8, 9890.0]})
    diff = clean.compare_editions(main, other, ["year"])
    assert diff.year.tolist() == [2019]  # 2018 differs by rounding only
