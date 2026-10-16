# Data Sources Log

One row per downloaded file, required by [DATA_USE_POLICY.md](DATA_USE_POLICY.md) (M1, M2, M4).
Raw files are not committed. They live locally at:

```
data/raw/<source>/<edition>/<dataset-slug>/<original filename>   (+ .meta.json)
```

- **Edition:** the year in the dataset title, or the year published if the title has none.
- **Coverage:** the period the data actually covers. This often differs from the edition.

Use `shared.fetch.download` (or `shared.fetch.adopt` for files downloaded by hand) so the
`.meta.json` record is written. Each record holds the page, owner, access date, coverage and checksum.

| Dataset title | Source | Data Source Owner | Licence | Edition | Coverage | Dataset page | File | Downloaded | Transformations | Used in |
|---|---|---|---|---|---|---|---|---|---|---|
| Consumer Price Index 2025 | data.gov.bn | Department of Statistics, JPES | Data.gov.bn Data Policy | 2025 | 2015–2025, annual | [link](https://www.data.gov.bn/consumer-price-index-2025/) | `Consumer-Price-Index-2025.xlsx` (sha256 `9adcdb8b…`) | 15 Oct 2026 (manual, matches official copy) | Repair 2022–2023 (known issues 1–2) | 01 Cost of living in 2025 |
| Percentage Change in Customer Price Index 2025 | data.gov.bn | Department of Statistics, JPES | Data.gov.bn Data Policy | 2025 | 2016–2025, annual | [link](https://www.data.gov.bn/percentage-change-in-customer-price-index-2025/) | `Percentage-Change-in-Consumer-Price-Index-2025.xlsx` (sha256 `20e2bc10…`) | 15 Oct 2026 | None. Used to verify and repair the CPI index | 01 Cost of living in 2025 |
| Average Retail Price of Subsidised Items and under Price Control 2025 | data.gov.bn | Department of Statistics, JPES | Data.gov.bn Data Policy | 2025 | 2015–2025, annual | [link](https://www.data.gov.bn/average-retail-price-of-subsidised-items-and-under-price-control-2025/) | `Average-Retail-Price-of-Subsidised-Items-and-under-Price-Control-2025.xlsx` (sha256 `44bcc2d5…`) | 15 Oct 2026 | Saloon car excluded; sugar 2024 flagged; Laila/Local rice kept separate | 01 Cost of living in 2025 |
| Consumer Price Index 2024 | data.gov.bn | Department of Economic Planning and Statistics | Data.gov.bn Data Policy | 2024 | 2015–2024, annual | [link](https://www.data.gov.bn/consumer-price-index-2024/) | `Consumer-Price-Index-2024.xlsx` (sha256 `cc04ffd6…`) | 15 Oct 2026 | None. Cross-check only | 01 (cross-check) |
| Inflation, consumer prices (annual %), Brunei (FP.CPI.TOTL.ZG) | World Bank WDI, original source IMF International Financial Statistics | — | CC BY 4.0 (per indicator metadata) | 2026 (pulled) | 2010–2025 | [link](https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG?locations=BN) | `FP_CPI_TOTL_ZG.csv` | 15 Oct 2026 | None. Cross-check only | 01 (cross-check) |
| Consumer price index, Brunei (FP.CPI.TOTL) | World Bank WDI, original source IMF International Financial Statistics | — | CC BY 4.0 (per indicator metadata) | 2026 (pulled) | 2010–2025 | [link](https://data.worldbank.org/indicator/FP.CPI.TOTL?locations=BN) | `FP_CPI_TOTL.csv` | 15 Oct 2026 | None. Cross-check only | 01 (cross-check) |
| Crime Statistics (2012 file) | data.gov.bn | Royal Brunei Police Force | Data.gov.bn Data Policy | 2012 | 2012, annual | [link](https://www.data.gov.bn/crime-statistics-2/) | `2-Crime-Statistics-2012.xlsx` (sha256 `16391d55…`) | 16 Oct 2026 | Read by label; "-" as missing; Acts with < 5 cases merged into "Other Acts" | 02 Crime statistics, 2012–2013 |
| Crime Statistics (2013 file) | data.gov.bn | Royal Brunei Police Force | Data.gov.bn Data Policy | 2013 | 2013, annual | [link](https://www.data.gov.bn/crime-statistics/) | `3-Crime-Statistics-2013.xlsx` (sha256 `9aa72ec8…`) | 16 Oct 2026 | Read by label; "-" as missing; Acts with < 5 cases merged into "Other Acts" | 02 Crime statistics, 2012–2013 |

## Known issues in source data

Recorded as found, before any correction. Corrections must be cross-checked against another
official source and described in the case study's method and caveats (policy M2, M5).

### Consumer Price Index 2025 (checked 15 Oct 2026)

Cross-checked against the publisher's own "Percentage Change in Customer Price Index 2025" and
World Bank CPI (FP.CPI.TOTL). The same errors appear in the 2024 edition (DEPS), so they carry
over between editions.

| # | Issue | Evidence | Status |
|---|---|---|---|
| 1 | 2023 values sit one row too low from Food onwards: each category holds the next one's value; the true Miscellaneous value is missing | Rebuilding 2023 as 2022 × (1 + published % change) reproduces the shifted values to 2 decimals (e.g. true Food 115.31 is published under Clothing). The 2023 "Overall" (106.81) is correct: World Bank 106.71, published change +0.357%. | **Resolved:** repair 2023 categories from 2022 × (1 + % change). Disclose in method and caveats |
| 2 | 2022 "Overall CPI" = 126.39 | Equals the true 2023 Miscellaneous value (126.003 × 1.00306 = 126.39), so the shift wrapped around. True value 102.7 × 1.03682 = 106.48 (World Bank 106.33) | **Resolved:** replace with 106.48. Disclose |
| 3 | Third column headed "Weight" holds index values | Values around 100, not shares | Rename to `index` when cleaning |
| 4 | Base year not stated | 2015 overall = 99.9, not 100.0. The World Bank labels its index 2010 = 100, but values sit near 100 around 2019–2020 | Open: World Bank 2015 = 100.01 suggests 2015 = 100, despite its "2010 = 100" label. Until confirmed, report changes (%) and rebase to 2019 = 100 for charts |
| 5 | Miscellaneous 2017 = 87.6 (−12.5%), then +13.6% in 2018 | Both files agree, so it's not a typo between files | Keep, flag in caveats if Miscellaneous is shown |
| 6 | Mixed precision by year; "Health " has a trailing space | 2025/2023/2022/2019 unrounded, other years 1 decimal | Strip whitespace; round to 1 decimal for display |

After repairs, every year's implied change matches the published % change within 0.1 points
(2018 Miscellaneous: 0.2, rounding).

### Average Retail Price of Subsidised Items and under Price Control 2025 (checked 15 Oct 2026)

| # | Issue | Evidence | Status |
|---|---|---|---|
| 1 | Sugar 2024 = BND 1.73/kg | 1.30 in 2022, 2023 and 2025. A one-year +33% jump and reversal for a price-controlled item is implausible | Open: flag, don't headline it unless confirmed elsewhere |
| 2 | "Laila Rice" (2015–2019) replaced by "Local Rice" (2020–2025) | Different item names, no overlap year | Treat as a series break. Don't join the two without confirmation |
| 3 | "Saloon Car (1,500cc)" listed 2015–2019 only | Dropped from 2020 | Exclude (not a household staple, and no recent data) |
| 4 | Header cell has leading spaces; prices in BND | — | Strip whitespace when cleaning |

### Crime Statistics, 2012 and 2013 files (checked 16 Oct 2026)

Both portal pages are titled "Crime Statistics"; the files are yearbook tables 14.2 (2012) and
14.3 (2013), bilingual Malay/English. Totals are Excel formulas; the stored values match the sum
of the rows in both years.

| # | Issue | Evidence | Status |
|---|---|---|---|
| 1 | Only two single-year files on the portal | No other Royal Brunei Police Force crime table in the catalogue | Open: limits the study to 2012–2013 |
| 2 | "-" used for some cells | e.g. Labour Act: 87 cases, solved "-", arrests "-". Could mean nil or not recorded | Treat as missing, not zero. The published totals count it as zero, so "solved %" for other agencies is a lower bound |
| 3 | The list of Acts in "Cases handled by other agencies" differs by year | 2012 has Telecommunication and Halal Meat Acts; 2013 has Electricity, Agricultural, and Religious Council & Kadis Courts Acts | Compare the totals and the Acts present in both years only |
| 4 | Same Act named differently | "Akta KDN" (2012) vs "Akta Keselamatan Dalam Negeri" (2013), both "Internal Security Act" | Match on the English name |
| 5 | Very small counts (1–3 cases or arrests) for several Acts | e.g. Internal Security Act 2013: 1 case, 1 arrest | SOP 7: merge Acts with fewer than 5 cases into "Other Acts" |
| 6 | Arrests can exceed cases | e.g. Various Acts 2012: 136 cases, 283 persons arrested | Not an error: arrests count persons. Don't compute arrests ÷ cases as a rate |
