# 09 — Retail prices of selected food and non-food items, item by item

**Question:** How did the average retail prices of selected food items (2013–2018) and
non-food items (2015–2025) change, item by item?

## Sources

| Dataset | Source | Owner | Licence | Accessed |
|---|---|---|---|---|
| Average Retail Price Of Selected Food Items (2010–2018) | data.gov.bn | Department of Economic Planning and Statistics | Data.gov.bn Data Policy | 19 Oct 2026 |
| Average Retail Price Of Selected Food Items (Continued) (2010–2013, cross-check only) | data.gov.bn | Department of Economic Planning and Development | Data.gov.bn Data Policy | 19 Oct 2026 |
| Average Retail Price of Selected Non-Food Items 2025 (2015–2025) | data.gov.bn | Department of Statistics, JPES | Data.gov.bn Data Policy | 19 Oct 2026 |
| Average Retail Price of Selected Non-Food Items (2015–2021 and 2015–2018 editions, cross-checks only) | data.gov.bn | Department of Statistics, JPES; Department of Economic Planning and Statistics | Data.gov.bn Data Policy | 19 Oct 2026 |

Full attributions are generated from `outputs/*.meta.json`. The subsidised and price-controlled
items are case study 01's table and are only linked, not reused.

## Method

1. `analysis/sources.py`: five tables downloaded with `shared.fetch.download`.
2. `analysis/clean.py`: group header rows split from items (each holds the sum of its items'
   prices in unlike units, checked then dropped); "-" kept as missing; 2013, listed twice in
   the food file, taken from its second listing; Government-set prices marked.
3. `analysis/build.py`: change per item, 2013→2018 (food) and 2015→2025 (non-food); food index
   with 2013 = 100; other editions compared value by value.

The full record (each step, why it was done, and the decision log) is in [PROCESS.md](PROCESS.md).

## Findings

Published as *"13 of 24 everyday food items cost more in 2018 than in 2013, while 10 of 11
Government-set prices were unchanged from 2015 to 2025"*
(`dashboard/case-studies/09-retail-prices.qmd`).

- Food, 2013→2018: 13 items rose, 9 fell, 2 changed by under 0.5%. Largest rise shallots
  (+28.1%), largest fall chicken eggs (−18.0%) (chart 1, hierarchy tree).
- Every fish and prawn item rose or stayed level; four of five milk, egg and fat items fell.
- Garlic (index 80 to 132) and shallots swung the most from year to year (chart 2, ranges).
- Non-food, 2015→2025: all 10 Government-set prices unchanged; cement −2.8% (chart 3).

## Limitations

- 18 of 24 food items repeat the same price in 2010–2012, so food starts in 2013.
- The tables don't say how the averages were made (shops, brands, months).
- Single items, not a weighted basket; see case study 01 for the CPI.
- Food ends in 2018. The page shows what changed, not why.

---
Analysis by Muhd Lai Razi Muhd Silmi with AI assistance (Claude). Not an official publication of the Government of Brunei Darussalam.
