"""Cleaning for case study 05 (agrifood processing, Ministry of Industry and Primary Resources).

Five related tables, in Malay. Names are standardised and translated here; the Malay names are
kept beside the English ones for a later Malay version of the site. See DATA_SOURCES.md
"Agrimakanan" known issues.
"""

from pathlib import Path

import pandas as pd

# Malay category (as published, any spelling) → (standard Malay name, English name)
CATEGORIES = {
    "biskut & bakeri": ("Biskut & Bakeri", "Biscuits & bakery"),
    "biskut dan bakeri": ("Biskut & Bakeri", "Biscuits & bakery"),
    "produk hasilan daging": ("Produk Hasilan Daging", "Meat products"),
    "air mineral & minuman ringan": ("Air Mineral & Minuman Ringan", "Mineral water & soft drinks"),
    "aiskrim": ("Aiskrim", "Ice cream"),
    "snek": ("Snek", "Snacks"),
    "makanan tradisi": ("Makanan Tradisi", "Traditional foods"),
    "produk hasilan ikan": ("Produk Hasilan Ikan", "Fish products"),
    "sos & perisa": ("Sos & Perisa", "Sauces & flavourings"),
    "rempah ratus": ("Rempah Ratus", "Spices"),
    "mi": ("Mi", "Noodles"),
    "mee": ("Mi", "Noodles"),
    "produk kacang soya": ("Produk Kacang Soya", "Soya bean products"),
    "produk hasilan kacang soya": ("Produk Kacang Soya", "Soya bean products"),
    "makanan segera": ("Makanan Segera", "Fast or instant food"),
    "acar & jeruk": ("Lain-lain", "Other"),  # inside "Lain-lain" in the district table
    "lain-lain": ("Lain-lain", "Other"),
}
NEW_IN_2013 = "Makanan Segera"  # DATA_SOURCES.md agrimakanan issue 1: a coverage change
DISTRICTS = {"brunei/muara": "Brunei-Muara", "brunei muara": "Brunei-Muara", "tutong": "Tutong",
             "belait": "Belait", "temburong": "Temburong"}  # fmt: skip
MIN_BUSINESSES = 5  # SOP 7: no published value may rest on fewer businesses than this


def _category(name: str) -> tuple[str, str]:
    key = " ".join(str(name).split()).lower()
    if key.startswith("lain-lain"):
        key = "lain-lain"
    if key not in CATEGORIES:
        raise ValueError(f"Unknown category: {name!r}. Add it to CATEGORIES.")
    return CATEGORIES[key]


def _with_names(df: pd.DataFrame, col: str) -> pd.DataFrame:
    names = df[col].map(_category)
    return df.assign(category_ms=names.str[0], category=names.str[1]).drop(columns=col)


def load_series(path: Path) -> pd.DataFrame:
    """Livestock- and crop-based market value by year → year, livestock_bnd, crop_bnd, total_bnd.

    Years with a missing ("n/a") value are dropped (2003), and the published change column is
    not used: it treats the missing value as zero.
    """
    df = pd.read_excel(path)
    df.columns = [c.strip() for c in df.columns]
    out = pd.DataFrame(
        {
            "year": df["Year"].astype(int),
            "livestock_bnd": pd.to_numeric(df["Proses Ternakan"], errors="coerce"),
            "crop_bnd": pd.to_numeric(df["Proses Tanaman"], errors="coerce"),
        }
    ).dropna()
    out["total_bnd"] = out.livestock_bnd + out.crop_bnd
    years = out.year.sort_values().tolist()
    if years != list(range(years[0], years[-1] + 1)):
        raise ValueError("Years are not consecutive after dropping missing values.")
    return out.sort_values("year").reset_index(drop=True)


def load_trend(path: Path) -> pd.DataFrame:
    """Category values 2010–2013 (B$ million) → year, category, category_ms, value_bnd."""
    df = pd.read_excel(path, header=None, skiprows=1, names=["year", "name", "value_m"])
    df = _with_names(df, "name")
    df["value_bnd"] = df.pop("value_m") * 1_000_000
    df = df.groupby(["year", "category_ms", "category"], as_index=False).value_bnd.sum()
    return df.astype({"year": int})


def load_categories_2013(path: Path, cross_tab: Path) -> pd.DataFrame:
    """2013 market value by category, with the number of businesses making each product.

    Business counts come from the category × district table (summed over districts), which
    counts a business once per category it makes. Raises if any category rests on fewer than
    MIN_BUSINESSES businesses, or if the two tables' values disagree.
    """
    value = pd.read_excel(path)
    value.columns = [c.strip() for c in value.columns]
    value = _with_names(value[["Category", "Market Value (B$)"]], "Category")
    value = value.groupby(["category_ms", "category"], as_index=False)["Market Value (B$)"].sum()

    xt = pd.read_excel(cross_tab)
    xt.columns = [c.strip() for c in xt.columns]
    xt = _with_names(xt[xt.District.str.strip() != "Jumlah"], "Category")
    counts = xt.groupby("category", as_index=False).agg(
        businesses=("No. of Entrepreneur", "sum"), value_check=("Market Value (B$)", "sum")
    )
    out = value.rename(columns={"Market Value (B$)": "value_bnd"}).merge(counts, on="category")
    if (abs(out.value_bnd - out.value_check) > 1).any():
        raise ValueError("Category values differ between the two 2013 tables.")
    if (out.businesses < MIN_BUSINESSES).any():
        raise ValueError("A category rests on fewer than 5 businesses; merge it before publishing.")
    out["share_pct"] = out.value_bnd / out.value_bnd.sum() * 100
    return out.drop(columns="value_check").sort_values("value_bnd", ascending=False)


def load_districts(path: Path) -> pd.DataFrame:
    """2013 district table → district, businesses, employees, value_bnd, shares."""
    df = pd.read_excel(path)
    df.columns = [c.strip() for c in df.columns]
    key = df["District"].str.strip().str.lower()
    if not set(key) <= set(DISTRICTS):
        raise ValueError(f"Unknown districts: {sorted(set(key) - set(DISTRICTS))}")
    out = pd.DataFrame(
        {
            "district": key.map(DISTRICTS),
            "businesses": df["No. of Entrepreneur"].astype(int),
            "employees": df["No. of Employees"].astype(int),
            "value_bnd": df["Market Value (B$)"].astype(float),
        }
    )
    if out.district.nunique() != 4:
        raise ValueError("Expected all four districts once.")
    if (out.businesses < MIN_BUSINESSES).any():
        raise ValueError("A district rests on fewer than 5 businesses.")
    for col in ("businesses", "employees", "value_bnd"):
        out[f"{col}_share_pct"] = out[col] / out[col].sum() * 100
    return out.sort_values("value_bnd", ascending=False).reset_index(drop=True)
