"""Datasets for case study 09 (retail prices), as listed on data.gov.bn (checked 19 Oct 2026).

Titles and owners are copied exactly from each dataset page; coverage is each page's "Time
Series (From–To)"; published is the page's listing date. `variant` keeps the two same-title
non-food editions in separate folders. The subsidised-items table is case study 01's and is
only linked from this study, not reused.
"""

from pathlib import Path

from shared.fetch import download

SITE = "https://www.data.gov.bn/"
DOS = "Department of Statistics, JPES"
DEPS = "Department of Economic Planning and Statistics"
DEPD = "Department of Economic Planning and Development"

# key: (title, page slug, file path under wp-content/uploads/, owner, coverage, published, variant)
DATASETS = {
    "food": (
        "Average Retail Price Of Selected Food Items",
        "average-retail-price-of-selected-food-items",
        "2025/12/Average-Retail-Price-of-Selected-Food-Item.xlsx",
        DEPS, "2010–2018, annual", "2025-12-18", "",
    ),
    "food_continued": (
        "Average Retail Price Of Selected Food Items (Continued)",
        "average-retail-price-of-selected-food-items-continued",
        "2025/12/7-Average-Retail-Price-Of-Selected-Food-Items-Continued.xlsx",
        DEPD, "2010–2013, annual", "2025-12-18", "",
    ),
    "nonfood": (
        "Average Retail Price of Selected Non-Food Items 2025",
        "average-retail-price-of-selected-non-food-items-2025",
        "Average-Retail-Price-of-Selected-Non-Food-Items-2025.xlsx",
        DOS, "2015–2025, annual", "2026-07-13", "",
    ),
    "nonfood_jpes": (
        "Average Retail Price of Selected Non-Food Items",
        "average-retail-price-of-selected-non-food-items",
        "2025/12/Average-Retail-Price-of-Selected-Non-Food-Items.xlsx",
        DOS, "2015–2021, annual", "2025-12-03", "dos-jpes",
    ),
    "nonfood_deps": (
        "Average Retail Price of Selected Non-Food Items",
        "average-retail-price-of-selected-non-food-items-2",
        "2025/12/Average-Retail-Price-of-Selected-Non-Food-Items-1.xlsx",
        DEPS, "2015–2018, annual", "2025-12-09", "deps",
    ),
}  # fmt: skip


def fetch() -> dict[str, Path]:
    """Download each dataset once (cached in data/raw/) and return its local path."""
    paths = {}
    for key, (title, slug, file, owner, coverage, published, variant) in DATASETS.items():
        edition = title[-4:] if title[-4:].isdigit() else published[:4]
        paths[key] = download(
            source="datagovbn",
            file_url=f"{SITE}wp-content/uploads/{file}",
            title=title,
            page_url=f"{SITE}{slug}/",
            edition=edition,
            owner=owner,
            coverage=coverage,
            published=published,
            variant=variant,
        )
    return paths
