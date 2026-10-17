import json
import subprocess

import pandas as pd
import pytest

from shared.clean_data import STATUS, read_clean, write_clean
from shared.paths import ROOT
from shared.provenance import Provenance

PROV = Provenance(
    source="datagovbn",
    title="Consumer Price Index 2025",
    page_url="https://www.data.gov.bn/consumer-price-index-2025/",
    accessed="2026-10-15",
)
DF = pd.DataFrame({"year": [2024, 2025], "value": [1.123456789, 2.0]})
BUILD = ROOT / "case_studies" / "01_cost_of_living" / "analysis" / "build.py"


def test_saves_full_table_under_the_study_with_its_record(tmp_path):
    path = write_clean(DF, BUILD, "t", [PROV, PROV], "Renamed.", root=tmp_path)
    assert path == tmp_path / "01_cost_of_living" / "t.csv"
    df, provenance, notes = read_clean("01_cost_of_living", "t", root=tmp_path)
    assert df.value[0] == 1.123456789  # full precision, not rounded for publication
    assert provenance == [PROV] and notes == "Renamed."  # same dataset listed once
    meta = json.loads((tmp_path / "01_cost_of_living" / "t.csv.meta.json").read_text())
    assert meta["status"] == STATUS
    assert meta["rows"] == 2 and meta["columns"] == ["year", "value"]
    assert len(meta["clean_py_sha256"]) == 64
    assert meta["code_version"]


@pytest.mark.parametrize("provenance, notes", [([], "Renamed."), ([PROV], " ")])
def test_needs_sources_and_notes(tmp_path, provenance, notes):
    with pytest.raises(ValueError):
        write_clean(DF, BUILD, "t", provenance, notes, root=tmp_path)


def test_clean_data_is_gitignored_except_its_readme():
    def ignored(path: str) -> bool:
        return subprocess.run(["git", "check-ignore", "-q", path], cwd=ROOT).returncode == 0

    assert ignored("data/clean/01_cost_of_living/cpi_index.csv")
    assert ignored("data/clean/01_cost_of_living/cpi_index.csv.meta.json")
    assert not ignored("data/clean/README.md")


def test_every_case_study_keeps_its_cleaned_tables():
    for build in sorted(ROOT.glob("case_studies/[0-9]*/analysis/build.py")):
        assert "write_clean(" in build.read_text(), f"{build.parent.parent.name}: no write_clean"
