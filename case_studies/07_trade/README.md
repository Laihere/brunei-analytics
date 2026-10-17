# 07 — Trade: imports, exports and the balance of trade, 2000–2021

**Question:** What did Brunei export and import from 2000 to 2021, and how did the balance of
trade change?

## Sources

| Dataset | Source | Owner | Licence | Accessed |
|---|---|---|---|---|
| Import, Export and Balance of Trade (main, 2000–2021) | data.gov.bn | Department of Statistics, JPES | Data.gov.bn Data Policy | 17 Oct 2026 |
| Total Export By Commodity Section (main, 2009–2021) | data.gov.bn | Department of Statistics, JPES | Data.gov.bn Data Policy | 17 Oct 2026 |
| Total Import by Commodity Section (main, 2000–2021) | data.gov.bn | Department of Statistics, JPES | Data.gov.bn Data Policy | 17 Oct 2026 |
| Classification Of Trade Commodities (section key) | data.gov.bn | Department of Economic Planning and Development | Data.gov.bn Data Policy | 17 Oct 2026 |
| Seven other editions of the same tables (cross-check) | data.gov.bn | JPES; Department of Economic Planning and Statistics; Department of Economic Planning and Development | Data.gov.bn Data Policy | 17 Oct 2026 |

Full attributions are generated from `outputs/*.meta.json`. Every file is listed in
[DATA_SOURCES.md](../../DATA_SOURCES.md).

## Method

1. `analysis/sources.py` downloads the 11 tables once each with `shared.fetch.download`; same-title
   editions are kept apart with `variant`.
2. `analysis/clean.py` reshapes the yearly totals to one column per measure, keys the commodity
   sections by SITC code (names differ between editions), and checks that every table adds up
   (exports = domestic + re-exports, total = exports + imports, balance = exports − imports,
   sections = totals), allowing for values rounded to 0.1 million.
3. `analysis/build.py` compares every other edition with the main one (no differences beyond
   rounding), computes each section's share of exports or imports, and writes the outputs and the
   local cleaned tables.

The full record (each step, why it was done, and the decision log) is in [PROCESS.md](PROCESS.md).

## Findings

- Brunei exported more than it imported in every year from 2000 to 2021. The surplus was largest
  in 2012 (B$11.8 bn) and smallest in 2020 (B$1.8 bn); imports grew 5.1-fold (charts 1–2).
- Mineral fuels were 96% of exports in 2009 and 78% in 2021; chemicals rose from 0.1% to 18%
  (chart 3).
- Machinery and transport was the largest import section in every year but one to 2018. From 2019
  mineral fuels were the largest, reaching 60% of imports in 2021 (chart 4).

## Limitations

- Values at current prices: changes can come from prices, quantities or both.
- Sections are broad; the tables don't show products, trading partners or services.
- The page shows what changed, not why.

---
Analysis by Muhd Lai Razi with AI assistance (Claude). Not an official publication of the Government of Brunei Darussalam.
