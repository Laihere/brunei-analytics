# data.gov.bn catalogue

`datagovbn_catalogue.csv` is the dataset list (metadata only, no data), built on 14 Oct 2026 with
`python3 -I catalogue/build_catalogue.py <cache_dir> catalogue/datagovbn_catalogue.csv`.

Columns: `id, title, category, owner, published, modified, n_files, formats, page_url, file_urls`.

## Snapshot (14 Oct 2026)

- **686 datasets** published between 9 Sep 2025 and 13 Jul 2026, with 563 unique titles. Re-uploads often reuse a title with a `-2`/`-3` slug, so check `published` and the file contents before choosing between duplicates.
- **Categories:** Sectoral Development 269, Social Wellbeing 189, Economy 128, Population 71, International 28.
- **Formats:** almost all Excel (`xlsx`; 4 also have `xls`). 2 datasets have no file attached.
- **Largest owners:** Ministry of Industry and Primary Resources 167, Ministry of Health 58, Ministry of Education 45, DEPS (under several name variants) ~80, JPES / Department of Statistics 64.
- **Owner not available:** 37 datasets, mostly GDP series. See DATA_USE_POLICY.md for how to credit these.

## Topic clusters worth a look

| Theme | Examples |
|---|---|
| Prices & cost of living | CPI 2025, % change in CPI, retail prices of subsidised and price-controlled items, non-food items |
| Macro economy | GDP by activity and expenditure, GDP per capita, oil & gas vs non-oil & gas |
| Trade | import/export growth, exports by trading partner, imported fresh fish and seafood |
| Labour | unemployment rate (survey and census), labour force 15+, government employees by division and sex, enterprises and employees by sector |
| Population & vital stats | mid-year estimates, population by district/race/sex, births and deaths |
| Health | hospital inpatient morbidity (e.g. cardiovascular) |
| Agriculture & food security | broiler industry 1992–2020, local chicken meat production, fisheries |
| Public safety & transport | crime statistics, road casualties, fire occurrences by district, registered vehicles |
| Climate | temperature, humidity, rainfall and sunshine at Brunei International Airport, rainfall at agricultural stations |
