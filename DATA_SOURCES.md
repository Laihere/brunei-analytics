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
| Road Casualties | data.gov.bn | Royal Brunei Police Force | Data.gov.bn Data Policy | 2025 (no year in title) | 2009–2017, annual | [link](https://www.data.gov.bn/road-casualties/) | `1-Road-Casualities.xlsx` (sha256 `ff7161aa…`) | 16 Oct 2026 | Reshaped to one row per year; ratios and 3-year averages computed | 03 Road casualties |
| Statistics of Road Traffic Accidents | data.gov.bn | Fire and Rescue Department Brunei Darussalam | Data.gov.bn Data Policy | 2025 (no year in title) | 2012–2021, annual | [link](https://www.data.gov.bn/statistics-of-road-traffic-accidents/) | `STATISTIC-OF-ROAD-TRAFFIC-ACCIDENTS-FROM-2012-TO-2021.xlsx` (sha256 `10d61f0d…`) + `Data-Definition-of-Road-Traffic-Accidents.xlsx` (`23e0d54a…`) | 16 Oct 2026 | Two call types summed per year. Cross-check only | 03 (cross-check) |
| Fire Occurances By Districts (owner listed: Brunei Darussalam Central Bank) | data.gov.bn | Brunei Darussalam Central Bank | Data.gov.bn Data Policy | 2025 (no year in title) | 2009–2020, annual | [link](https://www.data.gov.bn/fire-occurances-by-districts/) | `Fire-Occurances-By-Districts.xlsx` (sha256 `0fab54b8…`) | 16 Oct 2026 | Reshaped; yearly totals, district shares | 04 Fire occurrences |
| Fire Occurances By Districts (owner listed: Brunei Fire and Rescue Department) | data.gov.bn | Brunei Fire and Rescue Department | Data.gov.bn Data Policy | 2025 (no year in title) | 2009–2013, annual | [link](https://www.data.gov.bn/fire-occurances-by-districts-2/) | `4-Fire-Occurances-By-Districts.xlsx` (sha256 `c4dd8b52…`) | 16 Oct 2026 | None. Cross-check only | 04 (cross-check) |
| Statistic of Forest and Grass/Peat Fire | data.gov.bn | Fire and Rescue Department Brunei Darussalam | Data.gov.bn Data Policy | 2025 (no year in title) | 2012–2021, annual | [link](https://www.data.gov.bn/statistic-of-forest-and-grass-peat-fire/) | `STATISTIC-OF-FOREST-AND-GRASS-FIRE-FROM-2012-TO-2021.xlsx` (sha256 `47692985…`) | 16 Oct 2026 | Type labels trimmed; hectares summed per year | 04 Fire occurrences |

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

### Road Casualties (checked 16 Oct 2026)

Tidy long table (Year, Type, Amount), newest year first. Published 2025 but ends in 2017.

| # | Issue | Evidence | Status |
|---|---|---|---|
| 1 | Data ends in 2017 | Last year in the file; no later Royal Brunei Police Force table in the catalogue | Open: state the period on every title and card |
| 2 | One column mixes units | "Accidents" counts events; "Injuries" and "Deaths" count people | Reshape so each measure is its own column |
| 3 | Injuries fell 30% and deaths 40% from 2011 to 2012, accidents only 8%; both stay at the lower level after | 699 → 489 injuries; 47 → 28 deaths | Open: not explained (could be a real change or a change in recording). Report as a step and say the cause isn't known |
| 4 | Terms not defined | No definition of an injury (serious or slight) or a road death (e.g. within 30 days) | State in limitations |
| 5 | Deaths vary a lot from year to year | 17 (2016) to 47 (2011) | Compare 3-year averages, not single years |
| 6 | File name misspelt ("Casualities") | — | Cosmetic. Cite the dataset title, which is spelt correctly |

### Statistics of Road Traffic Accidents (checked 16 Oct 2026)

| # | Issue | Evidence | Status |
|---|---|---|---|
| 1 | Covers only accidents attended by Fire and Rescue | Data definition: "road traffics accidents attended by Fire and Rescue Department" | A subset, not comparable with police totals. Used only as a check: its deaths and injuries must not exceed the police figures |
| 2 | Header on the second row; year in merged cells | Year cell spans the two call-type rows | Forward-fill the year; sum the two call types |
| 3 | Small counts by call type (0–2) | "Car accident involving fire": 0–2 dead a year | Not published by call type; only yearly sums are used |

### Fire Occurances By Districts, two editions (checked 16 Oct 2026)

Both are tidy long tables (Year, District, Amount), newest year first. "Occurances" is spelt
this way in the published title.

| # | Issue | Evidence | Status |
|---|---|---|---|
| 1 | The longer edition (2009–2020) lists the Brunei Darussalam Central Bank as owner | The other edition, with identical 2009–2012 values, lists the Brunei Fire and Rescue Department | Credit the owner exactly as listed on each page (policy). Noted in the method. One of the EGNC email's questions covers owner names |
| 2 | 2013 differs between editions | Fire and Rescue edition: 265 fires (167, 57, 38, 3); Central Bank edition: 791 (350, 267, 168, 6). 2009–2012 are identical | Open: use the longer, later edition; show both 2013 totals in the cross-check. The shorter file may be a part-year or provisional count, but this isn't stated |
| 3 | 2010 is far above other years | 4,299 fires, against 1,274 (2009) and 651 (2011); high in all four districts | Keep: both editions agree, so not a typing error. Report as the peak without a cause |
| 4 | "Fire occurrence" isn't defined | No data definition file | Could include building, vehicle and vegetation fires. State in limitations |
| 5 | Data ends in 2020 | Published 2025 | State the period on titles and cards |

### Statistic of Forest and Grass/Peat Fire (checked 16 Oct 2026)

| # | Issue | Evidence | Status |
|---|---|---|---|
| 1 | Measures area burned (hectares), not the number of fires | Column "HECTRES" | Use only to compare the year pattern with fire counts, never added to them |
| 2 | "FOREST FIRE " has a trailing space; column header misspelt | — | Trim labels |
