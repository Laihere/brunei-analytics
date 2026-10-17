"""Container and cargo tables for case study 08 (synthetic)."""

import importlib.util

import pandas as pd
import pytest

from shared.paths import CASE_STUDIES

_spec = importlib.util.spec_from_file_location(
    "case08_clean", CASE_STUDIES / "08_muara_port" / "analysis" / "clean.py"
)
clean = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(clean)


def _xlsx(tmp_path, name, df):
    path = tmp_path / name
    df.to_excel(path, index=False)
    return path


def _containers(years=(2014, 2015), total=(110.0, 50.0)):
    return pd.DataFrame(
        {
            "Year": list(years),
            "Local Containers (TEUs) ": [100.0, 40.0],  # trailing space as published
            "Transhipment Containers (TEUs) ": [8.0, 10.0],
            "Total Containers (TEUs)": list(total),
            "Unnamed: 4": [None, None],  # spacer column
        }
    )


def test_containers_keep_published_total_and_the_sum(tmp_path):
    df = clean.load_containers(_xlsx(tmp_path, "c.xlsx", _containers()))
    assert df.total_teu.tolist() == [108.0, 50.0]
    assert df.gap_teu.tolist() == [2.0, 0.0]  # published − (local + transhipment)
    assert df.transhipment_share_pct.round(1).tolist() == [7.4, 20.0]


def test_years_must_be_consecutive(tmp_path):
    with pytest.raises(ValueError, match="consecutive"):
        clean.load_containers(_xlsx(tmp_path, "c.xlsx", _containers(years=(2013, 2015))))


def test_cargo_must_be_positive(tmp_path):
    ok = pd.DataFrame({"Year": [2014, 2015], "Uncontainerized Cargo (Tonnage)": [5.0, 7.0]})
    assert clean.load_cargo(_xlsx(tmp_path, "g.xlsx", ok)).cargo_tonnes.sum() == 12.0
    bad = ok.assign(**{"Uncontainerized Cargo (Tonnage)": [5.0, 0.0]})
    with pytest.raises(ValueError, match="positive"):
        clean.load_cargo(_xlsx(tmp_path, "b.xlsx", bad))
