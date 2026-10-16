"""Parsing and privacy rules for case study 02, tested on small synthetic yearbook tables
(raw data isn't in CI)."""

import importlib.util

import openpyxl
import pytest

from shared.paths import CASE_STUDIES

_spec = importlib.util.spec_from_file_location(
    "case02_clean", CASE_STUDIES / "02_crime_statistics" / "analysis" / "clean.py"
)
clean = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(clean)

HEADER = [
    ["Jenis Kesalahan", "Jumlah", "Selesai", None, "Tangkapan"],
    ["Nature Of Offence", "Kes", "Solved", None, "Arrest"],
    [None, "Total", "Jumlah", "Peratus", "Orang"],
    [None, "Cases", "Total", "Percentage", "Person"],
]


def _yearbook(tmp_path, year, police, other, police_total=None):
    """Write a table laid out like the source: Malay row with counts, then the English row."""
    rows = [[f"14.2   Perangkaan Jenayah, {year}"], [f"   Crime Statistics, {year}"]]
    for section, data, total in (
        ("Cases Handled By Police", police, police_total),
        ("Cases Handled By Other Agencies", other, None),
    ):
        rows += [["Kes Dikendalikan"], [section], *HEADER]
        for ms, en, cases, solved, arrests in data:
            rows += [[ms, cases, solved, None, arrests], [en]]
        if total is None:
            total = [
                sum(0 if v == "-" else v for v in col)
                for col in zip(*(d[2:] for d in data), strict=True)
            ]
        rows += [["Jumlah", total[0], total[1], None, total[2]], ["Total"]]
    wb = openpyxl.Workbook()
    for r in rows:
        wb.active.append(r)
    path = tmp_path / f"crime-{year}.xlsx"
    wb.save(path)
    return path


POLICE = [
    ("Terhadap Harta Benda", "Against Property", 300, 40, 30),
    ("Terhadap Tubuh Manusia", "Against Human Body", 60, 45, 20),
]
OTHER_2012 = [
    ("Terhadap Akta Kastam", "Against Customs Act", 30, 29, 40),
    ("Terhadap Akta Buruh", "Against Labour Act", 8, "-", "-"),
    ("Terhadap Akta Rasuah", "Against Corruption Act", 3, 3, 3),
    ("Terhadap Akta KDN", "Against Internal Security Act", 2, "-", "-"),
]
OTHER_2013 = [
    ("Terhadap Akta Kastam", "Against Customs Act", 35, 30, 41),
    ("Terhadap Akta Buruh", "Against Labour Act", 9, "-", "-"),
    ("Terhadap Akta Rasuah", "Against Corruption Act", 9, 9, 9),
]


def test_reads_year_rows_labels_and_totals(tmp_path):
    rows, totals = clean.read_table(_yearbook(tmp_path, 2012, POLICE, OTHER_2012))
    assert set(rows.year) == {2012}
    police = rows[rows.handled_by == "police"].set_index("offence")
    assert police.loc["Against Property", "cases"] == 300
    assert police.loc["Against Property", "offence_ms"] == "Terhadap Harta Benda"
    labour = rows[rows.offence == "Against Labour Act"].iloc[0]
    assert labour.cases == 8 and labour[["solved", "arrests"]].isna().all()  # "-" is missing
    assert len(totals) == 2


def test_rows_must_add_up_to_published_totals(tmp_path):
    path = _yearbook(tmp_path, 2012, POLICE, OTHER_2012, police_total=[361, 85, 50])
    with pytest.raises(ValueError, match="published totals"):
        clean.load([path])


def test_small_acts_are_merged_across_years(tmp_path):
    paths = [
        _yearbook(tmp_path, 2012, POLICE, OTHER_2012),
        _yearbook(tmp_path, 2013, POLICE, OTHER_2013),
    ]
    rows, _ = clean.load(paths)
    other = rows[rows.handled_by == "other agencies"].set_index(["year", "offence"])
    # Corruption has 9 cases in 2013 but 3 in 2012, so it is merged in both years.
    assert set(other.index.get_level_values("offence")) == {
        "Against Customs Act",
        "Against Labour Act",
        clean.OTHER_ACTS,
    }
    assert other.loc[(2012, clean.OTHER_ACTS), "cases"] == 5  # 3 + 2
    assert not other.loc[(2012, clean.OTHER_ACTS), "complete"]  # includes a "-" cell
    assert other.loc[(2013, clean.OTHER_ACTS), "complete"]
    assert (rows.cases >= clean.MIN_CASES).all()


def test_merged_group_below_limit_is_refused(tmp_path):
    tiny = [OTHER_2012[0], ("Terhadap Akta Ugama", "Against Religious Act", 1, 1, 1)]
    with pytest.raises(ValueError, match="small-count"):
        clean.load([_yearbook(tmp_path, 2012, POLICE, tiny)])
