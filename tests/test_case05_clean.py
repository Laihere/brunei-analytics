"""Name handling, missing values and privacy rules for case study 05, on synthetic tables."""

import importlib.util

import pandas as pd
import pytest

from shared.paths import CASE_STUDIES

_spec = importlib.util.spec_from_file_location(
    "case05_clean", CASE_STUDIES / "05_agrifood_processing" / "analysis" / "clean.py"
)
clean = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(clean)


def _xlsx(tmp_path, name, df, **kw):
    path = tmp_path / name
    df.to_excel(path, index=False, **kw)
    return path


def test_category_spellings_map_to_one_name():
    assert clean._category("Mee") == clean._category("MI ") == ("Mi", "Noodles")
    assert clean._category("Biskut dan Bakeri") == clean._category("BISKUT & BAKERI")
    assert clean._category("LAIN-LAIN (Acar&Jeruk, Sagu)")[1] == "Other"
    with pytest.raises(ValueError, match="Unknown category"):
        clean._category("Kopi")


def test_series_drops_missing_year_and_recomputes_total(tmp_path):
    df = pd.DataFrame(
        {
            "Year": [2005, 2004, 2003],
            "Proses Ternakan": [2.0, 1.0, 9.0],
            "Proses Tanaman": [20.0, 10.0, "n/a"],
            "Kadar Kenaikan/Penurunan": [11.0, 2.0, None],
        }
    )
    out = clean.load_series(_xlsx(tmp_path, "s.xlsx", df))
    assert out.year.tolist() == [2004, 2005]
    assert out.total_bnd.tolist() == [11.0, 22.0]


def _cross_tab(counts):
    rows = []
    for cat, n in counts.items():
        rows += [(cat, "Brunei Muara", n, 1, 100.0), (cat, "Jumlah", n, 1, 100.0)]
    cols = ["Category", "District", "No. of Entrepreneur", "No. of Employees ", "Market Value (B$)"]
    return pd.DataFrame(rows, columns=cols)


def test_category_resting_on_few_businesses_is_refused(tmp_path):
    value = pd.DataFrame({"Category": ["Snek ", "Aiskrim"], "Market Value (B$)": [100.0, 100.0]})
    v = _xlsx(tmp_path, "v.xlsx", value)
    ok = clean.load_categories_2013(
        v, _xlsx(tmp_path, "ok.xlsx", _cross_tab({"SNEK": 7, "AISKRIM": 5}))
    )
    assert dict(zip(ok.category, ok.businesses, strict=True)) == {"Snacks": 7, "Ice cream": 5}
    few = _xlsx(tmp_path, "few.xlsx", _cross_tab({"SNEK": 7, "AISKRIM": 4}))
    with pytest.raises(ValueError, match="fewer than 5"):
        clean.load_categories_2013(v, few)
