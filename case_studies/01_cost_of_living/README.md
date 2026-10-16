# 01 — Cost of living in 2025: prices and subsidised items

**Question:** How did prices in Brunei change in 2025, and how far have they moved since before the pandemic (2019)?

## Sources

| Dataset | Source | Owner | Licence | Accessed |
|---|---|---|---|---|
| Consumer Price Index 2025 | data.gov.bn | Department of Statistics, JPES | Data.gov.bn Data Policy | 15 Oct 2026 |
| Percentage Change in Customer Price Index 2025 | data.gov.bn | Department of Statistics, JPES | Data.gov.bn Data Policy | 15 Oct 2026 |
| Average Retail Price of Subsidised Items and under Price Control 2025 | data.gov.bn | Department of Statistics, JPES | Data.gov.bn Data Policy | 15 Oct 2026 |
| Consumer price index / Inflation (FP.CPI.TOTL, FP.CPI.TOTL.ZG) | World Bank WDI (original source: IMF IFS) | — | CC BY 4.0 | 15 Oct 2026 |

Full attributions are generated from `outputs/*.meta.json`.

## Method

1. Files downloaded with `shared.fetch` into `data/raw/` (see DATA_SOURCES.md).
2. `analysis/clean.py`:
   - The CPI file's 2023 rows are shifted one category down, and its 2022 overall value is wrong.
     Both are rebuilt as previous year × (1 + the publisher's own % change) and flagged `repaired`.
     The build fails if any year still disagrees with the published changes by more than 0.25 pts.
   - Subsidised items: saloon car excluded, sugar 2024 flagged, Laila and Local rice kept separate.
3. `analysis/figures.py`: the five charts, each returning its data table.
4. `analysis/build.py`: rebases CPI to 2019 = 100, summarises 2025, validates schemas, and checks
   overall CPI against the World Bank series. Writes the CSVs in `outputs/`.

Run: `uv run python case_studies/01_cost_of_living/analysis/build.py`

The full record (each step, why it was done, and the decision log) is in [PROCESS.md](PROCESS.md).

## Findings

Published as *"Brunei's prices stopped rising by 2025, but stayed 7% above 2019"*
(`dashboard/case-studies/01-cost-of-living.qmd`). Numbers in the text are computed from `outputs/`.

- Yearly price change: 2016–2019 average −0.2%, 2020–2022 +2.4% (peak +3.7% in 2022), 2023–2025 −0.1%.
- 2025 vs 2019: all items +7.2%, food & drink +13.7%, miscellaneous +26.8%; communication −5.8%.
- Subsidised items 2025 vs 2019: vegetable oil +39%, palm oil +27%, infant formula +14%; rice +1% to +3%.
- Stabilised: 2023–2025 overall changes within −0.4% to +0.4%; food's first yearly decrease since 2019 was in 2025.

Scope: when and what changed, not why. Periods are labelled by time ("pandemic years and after"),
not as causes.

## Limitations

- Repaired values (2022 overall, 2023 categories) are rebuilt from the publisher's own % changes, not published directly.
- Base year not stated in the source; results are shown as % changes or rebased to 2019 = 100.
- National annual averages: they say nothing about districts, households or months.
- Miscellaneous goods and services fell 12.5% in 2017 and rose 13.6% in 2018; both source tables agree, but the cause isn't stated.

---
Analysis by Muhd Lai Razi with AI assistance (Claude). Not an official publication of the Government of Brunei Darussalam.
