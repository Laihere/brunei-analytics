"""Datasets for case study 08 (Muara Port), as listed on data.gov.bn (checked 17 Oct 2026).

Each dataset page has two files: the table and the Ports Department's data definition for it.
Titles and owner are copied exactly from the dataset pages.
"""

from pathlib import Path

from shared.fetch import download

SITE = "https://www.data.gov.bn/"
FILES = SITE + "wp-content/uploads/2025/12/"
OWNER = "Berthing Section and Statistic Unit, Ports Department"
PUBLISHED = "2025-12-11"

# key: (title as published, page slug, table file, definition file)
DATASETS = {
    "conventional": (
        "MUARA CONVENTIONAL TERMINAL, MUARA PORT 2004-2015",
        "muara-conventional-terminal-muara-port-2004-2015",
        "1.-MUARA-CONVENTIONAL-TERMINAL_MUARA-PORT-2004-2015.xlsx",
        "1.1-DATA-DEFINITION-MUARA-CONVENTIONAL-TERMINAL_MUARA-PORT-2004-2015.xlsx",
    ),
    "container": (
        "MUARA CONTAINER TERMINAL, MUARA PORT 2004-2015",
        "muara-container-terminal-muara-port-2004-2015",
        "2.-MUARA-CONTAINER-TERMINAL_MUARA-PORT-2004-2015.xlsx",
        "2.1-DATA-DEFINITION-MUARA-CONTAINER-TERMINAL_MUARA-PORT-2004-2015.xlsx",
    ),
    "vessel_calls": (
        "VESSEL CALLING (2004-2015)",
        "vessel-calling-2004-2015",
        "3.-VESSEL-CALL_MUARA-PORT-2004-2015.xlsx",
        "3.1-DATA-DEFINITION-VESSEL-CALL_MUARA-PORT-2004-2015.xlsx",
    ),
    "import_vessels": (
        "IMPORT VESSELS (2004 – 2015)",
        "import-vessels-2004-2015",
        "4.-IMPORT-VESSELS-2004-2015.xlsx",
        "4.1-DATA-DEFINITION-IMPORT-VESSEL.xlsx",
    ),
    "export_vessels": (
        "EXPORT VESSELS (2004-2015)",
        "export-vessels-2004-2015",
        "5.-EXPORT-VESSELS-2004-2015.xlsx",
        "5.1-DATA-DEFINITION-EXPORT-VESSEL.xlsx",
    ),
}


def fetch() -> dict[str, tuple[Path, Path]]:
    """Download each table and its definition file once; return {key: (table, definition)}."""
    paths = {}
    for key, (title, slug, table, definition) in DATASETS.items():
        got = [
            download(
                source="datagovbn",
                file_url=FILES + name,
                title=title,
                page_url=f"{SITE}{slug}/",
                edition="2015",
                owner=OWNER,
                coverage="2004–2015, annual",
                published=PUBLISHED,
            )
            for name in (table, definition)
        ]
        paths[key] = (got[0], got[1])
    return paths
