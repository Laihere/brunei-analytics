import json

import pytest

from shared.fetch import adopt, dataset_dir, edition_of, sha256_of, slug_of
from shared.provenance import read_meta


def test_edition_is_year_in_title_else_year_published():
    assert edition_of("Consumer Price Index 2025") == "2025"
    assert edition_of("Consumer Price Index", published="2025-12-18") == "2025"
    with pytest.raises(ValueError):
        edition_of("Consumer Price Index")


def test_slug_drops_year_so_editions_line_up():
    assert slug_of("Consumer Price Index 2025") == "consumer-price-index"
    assert slug_of("Consumer Price Index 2024") == "consumer-price-index"
    assert (
        slug_of("Average Retail Price of Subsidised Items and under Price Control 2025")
        == "average-retail-price-of-subsidised-items-and-under-price-control"
    )


def test_dataset_dir_layout(tmp_path):
    folder = dataset_dir("datagovbn", "2025", "Consumer Price Index 2025", tmp_path)
    assert folder == tmp_path / "datagovbn" / "2025" / "consumer-price-index"
    # Same title and edition from different owners: kept apart by variant
    deps = dataset_dir("datagovbn", "2025", "Import, Export and Balance of Trade", tmp_path, "DEPS")
    assert deps.name == "import-export-and-balance-of-trade--deps"
    with pytest.raises(ValueError):
        dataset_dir("datagovbn", "latest", "x", tmp_path)
    with pytest.raises(ValueError):
        dataset_dir("imf", "2025", "x", tmp_path)


def test_adopt_moves_file_and_records_provenance(tmp_path):
    manual = tmp_path / "Consumer-Price-Index-2025.xlsx"
    manual.write_bytes(b"data")
    dest = adopt(
        manual,
        source="datagovbn",
        file_url="https://www.data.gov.bn/wp-content/uploads/Consumer-Price-Index-2025.xlsx",
        title="Consumer Price Index 2025",
        page_url="https://www.data.gov.bn/consumer-price-index-2025/",
        edition="2025",
        accessed="2026-10-15",
        owner="Department of Statistics, JPES",
        coverage="2015–2025",
        raw_dir=tmp_path / "raw",
    )
    assert not manual.exists()
    assert dest.parent == tmp_path / "raw" / "datagovbn" / "2025" / "consumer-price-index"
    (prov,), _ = read_meta(dest)
    assert prov.coverage == "2015–2025" and prov.edition == "2025"
    assert prov.sha256 == sha256_of(dest)
    assert json.loads(dest.with_name(dest.name + ".meta.json").read_text())["sources"]

    again = tmp_path / "Consumer-Price-Index-2025.xlsx"
    again.write_bytes(b"data")
    with pytest.raises(FileExistsError):
        adopt(
            again,
            "datagovbn",
            "u",
            "Consumer Price Index 2025",
            "p",
            "2025",
            "2026-10-15",
            raw_dir=tmp_path / "raw",
        )
