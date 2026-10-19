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
| BROILER INDUSTRY YEAR 1992-2020 | data.gov.bn | Agriculture and Agrifood Department | Data.gov.bn Data Policy | 2020 | 1992–2020, annual | [link](https://www.data.gov.bn/broiler-industry-year-1992-2020/) | `Broiler-Industry-1992-2020.xlsx` (sha256 `4d30764f…`) | 16 Oct 2026 | Local share of supply computed | 06 Livestock supply |
| Egg Industry, Year 1992-2020 | data.gov.bn | Agriculture and Agrifood Department | Data.gov.bn Data Policy | 2020 | 1992–2020, annual | [link](https://www.data.gov.bn/egg-industry-year-1992-2020/) | `Egg-Industry-1992-2020.xlsx` (sha256 `6ca22e6e…`) | 16 Oct 2026 | "Monthly" header read as yearly; local share computed | 06 Livestock supply |
| Beef Industry, Year 1995-2020 | data.gov.bn | Agriculture and Agrifood Department | Data.gov.bn Data Policy | 2020 | 1995–2020, annual | [link](https://www.data.gov.bn/beef-industry-year-1995-2020/) | `Beef-Industry-1995-2020.xlsx` (sha256 `12061a55…`) | 16 Oct 2026 | 1995–1999 dropped (imports n/a); two import types summed | 06 Livestock supply |
| Day Old Chick Industry Year 2001-2020 | data.gov.bn | Agriculture and Agrifood Department | Data.gov.bn Data Policy | 2020 | 2001–2020, annual | [link](https://www.data.gov.bn/day-old-chick-industry-year-2001-2020/) | `Day-Old-Chick-Industry-2001-2020.xlsx` (sha256 `98223af7…`) | 16 Oct 2026 | Local share computed | 06 Livestock supply |
| Fertilized Eggs Industry , Year 2011-2020 | data.gov.bn | Agriculture and Agrifood Department | Data.gov.bn Data Policy | 2020 | 2001–2020, annual (title says 2011) | [link](https://www.data.gov.bn/fertilized-eggs-industry-year-2011-2020/) | `Fertilized-Eggs-Industry-2001-2020.xlsx` (sha256 `432bb181…`) | 16 Oct 2026 | Local share computed | 06 Livestock supply |
| Number Of Slaughtered Broilers, 2011-2020 | data.gov.bn | Agriculture and Agrifood Department | Data.gov.bn Data Policy | 2020 | 2011–2020, monthly | [link](https://www.data.gov.bn/number-of-slaughtered-broilers-2011-2020/) | `Number-of-Slaughtered-Broilers-2011-2020.xlsx` (sha256 `d3156183…`) | 16 Oct 2026 | Yearly totals; cross-check only | 06 (cross-check) |
| Broiler Industry, 1992-2015 | data.gov.bn | Department of Agriculture and Agrifood, Ministry of Primary Resources and Tourism | Data.gov.bn Data Policy | 2015 | 1992–2015, annual | [link](https://www.data.gov.bn/broiler-industry-1992-2015/) | `Broiler-Industry-1992-2015.xlsx` (sha256 `caebd0e2…`) | 16 Oct 2026 | None. Cross-check only | 06 (cross-check) |
| Egg Industry, 1992-2015 | data.gov.bn | Department of Agriculture and Agrifood, Ministry of Primary Resources and Tourism | Data.gov.bn Data Policy | 2015 | 1992–2015, annual | [link](https://www.data.gov.bn/egg-industry-1992-2015/) | `Egg-Industry-1992-2015.xlsx` (sha256 `6d8b68c7…`) | 16 Oct 2026 | None. Cross-check only | 06 (cross-check) |
| Beef Industry, 1995-2015 | data.gov.bn | Department of Agriculture and Agrifood, Ministry of Primary Resources and Tourism | Data.gov.bn Data Policy | 2015 | 1995–2015, annual | [link](https://www.data.gov.bn/beef-industry-1995-2015/) | `Beef-Industry-1995-2015.xlsx` (sha256 `a27e1f27…`) | 16 Oct 2026 | None. Cross-check only | 06 (cross-check) |
| Day Old Chick Industry, 2001-2015 | data.gov.bn | Department of Agriculture and Agrifood, Ministry of Primary Resources and Tourism | Data.gov.bn Data Policy | 2015 | 2001–2015, annual | [link](https://www.data.gov.bn/day-old-chick-industry-2001-2015/) | `Day-Old-Chick-Industry-2001-2015.xlsx` (sha256 `c1d4bd34…`) | 16 Oct 2026 | None. Cross-check only | 06 (cross-check) |
| Fertilized Eggs Industry, 2011-2015 | data.gov.bn | Department of Agriculture and Agrifood, Ministry of Primary Resources and Tourism | Data.gov.bn Data Policy | 2015 | 2001–2015, annual | [link](https://www.data.gov.bn/fertilized-eggs-industry-2011-2015/) | `Fertilized-Eggs-Industry-2001-2015.xlsx` (sha256 `eb86c850…`) | 16 Oct 2026 | None. Cross-check only | 06 (cross-check) |
| Status Pengeluaran Produck Agrimakanan [Status of agrifood product production] | data.gov.bn | Ministry of Industry and Primary Resources | Data.gov.bn Data Policy | 2025 (file names say 2013 or 2003–2012) | 2003–2013, annual | [link](https://www.data.gov.bn/status-pengeluaran-produck-agrimakanan/) | `STATUS-PENGELUARAN-PRODUK-AGRIMAKANAN-2003-2012.xlsx` (sha256 `1d8c394f…`) | 16 Oct 2026 | Totals recomputed; 2003 dropped (crop value n/a); published change column not used | 05 Agrifood processing |
| Statistik Industri Agrimakanan [Agrifood industry statistics] | data.gov.bn | Ministry of Industry and Primary Resources | Data.gov.bn Data Policy | 2025 (file names say 2013 or 2003–2012) | 2013 | [link](https://www.data.gov.bn/statistik-industri-agrimakanan/) | `STATISTIK-INDUSTRI-AGRIMAKANAN-2013.xlsx` (sha256 `41996ad2…`) | 16 Oct 2026 | Category names trimmed and translated; pickles merged into Other | 05 Agrifood processing |
| Tren Pengeluaran Agrimakanan Mengikut Kategori Produk [Agrifood production trends by product category] | data.gov.bn | Ministry of Industry and Primary Resources | Data.gov.bn Data Policy | 2025 (file names say 2013 or 2003–2012) | 2010–2013, annual | [link](https://www.data.gov.bn/tren-pengeluaran-agrimakanan-mengikut-kategori-produk/) | `TREN-PENGELUARAN-AGRIMAKANAN-MENGIKUT-KATEGORI-PRODUK-2010-2013.xlsx` (sha256 `07f5f9fd…`) | 16 Oct 2026 | Category names translated; B$ million | 05 Agrifood processing |
| Status Pengeluaran Agrimakanan Mengikut Daerah [Status of agrifood production by district] | data.gov.bn | Ministry of Industry and Primary Resources | Data.gov.bn Data Policy | 2025 (file names say 2013 or 2003–2012) | 2013 | [link](https://www.data.gov.bn/status-pengeluaran-agrimakanan-mengikut-daerah/) | `STATUS-PENGELUARAN-AGRIMAKANAN-MENGIKUT-DAERAH-2013.xlsx` (sha256 `d3092853…`) | 16 Oct 2026 | District names standardised; shares computed | 05 Agrifood processing |
| Statistik Industri Agrimakanan Mengikut Daerah Dan Kategori Produck [Agrifood industry statistics by district and product category] | data.gov.bn | Ministry of Industry and Primary Resources | Data.gov.bn Data Policy | 2025 (file names say 2013 or 2003–2012) | 2013 | [link](https://www.data.gov.bn/statistik-industri-agrimakanan-mengikut-daerah-dan-kategori-produck/) | `STATISTIK-INDUSTRI-AGRIMAKANAN-MENGIKUT-DAERAH-DAN-KATEGORI-PRODUK-2013.xlsx` (sha256 `68e895b1…`) | 16 Oct 2026 | Not published (small cells). Cross-check only; category entrepreneur counts used | 05 (cross-check) |
| Import, Export and Balance of Trade (owner listed: Department of Statistics, JPES) | data.gov.bn | Department of Statistics, JPES | Data.gov.bn Data Policy | 2025 (no year in title) | 2000–2020, annual | [link](https://www.data.gov.bn/import-export-and-balance-of-trade/) | `Import-Export-and-Balance-of-Trade.xlsx` (sha256 `19fa6746…`) | 17 Oct 2026 | Main series (yearly totals); reshaped | 07 Trade |
| Import, Export and Balance of Trade (owner listed: JPES) | data.gov.bn | JPES | Data.gov.bn Data Policy | 2025 (no year in title) | 2000–2020, annual | [link](https://www.data.gov.bn/import-export-and-balance-of-trade-2/) | `Import-Export-and-Balance-of-Trade.xlsx` (sha256 `e072e122…`) | 17 Oct 2026 | Cross-check only (no differences beyond rounding) | 07 Trade |
| Import, Export And Balance Of Trade (owner listed: Department of Economic Planning and Statistics) | data.gov.bn | Department of Economic Planning and Statistics | Data.gov.bn Data Policy | 2025 (no year in title) | 2000–2018, annual | [link](https://www.data.gov.bn/import-export-and-balance-of-trade-3/) | `Import-Export-and-Balance-of-Trade-1.xlsx` (sha256 `be16af6e…`) | 17 Oct 2026 | Cross-check only (no differences beyond rounding) | 07 Trade |
| Inport, Export And Balance Of Trade (owner listed: Department of Economic Planning and Development) | data.gov.bn | Department of Economic Planning and Development | Data.gov.bn Data Policy | 2025 (no year in title) | 2009–2013, annual | [link](https://www.data.gov.bn/inport-export-and-balance-of-trade/) | `2-Inport-Export-And-Balance-Of-Trade.xlsx` (sha256 `fd1d66ac…`) | 17 Oct 2026 | Cross-check only (no differences beyond rounding) | 07 Trade |
| Total Export By Commodity Section (owner listed: Department of Statistics, JPES) | data.gov.bn | Department of Statistics, JPES | Data.gov.bn Data Policy | 2025 (no year in title) | 2009–2021, annual | [link](https://www.data.gov.bn/total-export-by-commodity-section/) | `Total-Export-By-Commodity-Section.xls.xlsx` (sha256 `6161c764…`) | 17 Oct 2026 | Main series (exports by section); sections keyed by SITC code, shares computed | 07 Trade |
| Total Export By Commodity Section (owner listed: JPES) | data.gov.bn | JPES | Data.gov.bn Data Policy | 2025 (no year in title) | 2009–2020, annual | [link](https://www.data.gov.bn/total-export-by-commodity-section-2/) | `Total-Export-By-Commodity-Section.xls.xlsx` (sha256 `5bb85a0c…`) | 17 Oct 2026 | Cross-check only (no differences beyond rounding) | 07 Trade |
| Total Export By Commodity Section (owner listed: Department of Economic Planning and Statistics) | data.gov.bn | Department of Economic Planning and Statistics | Data.gov.bn Data Policy | 2025 (no year in title) | 2009–2018, annual | [link](https://www.data.gov.bn/total-export-by-commodity-section-3/) | `Total-Export-by-Commodity-Section.xlsx` (sha256 `cc7dd83c…`) | 17 Oct 2026 | Cross-check only (no differences beyond rounding) | 07 Trade |
| Total Import by Commodity Section (owner listed: Department of Statistics, JPES) | data.gov.bn | Department of Statistics, JPES | Data.gov.bn Data Policy | 2025 (no year in title) | 2000–2021, annual | [link](https://www.data.gov.bn/total-import-by-commodity-section/) | `Total-Import-by-Commodity-Section.xlsx` (sha256 `db357472…`) | 17 Oct 2026 | Main series (imports by section); 'Total Import' rows checked then dropped; shares computed | 07 Trade |
| Total Import by Commodity Section (owner listed: JPES) | data.gov.bn | JPES | Data.gov.bn Data Policy | 2025 (no year in title) | 2000–2020, annual | [link](https://www.data.gov.bn/total-import-by-commodity-section-2/) | `Total-Import-by-Commodity-Section.xlsx` (sha256 `7fe2af71…`) | 17 Oct 2026 | Cross-check only (no differences beyond rounding) | 07 Trade |
| Total Import By Commodity Section (owner listed: Department of Economic Planning and Statistics) | data.gov.bn | Department of Economic Planning and Statistics | Data.gov.bn Data Policy | 2025 (no year in title) | 2000–2018, annual | [link](https://www.data.gov.bn/total-import-by-commodity-section-3/) | `Total-Import-by-Commodity-Section-1.xlsx` (sha256 `5e73be4d…`) | 17 Oct 2026 | Cross-check only (no differences beyond rounding) | 07 Trade |
| Classification Of Trade Commodities | data.gov.bn | Department of Economic Planning and Development | Data.gov.bn Data Policy | 2025 (no year in title) | 2009–2013 | [link](https://www.data.gov.bn/classification-of-trade-commodities/) | `1-Classification-Of-Trade-Commodities.xlsx` (sha256 `bcea3a71…`) | 17 Oct 2026 | Section key: codes, English and Malay names | 07 Trade |
| MUARA CONVENTIONAL TERMINAL, MUARA PORT 2004-2015 | data.gov.bn | Berthing Section and Statistic Unit, Ports Department | Data.gov.bn Data Policy | 2015 | 2004–2015, annual | [link](https://www.data.gov.bn/muara-conventional-terminal-muara-port-2004-2015/) | `1.-MUARA-CONVENTIONAL-TERMINAL_MUARA-PORT-2004-2015.xlsx` (sha256 `d57b9760…`) | 17 Oct 2026 | Main series: uncontainerised cargo by year | 08 Muara Port |
| MUARA CONVENTIONAL TERMINAL, MUARA PORT 2004-2015 | data.gov.bn | Berthing Section and Statistic Unit, Ports Department | Data.gov.bn Data Policy | 2015 | 2004–2015, annual | [link](https://www.data.gov.bn/muara-conventional-terminal-muara-port-2004-2015/) | `1.1-DATA-DEFINITION-MUARA-CONVENTIONAL-TERMINAL_MUARA-PORT-2004-2015.xlsx` (sha256 `14bbb309…`) | 17 Oct 2026 | Definition of uncontainerized cargo | 08 Muara Port |
| MUARA CONTAINER TERMINAL, MUARA PORT 2004-2015 | data.gov.bn | Berthing Section and Statistic Unit, Ports Department | Data.gov.bn Data Policy | 2015 | 2004–2015, annual | [link](https://www.data.gov.bn/muara-container-terminal-muara-port-2004-2015/) | `2.-MUARA-CONTAINER-TERMINAL_MUARA-PORT-2004-2015.xlsx` (sha256 `a8b286ab…`) | 17 Oct 2026 | Main series: containers by year | 08 Muara Port |
| MUARA CONTAINER TERMINAL, MUARA PORT 2004-2015 | data.gov.bn | Berthing Section and Statistic Unit, Ports Department | Data.gov.bn Data Policy | 2015 | 2004–2015, annual | [link](https://www.data.gov.bn/muara-container-terminal-muara-port-2004-2015/) | `2.1-DATA-DEFINITION-MUARA-CONTAINER-TERMINAL_MUARA-PORT-2004-2015.xlsx` (sha256 `184ff1df…`) | 17 Oct 2026 | Definition of TEU, local, transhipment and total | 08 Muara Port |
| VESSEL CALLING (2004-2015) | data.gov.bn | Berthing Section and Statistic Unit, Ports Department | Data.gov.bn Data Policy | 2015 | 2004–2015, annual | [link](https://www.data.gov.bn/vessel-calling-2004-2015/) | `3.-VESSEL-CALL_MUARA-PORT-2004-2015.xlsx` (sha256 `e40ff981…`) | 17 Oct 2026 | Inspected, not used (see known issues) | 08 Muara Port |
| VESSEL CALLING (2004-2015) | data.gov.bn | Berthing Section and Statistic Unit, Ports Department | Data.gov.bn Data Policy | 2015 | 2004–2015, annual | [link](https://www.data.gov.bn/vessel-calling-2004-2015/) | `3.1-DATA-DEFINITION-VESSEL-CALL_MUARA-PORT-2004-2015.xlsx` (sha256 `fe688381…`) | 17 Oct 2026 | Read for the definition of vessel calling | 08 Muara Port |
| IMPORT VESSELS (2004 – 2015) | data.gov.bn | Berthing Section and Statistic Unit, Ports Department | Data.gov.bn Data Policy | 2015 | 2004–2015, annual | [link](https://www.data.gov.bn/import-vessels-2004-2015/) | `4.-IMPORT-VESSELS-2004-2015.xlsx` (sha256 `ae667278…`) | 17 Oct 2026 | Inspected, not used (see known issues) | 08 Muara Port |
| IMPORT VESSELS (2004 – 2015) | data.gov.bn | Berthing Section and Statistic Unit, Ports Department | Data.gov.bn Data Policy | 2015 | 2004–2015, annual | [link](https://www.data.gov.bn/import-vessels-2004-2015/) | `4.1-DATA-DEFINITION-IMPORT-VESSEL.xlsx` (sha256 `e41540ef…`) | 17 Oct 2026 | Read for the definitions of vessel types | 08 Muara Port |
| EXPORT VESSELS (2004-2015) | data.gov.bn | Berthing Section and Statistic Unit, Ports Department | Data.gov.bn Data Policy | 2015 | 2004–2015, annual | [link](https://www.data.gov.bn/export-vessels-2004-2015/) | `5.-EXPORT-VESSELS-2004-2015.xlsx` (sha256 `77c173d3…`) | 17 Oct 2026 | Inspected, not used (see known issues) | 08 Muara Port |
| EXPORT VESSELS (2004-2015) | data.gov.bn | Berthing Section and Statistic Unit, Ports Department | Data.gov.bn Data Policy | 2015 | 2004–2015, annual | [link](https://www.data.gov.bn/export-vessels-2004-2015/) | `5.1-DATA-DEFINITION-EXPORT-VESSEL.xlsx` (sha256 `502496e7…`) | 17 Oct 2026 | Read for the definitions of vessel types | 08 Muara Port |
| Brunei Darussalam ADM1 (districts) boundaries, simplified | geoBoundaries (William & Mary geoLab), gbOpen release 9469f09; original data from Wikimedia Commons (user Tachymetre) | — | CC BY 4.0 (site licence; file metadata says public domain) | 2023 | 4 districts | [link](https://www.geoboundaries.org/countryDownloads.html) | `geoBoundaries-BRN-ADM1_simplified.geojson` (sha256 `6ec08eaa…`) | 19 Oct 2026 | Approximate boundaries, not an official survey; projected to SVG paths in `case_studies/_shared/outputs/brunei_districts.csv` | 05 (chart 5, district maps) |

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

### Agrimakanan (agrifood processing) tables, Ministry of Industry and Primary Resources (checked 16 Oct 2026)

Five related tables about **food processing** (manufactured food products), not farming.
Market values agree across all five to the dollar (2013 total B$86,236,376; 2010–2012 totals
match between the time series and the category table).

| # | Issue | Evidence | Status |
|---|---|---|---|
| 1 | "Makanan Segera" (fast or instant food) appears in 2013 only | B$34.5m in 2013, 0 in 2010–2012; 40% of 2013's total | Treat as a coverage change, not growth: show it separately and compare years without it. Without it, 2013 = B$51.7m vs B$62.8m in 2012 |
| 2 | Head-counts differ between tables | Category × district table sums to 548 entrepreneurs and 3,495 employees; district table: 225 and 1,739. Market values match exactly | Likely one business counted in each category it makes (not stated). Use the district table for head-counts; category counts only as "businesses making this product" |
| 3 | 2003 crop-based value is "n/a" | The published 2004 change (+B$16.5m) treats it as zero | Start the series in 2004; recompute changes, don't use the published column |
| 4 | Small cells in the category × district table | 17 of 52 cells have 1–4 entrepreneurs; a market value there can reveal one business's sales | SOP 7: publish category totals and district totals only, never the cross-tab |
| 5 | Implausible cells | Makanan Segera: 11 entrepreneurs, 0 employees, B$34.5m; Mi (noodles) in Temburong: 1 entrepreneur, 34 employees, B$0 | Can't be checked; employee counts by category not charted |
| 6 | Livestock-based vs crop-based split | 2013 livestock-based = meat products + Makanan Segera; fish products are counted as crop-based | Keep the publisher's split; explain it in a note |
| 7 | Labels | Malay category names with trailing spaces; "Mi"/"Mee", "Produk Kacang Soya"/"Produk Hasilan Kacang Soya", "Brunei/Muara"/"Brunei Muara"; "Acar & Jeruk" separate in one table, inside "Lain-lain" in another | Trim, standardise, translate; merge pickles into Other |
| 8 | Values in current Brunei dollars | No price adjustment | State it in the limitations |

### Livestock industry tables, Agriculture and Agrifood Department (checked 16 Oct 2026)

Six 2020 editions (broiler, egg, beef, day-old chick, fertilized eggs, slaughtered broilers) and
five 2015 editions. The two editions agree in every shared year except one revision (issue 1).

| # | Issue | Evidence | Status |
|---|---|---|---|
| 1 | Broiler imports 2015 revised | 3,220.44 t (2020 edition) vs 3,317.64 t (2015 edition) | Use the later edition; note the revision |
| 2 | Local chicken meat is calculated, not weighed | Tonnes = birds slaughtered × 1.5 kg in every year 2011–2020 (exact) | Say so on the page: an estimate from bird counts with a fixed weight per bird |
| 3 | October 2018 slaughter count copies September (1,426,601) | Months sum to 9,608 less than the published total; the total matches the meat tonnes | Use the published yearly total; monthly data not charted |
| 4 | Fractional bird | December 2020: 1,694,609.56 | Consistent with issue 2 (back-calculated); keep, round for display |
| 5 | Egg column headed "Monthly Production (Million Eggs)" | Values (61–172 million) are yearly; monthly values would mean ~2 billion eggs a year | Read as yearly production; note the label |
| 6 | Beef imports "n/a" for 1995–1999 | Both import columns | Local share of beef starts in 2000 |
| 7 | Beef chilled & frozen imports are 0 in 2000–2004, then 200 t in 2005 and over 1,000 t from 2006 | Abrupt start | Probably not recorded before 2005 (not stated). Show as first recorded in 2005; beef local share before 2005 is an upper bound |
| 8 | Fertilized eggs title says 2011–2020; file covers 2001–2020 | File name and rows | Use all years; cite the title as published |
| 9 | No export figures | Only local production and imports | Local share = local ÷ (local + imports), not a full self-sufficiency ratio (which also subtracts exports and stock changes) |
| 10 | Day-old chick 2018 = 19,337,447.999999996 | Floating-point artefact | Round to whole birds |

### Trade tables: imports, exports, balance of trade and commodity sections (checked 17 Oct 2026)

Four editions of the yearly totals and three of each commodity-section table, published under
different owners (Department of Statistics, JPES; JPES; Department of Economic Planning and
Statistics; Department of Economic Planning and Development). They agree value by value in
every shared year, within rounding.

| # | Issue | Evidence | Status |
|---|---|---|---|
| 1 | Page coverage understated | Department of Statistics, JPES edition: page says 2000–2020 (2009–2021 and 2000–2021 for the section tables), the yearly totals table includes 2021 | Use 2021; note it on the page |
| 2 | Mixed precision | Some values are published in full (8,446.785…), others rounded to 0.1 million (8,446.8), sometimes in the same year | All checks allow 0.15 million; values kept as published |
| 3 | Section names differ between editions | e.g. "Food" vs "Food and Live animals", "Mineral fuels" vs "Mineral fuels, Lubricants and Related Materials"; classification table spells section 4 "Vegetables Oil and Animals Fats" | Keyed by SITC code (0–9); labels from the classification table |
| 4 | Title typo | DEPD edition titled "Inport, Export And Balance Of Trade" | Cite the title as published |
| 5 | DEPD edition has no "Exports" or "Total Trade" rows | Lists domestic exports, re-exports, imports and balance | Exports and total trade added from the parts for the cross-check only |
| 6 | Same file name in two editions | `Import-Export-and-Balance-of-Trade.xlsx` in the 2025/11 and 2025/12 uploads (different files) | Stored in separate folders with `variant` (shared/fetch.py) |
| 7 | Exports by section start in 2009, imports by section in 2000 | Section tables | Export composition shown from 2009 only |
| 8 | Two SITC revisions in one series | Department of Statistics IMTS FAQ (Q8): SITC Rev. 3 to 2012, Rev. 4 from 2013; the classification table says Rev. 3 | Section-level comparisons hold: Rev. 4 keeps the same ten sections (UN, 2006, para. 15). Noted in the outputs and the glossary |

### Muara Port tables, Ports Department (checked 17 Oct 2026)

Five tables (2004–2015), each with a data definition file. Muara Container Terminal and Muara
Conventional Terminal are used; the three vessel tables were read and left out (issue 4).

| # | Issue | Evidence | Status |
|---|---|---|---|
| 1 | Published total containers ≠ local + transhipment | The data definition says total = local + transhipment, but the totals differ in every year, by 1 to 2,385 TEU (up to 2.4%, 2011); usually the total is higher | Charts use local and transhipment as published; both totals and the difference are in the output and the page's data table |
| 2 | Half TEUs | 2006 total 101,543.5; 2013 local 107,142.5. A TEU is 1 (20') or 2 (40') per container, so a half shouldn't occur | Kept as published; noted in the output |
| 3 | Uncontainerised cargo more than doubles in 2015 | 845,798 t (2014) → 1,931,712 t (2015), +128%; also −40% in 2006 | Shown as published; the page says the table doesn't explain it and nothing here can check it |
| 4 | Vessel tables can't be reconciled | Vessel calling covers Muara only; import and export vessel tables also cover Belait and Temburong ports (domestic vessels), and import + export ≠ vessel calls (e.g. 2008: 1,709 + 261 vs 1,044 calls). The import table has a blank row and a blank 2014 "Other Vessel" cell; "Non-Working Vessel" (berthed with no loading or unloading) reaches 883 | Not used; mentioned in the page's side note and method |
| 5 | Title spellings | Page titles in capitals; "IMPORT VESSELS (2004 – 2015)" uses an en dash | Cited as published |

