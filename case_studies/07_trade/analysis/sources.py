"""Datasets for case study 07 (trade), as listed on data.gov.bn (checked 17 Oct 2026).

The same tables are published several times under different owners. Titles and owners are
copied exactly from each dataset page, including "Inport" in the DEPD edition's title. Coverage
is each page's "Time Series (From–To)". `variant` keeps same-title copies in separate folders.
"""

from pathlib import Path

from shared.fetch import download

SITE = "https://www.data.gov.bn/"
DOS = "Department of Statistics, JPES"
JPES = "JPES"
DEPS = "Department of Economic Planning and Statistics"
DEPD = "Department of Economic Planning and Development"

# key: (title, page slug, file path under wp-content/uploads/, owner, coverage, published, variant)
DATASETS = {
    # Import, export and balance of trade, yearly totals
    "trade_dos": (
        "Import, Export and Balance of Trade",
        "import-export-and-balance-of-trade",
        "2025/11/Import-Export-and-Balance-of-Trade.xlsx",
        DOS, "2000–2020, annual", "2025-11-15", "dos-jpes",
    ),
    "trade_jpes": (
        "Import, Export and Balance of Trade",
        "import-export-and-balance-of-trade-2",
        "2025/12/Import-Export-and-Balance-of-Trade.xlsx",
        JPES, "2000–2020, annual", "2025-12-04", "jpes",
    ),
    "trade_deps": (
        "Import, Export And Balance Of Trade",
        "import-export-and-balance-of-trade-3",
        "2025/12/Import-Export-and-Balance-of-Trade-1.xlsx",
        DEPS, "2000–2018, annual", "2025-12-17", "deps",
    ),
    "trade_depd": (
        "Inport, Export And Balance Of Trade",
        "inport-export-and-balance-of-trade",
        "2025/12/2-Inport-Export-And-Balance-Of-Trade.xlsx",
        DEPD, "2009–2013, annual", "2025-12-17", "depd",
    ),
    # Exports and imports by commodity section (SITC sections)
    "exports_dos": (
        "Total Export By Commodity Section",
        "total-export-by-commodity-section",
        "2025/11/Total-Export-By-Commodity-Section.xls.xlsx",
        DOS, "2009–2021, annual", "2025-11-15", "dos-jpes",
    ),
    "exports_jpes": (
        "Total Export By Commodity Section",
        "total-export-by-commodity-section-2",
        "2025/12/Total-Export-By-Commodity-Section.xls.xlsx",
        JPES, "2009–2020, annual", "2025-12-04", "jpes",
    ),
    "exports_deps": (
        "Total Export By Commodity Section",
        "total-export-by-commodity-section-3",
        "2025/12/Total-Export-by-Commodity-Section.xlsx",
        DEPS, "2009–2018, annual", "2025-12-17", "deps",
    ),
    "imports_dos": (
        "Total Import by Commodity Section",
        "total-import-by-commodity-section",
        "2025/11/Total-Import-by-Commodity-Section.xlsx",
        DOS, "2000–2021, annual", "2025-11-15", "dos-jpes",
    ),
    "imports_jpes": (
        "Total Import by Commodity Section",
        "total-import-by-commodity-section-2",
        "2025/12/Total-Import-by-Commodity-Section.xlsx",
        JPES, "2000–2020, annual", "2025-12-04", "jpes",
    ),
    "imports_deps": (
        "Total Import By Commodity Section",
        "total-import-by-commodity-section-3",
        "2025/12/Total-Import-by-Commodity-Section-1.xlsx",
        DEPS, "2000–2018, annual", "2025-12-17", "deps",
    ),
    # Label key for the commodity sections
    "classification": (
        "Classification Of Trade Commodities",
        "classification-of-trade-commodities",
        "2025/12/1-Classification-Of-Trade-Commodities.xlsx",
        DEPD, "2009–2013", "2025-12-18", "depd",
    ),
}  # fmt: skip


def fetch() -> dict[str, Path]:
    """Download each dataset once (cached in data/raw/) and return its local path."""
    paths = {}
    for key, (title, slug, file, owner, coverage, published, variant) in DATASETS.items():
        paths[key] = download(
            source="datagovbn",
            file_url=f"{SITE}wp-content/uploads/{file}",
            title=title,
            page_url=f"{SITE}{slug}/",
            edition=published[:4],
            owner=owner,
            coverage=coverage,
            published=published,
            variant=variant,
        )
    return paths
