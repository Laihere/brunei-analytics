"""Cleaning for case study 09 (average retail prices of selected food and non-food items).

Both tables are long (Year, item, price), with group header rows mixed in among the items. In
some editions a header row holds the sum of its items' prices, which mixes units (per kg, per
tin, per tray) and has no meaning, so header rows become the `group` column and their values
are checked, then dropped. See DATA_SOURCES.md "Average retail price tables" known issues.
"""

from pathlib import Path

import pandas as pd

# Group header rows, as published (food headers carry a unit for their items)
FOOD_GROUPS = {
    "Rice and Cereals (Per Kilogramme)": ("Rice and cereals", "per kg"),
    "Fresh Meat and Poultry (Per Kilogramme)": ("Fresh meat and poultry", "per kg"),
    "Milk, Egg and Oil": ("Milk, eggs and fats", ""),
    "Fish and Prawns (Per Kilogramme)": ("Fish and prawns", "per kg"),
    "Vegetables and Fruits (Per Kilogramme)": ("Vegetables and fruits", "per kg"),
}
NONFOOD_GROUPS = {
    "Housing, Water, Electricity, Gas and Other Fuels": "Housing, water, electricity and gas",
    "Miscellaneous Goods and Services": "Passports",
}
# Items whose unit is in their own name; the label drops it, the unit column keeps it
UNIT_IN_NAME = {
    "Condensed Milk (388g Per Tin)": ("Condensed milk", "388 g tin"),
    "Evaporated Milk (400g Per Tin)": ("Evaporated milk", "400 g tin"),
    "Chicken Eggs (Per Tray)": ("Chicken eggs", "tray"),
    "Butter (340g Per Tin)": ("Butter", "340 g tin"),
    "Margerine (1 Kg Tin)": ("Margarine", "1 kg tin"),
    "Cement (10 Kilogramme Bag)": ("Cement", "10 kg bag"),
    "Water Supply (0 - 54.53 Unit)": ("Water, first 54.53 units", "per unit"),
    "Water Supply (54.54 Unit and Above)": ("Water, above 54.54 units", "per unit"),
    "Prepaid Electricity (1 - 600 KWh)": ("Electricity, 1–600 kWh", "per kWh"),
    "Prepaid Electricity (601 - 2,000 KWh)": ("Electricity, 601–2,000 kWh", "per kWh"),
    "Prepaid Electricity (2,001 - 4,000 KWh)": ("Electricity, 2,001–4,000 kWh", "per kWh"),
    "Prepaid Electricity (4,001 KWh and Above)": ("Electricity, 4,001 kWh and above", "per kWh"),
    "Piped Gas": ("Piped gas", "unit not stated"),
    "Cylinder Gas (LPG)": ("Cylinder gas (LPG)", "unit not stated"),
    "International Biometric Passport": ("International passport", "each"),
    "Borneo Biometric Passport": ("Borneo passport", "each"),
}
# Same item, different name in the 2010–2013 "Continued" edition
CONTINUED_NAMES = {"Sawi Putih": "Pak Choy"}
# Government-set prices and fees (tariff notes on the page); everything else is a market price
SET_PRICES = {
    "Water Supply (0 - 54.53 Unit)",
    "Water Supply (54.54 Unit and Above)",
    "Prepaid Electricity (1 - 600 KWh)",
    "Prepaid Electricity (601 - 2,000 KWh)",
    "Prepaid Electricity (2,001 - 4,000 KWh)",
    "Prepaid Electricity (4,001 KWh and Above)",
    "Piped Gas",
    "Cylinder Gas (LPG)",
    "International Biometric Passport",
    "Borneo Biometric Passport",
}


def _read(path: Path) -> pd.DataFrame:
    """year, name (trimmed, as published), value (number or NaN; "-" and blanks are NaN)."""
    df = pd.read_excel(path)
    if len(df.columns) != 3 or str(df.columns[0]).strip() != "Year":
        raise ValueError(f"{path.name}: expected three columns starting with 'Year'.")
    df.columns = ["year", "name", "value"]
    df = df.dropna(subset=["year", "name"]).astype({"year": int})
    df["name"] = df.name.astype(str).str.strip()
    df["value"] = pd.to_numeric(df.value.replace("-", pd.NA), errors="coerce")
    return df.reset_index(drop=True)


def _split_groups(df: pd.DataFrame, groups: dict, path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Items with their group, and the header rows (year, group, value) for checking."""
    is_header = df.name.isin(groups)
    df = df.assign(header=df.name.where(is_header))
    df["header"] = df.groupby("year").header.ffill()  # each item belongs to the header above it
    if df.header.isna().any():
        raise ValueError(f"{path.name}: items before the first group header.")
    return df[~is_header].copy(), df[is_header][["year", "header", "value"]]


def _label(name: str) -> tuple[str, str]:
    if name in UNIT_IN_NAME:
        return UNIT_IN_NAME[name]
    return name.replace("Margerine", "Margarine"), ""


FIRST_FOOD_HEADER = "Rice and Cereals (Per Kilogramme)"


def food_blocks(path: Path) -> pd.DataFrame:
    """The raw food table with a `block` number: each year's list starts with the rice and
    cereals header. The 2025 file lists 2013 twice (two blocks), see known issues."""
    df = _read(path)
    df["block"] = (df.name == FIRST_FOOD_HEADER).cumsum()
    return df


def duplicate_year_differences(path: Path) -> pd.DataFrame:
    """For a year published in two blocks: year, name, first, second where they differ."""
    df = food_blocks(path)
    rows = []
    for year, g in df.groupby("year"):
        blocks = [b.reset_index(drop=True) for _, b in g.groupby("block")]
        if len(blocks) == 1:
            continue
        if len(blocks) != 2 or not blocks[0].name.equals(blocks[1].name):
            raise ValueError(f"{path.name}: {year} repeats in an unexpected way.")
        a, b = blocks
        differ = ~((a.value - b.value).abs() < 1e-9) & ~(a.value.isna() & b.value.isna())
        rows += [
            {"year": year, "name": n, "first": x, "second": y}
            for n, x, y in zip(a.name[differ], a.value[differ], b.value[differ], strict=True)
        ]
    return pd.DataFrame(rows, columns=["year", "name", "first", "second"])


def load_food(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """year, group, item (as published), label, unit, price_bnd (NaN where "-"); plus the
    published group rows (year, group, published_total, items_sum) for the known-issues check.
    Where a year is listed twice, the second listing is kept: its one differing item price
    (salted anchovies, 2013) matches the 2010–2013 "Continued" edition."""
    df = food_blocks(path)
    keep = df.groupby("year").block.transform("max")
    df = df[df.block == keep].drop(columns="block").reset_index(drop=True)
    items, headers = _split_groups(df, FOOD_GROUPS, path)
    items["group"] = items.header.map(lambda h: FOOD_GROUPS[h][0])
    labels = items.name.map(_label)
    items["label"] = [lab for lab, _ in labels]
    items["unit"] = [u or FOOD_GROUPS[h][1] for (_, u), h in zip(labels, items.header, strict=True)]
    items = items.rename(columns={"name": "item", "value": "price_bnd"})
    sums = items.groupby(["year", "header"]).price_bnd.sum(min_count=1).rename("items_sum")
    check = headers.rename(columns={"value": "published_total"}).merge(
        sums.reset_index(), on=["year", "header"]
    )
    check["group"] = check.header.map(lambda h: FOOD_GROUPS[h][0])
    cols = ["year", "group", "item", "label", "unit", "price_bnd"]
    return items[cols].reset_index(drop=True), check[
        ["year", "group", "published_total", "items_sum"]
    ]


def load_food_continued(path: Path) -> pd.DataFrame:
    """year, label, price_bnd from the 2010–2013 "Continued" edition (fish, vegetables and
    fruits only), names matched to the main table's labels."""
    df = _read(path)
    df["label"] = (
        df.name.str.replace(r"\s*\(Per Kilogramme\)$", "", regex=True)
        .str.strip()
        .replace(CONTINUED_NAMES)
    )
    return df.rename(columns={"value": "price_bnd"})[["year", "label", "price_bnd"]]


def load_nonfood(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """year, group, item, label, unit, set_price (Government-set price or fee), price_bnd;
    plus the published group rows (empty in some editions, a sum of unlike prices in others)."""
    df = _read(path)
    items, headers = _split_groups(df, NONFOOD_GROUPS, path)
    unknown = set(items.name) - set(UNIT_IN_NAME)
    if unknown:
        raise ValueError(f"{path.name}: items not in the label list: {sorted(unknown)}")
    items["group"] = items.header.map(NONFOOD_GROUPS)
    items["label"] = items.name.map(lambda n: UNIT_IN_NAME[n][0])
    items["unit"] = items.name.map(lambda n: UNIT_IN_NAME[n][1])
    items["set_price"] = items.name.isin(SET_PRICES)
    items = items.rename(columns={"name": "item", "value": "price_bnd"})
    sums = items.groupby(["year", "header"]).price_bnd.sum(min_count=1).rename("items_sum")
    check = headers.rename(columns={"value": "published_total"}).merge(
        sums.reset_index(), on=["year", "header"]
    )
    check["group"] = check.header.map(NONFOOD_GROUPS)
    cols = ["year", "group", "item", "label", "unit", "set_price", "price_bnd"]
    return items[cols].reset_index(drop=True), check[
        ["year", "group", "published_total", "items_sum"]
    ]


def repeated_years(food: pd.DataFrame, years: list[int]) -> pd.Series:
    """Per item label: True when its price is exactly the same in every one of `years`."""
    wide = food[food.year.isin(years)].pivot(index="label", columns="year", values="price_bnd")
    return wide.nunique(axis=1).eq(1) & wide.notna().all(axis=1)
