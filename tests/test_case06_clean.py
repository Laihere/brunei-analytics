"""Supply tables, edition comparison and the slaughter check for case study 06 (synthetic)."""

import importlib.util

import pandas as pd
import pytest

from shared.paths import CASE_STUDIES

_spec = importlib.util.spec_from_file_location(
    "case06_clean", CASE_STUDIES / "06_livestock_supply" / "analysis" / "clean.py"
)
clean = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(clean)


def _xlsx(tmp_path, name, df):
    path = tmp_path / name
    df.to_excel(path, index=False)
    return path


def _broiler(tmp_path, name="b.xlsx", imports=(1.0, 2.0, 3.0)):
    df = pd.DataFrame(
        {
            "Year": [2012, 2011, 2010],
            "Local Production (mt)": [9.0, 8.0, 7.0],
            "Import (mt)": imports,
        }
    )
    return _xlsx(tmp_path, name, df)


def test_local_share_and_order(tmp_path):
    out = clean.supply("chicken", _broiler(tmp_path))
    assert out.year.tolist() == [2010, 2011, 2012]
    assert out.local_share_pct.tolist() == pytest.approx([70.0, 80.0, 90.0])


def test_beef_drops_na_years_and_sums_import_types(tmp_path):
    df = pd.DataFrame(
        {
            "Year": [2001, 2000, 1999],
            "Local Production (mt)": [1.0, 2.0, 3.0],
            "Import (Alive) (mt)": [5.0, 6.0, "n/a"],
            "Import (Chilled & Frozen) (mt)": [4.0, 0.0, "n/a"],
        }
    )
    out = clean.supply("beef", _xlsx(tmp_path, "beef.xlsx", df)).set_index("year")
    assert out.index.tolist() == [2000, 2001]
    assert out.loc[2001, "imports"] == 9.0 and out.loc[2001, "imports_alive"] == 5.0


def test_edition_differences_must_be_known(tmp_path):
    new, old = _broiler(tmp_path, "new.xlsx"), _broiler(tmp_path, "old.xlsx", (1.0, 2.5, 3.0))
    known = clean.compare_editions(new, old, {2011: "revised"})
    assert known.year.tolist() == [2011]
    with pytest.raises(ValueError, match="2011"):
        clean.compare_editions(new, old)


def test_slaughter_check_requires_fixed_weight_per_bird(tmp_path):
    chicken = pd.DataFrame({"year": [2011], "local": [15.0]})  # tonnes
    months = {m: [1000] for m in ["January", "February"]}
    ok = _xlsx(tmp_path, "s.xlsx", pd.DataFrame({"Year": [2011], **months, "Total": [10000]}))
    assert clean.slaughter_check(ok, chicken).kg_per_bird.iloc[0] == pytest.approx(1.5)
    bad = _xlsx(tmp_path, "t.xlsx", pd.DataFrame({"Year": [2011], **months, "Total": [9000]}))
    with pytest.raises(ValueError, match="1.5 kg"):
        clean.slaughter_check(bad, chicken)
