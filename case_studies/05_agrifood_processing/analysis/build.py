"""Build case study 05 outputs from data/raw/.

Run from the repo root:  uv run python case_studies/05_agrifood_processing/analysis/build.py
"""

import sys
from pathlib import Path

import pandas as pd
import pandera.pandas as pa

sys.path.insert(0, str(Path(__file__).parent))
from clean import (  # noqa: E402
    NEW_IN_2013,
    load_categories_2013,
    load_cross_tab,
    load_districts,
    load_series,
    load_trend,
)

from shared.charts import item_status  # noqa: E402
from shared.clean_data import write_clean  # noqa: E402
from shared.fetch import download  # noqa: E402
from shared.outputs import write_output  # noqa: E402
from shared.provenance import read_meta  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "outputs"
FILES = "https://www.data.gov.bn/wp-content/uploads/2025/12/"
OWNER = "Ministry of Industry and Primary Resources"
DATASETS = {  # key: (file, title as published, English title, page slug, coverage)
    "series": (
        "STATUS-PENGELUARAN-PRODUK-AGRIMAKANAN-2003-2012.xlsx",
        "Status Pengeluaran Produck Agrimakanan",
        "Status of agrifood product production",
        "status-pengeluaran-produck-agrimakanan",
        "2003–2013, annual",
    ),
    "trend": (
        "TREN-PENGELUARAN-AGRIMAKANAN-MENGIKUT-KATEGORI-PRODUK-2010-2013.xlsx",
        "Tren Pengeluaran Agrimakanan Mengikut Kategori Produk",
        "Agrifood production trends by product category",
        "tren-pengeluaran-agrimakanan-mengikut-kategori-produk",
        "2010–2013, annual",
    ),
    "categories": (
        "STATISTIK-INDUSTRI-AGRIMAKANAN-2013.xlsx",
        "Statistik Industri Agrimakanan",
        "Agrifood industry statistics",
        "statistik-industri-agrimakanan",
        "2013",
    ),
    "cross_tab": (
        "STATISTIK-INDUSTRI-AGRIMAKANAN-MENGIKUT-DAERAH-DAN-KATEGORI-PRODUK-2013.xlsx",
        "Statistik Industri Agrimakanan Mengikut Daerah Dan Kategori Produck",
        "Agrifood industry statistics by district and product category",
        "statistik-industri-agrimakanan-mengikut-daerah-dan-kategori-produck",
        "2013",
    ),
    "districts": (
        "STATUS-PENGELUARAN-AGRIMAKANAN-MENGIKUT-DAERAH-2013.xlsx",
        "Status Pengeluaran Agrimakanan Mengikut Daerah",
        "Status of agrifood production by district",
        "status-pengeluaran-agrimakanan-mengikut-daerah",
        "2013",
    ),
}

SERIES_SCHEMA = pa.DataFrameSchema(
    {
        "year": pa.Column(int),
        "livestock_bnd": pa.Column(float, pa.Check.gt(0)),
        "crop_bnd": pa.Column(float, pa.Check.gt(0)),
        "total_bnd": pa.Column(float, pa.Check.gt(0)),
        "new_category_bnd": pa.Column(float, pa.Check.ge(0)),
        "comparable_bnd": pa.Column(float, pa.Check.gt(0)),
    },
    unique=["year"],
)


def fetch() -> dict[str, Path]:
    return {
        key: download(
            source="datagovbn",
            file_url=FILES + file,
            title=title,
            page_url=f"https://www.data.gov.bn/{slug}/",
            edition="2025",
            owner=OWNER,
            coverage=coverage,
            published="2025-12-22",
            title_translation=english,
        )
        for key, (file, title, english, slug, coverage) in DATASETS.items()
    }


def prov(*paths: Path):
    return [p for path in paths for p in read_meta(path)[0]]


def main():
    f = fetch()
    series = load_series(f["series"])
    trend = load_trend(f["trend"])
    first, last = series.year.min(), series.year.max()

    # The category table (2010–2013) must add up to the series in every shared year.
    by_year = trend.groupby("year").value_bnd.sum()
    gap = (series.set_index("year").total_bnd.reindex(by_year.index) - by_year).abs().max()
    if gap > 10_000:  # the 2010 category values are rounded to B$0.01 million
        raise ValueError(f"Category totals differ from the series by B${gap:,.0f}.")

    new = trend[trend.category_ms == NEW_IN_2013].set_index("year").value_bnd
    series["new_category_bnd"] = series.year.map(new).fillna(0.0)
    series["comparable_bnd"] = series.total_bnd - series.new_category_bnd
    SERIES_SCHEMA.validate(series)
    write_output(
        series.round(2),
        OUT / "agrifood_series.csv",
        prov(f["series"], f["trend"]),
        notes=(
            f"Market value of processed agrifood products, {first}–{last}, current Brunei "
            "dollars. 2003 dropped (crop-based value not available). Totals recomputed; the "
            "published change column was not used. 'new_category_bnd' is 'Makanan Segera' "
            "(fast or instant food), first counted in 2013 (0 in 2010–2012 in the category "
            "table, which starts in 2010); 'comparable_bnd' leaves it out."
        ),
    )

    t0, t1 = trend.year.min(), trend.year.max()
    trend["status"] = trend.category.map(
        item_status(trend, "category", "year", "value_bnd", t0, t1)
    )
    write_output(
        trend.round(2),
        OUT / "agrifood_categories_2010_2013.csv",
        prov(f["trend"]),
        notes=(
            "Market value by product category, 2010–2013, converted from B$ million to B$. "
            "Malay names standardised and translated by the author; 'Acar & Jeruk' (pickles) "
            "merged into Other. 'status' compares 2010 with 2013: continued, new (0 in 2010) or "
            "discontinued (0 in 2013)."
        ),
    )

    cats = load_categories_2013(f["categories"], f["cross_tab"])
    write_output(
        cats.round(2),
        OUT / "agrifood_categories_2013.csv",
        prov(f["categories"], f["cross_tab"]),
        notes=(
            "2013 market value by product category, with the number of businesses making each "
            "product (summed from the category × district table, which counts a business once "
            "per category it makes). The category × district cells themselves are not "
            "published, because many rest on fewer than 5 businesses."
        ),
    )

    districts = load_districts(f["districts"])
    write_output(
        districts.round(2),
        OUT / "agrifood_districts_2013.csv",
        prov(f["districts"]),
        notes=(
            "2013 businesses, employees and market value by district, from the district table "
            "('Brunei/Muara' written as Brunei-Muara). Shares computed by the author."
        ),
    )
    # Full cleaned tables, local only (data/clean/, policy §4 rule 3). The category ×
    # district cells include very small business counts and are never published.
    write_clean(
        series,
        __file__,
        "agrifood_series",
        prov(f["series"], f["trend"]),
        notes="Market value of processed agrifood products by year, with comparable totals.",
    )
    write_clean(
        trend,
        __file__,
        "agrifood_categories_2010_2013",
        prov(f["trend"]),
        notes="Market value by category, 2010–2013, in B$, names translated, with status.",
    )
    write_clean(
        load_cross_tab(f["cross_tab"]),
        __file__,
        "agrifood_category_by_district_2013",
        prov(f["cross_tab"]),
        notes=(
            "2013 businesses, employees and market value by category and district; total rows "
            "dropped. Contains cells with 1–4 businesses: local reference only."
        ),
    )
    write_clean(
        districts,
        __file__,
        "agrifood_districts_2013",
        prov(f["districts"]),
        notes="2013 businesses, employees and market value by district, with shares.",
    )
    report(series, cats, districts)


def report(series: pd.DataFrame, cats: pd.DataFrame, districts: pd.DataFrame):
    pd.set_option("display.width", 160)
    print("\n== Series (B$ million)")
    print((series.set_index("year") / 1e6).round(2).to_string())
    print("\n== 2013 categories")
    print(cats.round(1).to_string(index=False))
    print("\n== 2013 districts")
    print(districts.round(1).to_string(index=False))


if __name__ == "__main__":
    main()
