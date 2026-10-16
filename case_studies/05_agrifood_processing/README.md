# 05 — Agrifood processing (agrimakanan), 2004–2013

**Question:** How did Brunei's food processing industry change from 2004 to 2013, what did it
make, and where was it based?

Part (a) of the agrimakanan topic. Part (b), the livestock industry series, is a separate study.

## Sources

All from data.gov.bn, owner Ministry of Industry and Primary Resources, Data.gov.bn Data Policy,
accessed 16 Oct 2026. Titles are in Malay; English translations are given in APA brackets.

| Dataset (Malay) | English | Used for |
|---|---|---|
| Status Pengeluaran Produck Agrimakanan | Status of agrifood product production | 2004–2013 series |
| Tren Pengeluaran Agrimakanan Mengikut Kategori Produk | Agrifood production trends by product category | Categories 2010–2013 |
| Statistik Industri Agrimakanan | Agrifood industry statistics | Categories 2013 |
| Statistik Industri Agrimakanan Mengikut Daerah Dan Kategori Produck | … by district and product category | Cross-check and business counts only (not published) |
| Status Pengeluaran Agrimakanan Mengikut Daerah | Status of agrifood production by district | Districts 2013 |

Full attributions are generated from `outputs/*.meta.json`. Background sources (two
institutional reports; no peer-reviewed study was found) are in `context.yml` and
`CONTEXT_SOURCES.md`.

## Method

1. Files downloaded with `shared.fetch` into `data/raw/` (see DATA_SOURCES.md).
2. `analysis/clean.py`: Malay names standardised (several spellings) and translated, Malay kept
   alongside; 2003 dropped (crop value n/a) and totals recomputed; the build stops if a category
   or district rests on fewer than 5 businesses, or if the tables disagree.
3. `analysis/build.py`: separates "Makanan Segera" (first counted in 2013) from the categories
   counted every year; writes four CSVs.
4. `analysis/figures.py`: four charts; the 2013 newcomer is always grey.

Run: `uv run python case_studies/05_agrifood_processing/analysis/build.py`

The full record (each step, why it was done, and the decision log) is in [PROCESS.md](PROCESS.md).

## Findings

Published as *"Brunei's food processing grew 2.6× in 2004–2012; most of 2013's jump came from a
newly counted category"* (`dashboard/case-studies/05-agrifood-processing.qmd`).

- Market value rose every year: B$24.0m (2004) → B$62.8m (2012).
- 2013: B$86.2m, of which B$34.5m (40%) is fast or instant food, first counted that year.
  Without it: B$51.7m, −18% on 2012; biscuits & bakery B$30.0m → B$23.0m.
- 2013: traditional foods had the most businesses (125) but 2.4% of value.
- 2013: Brunei-Muara had 71% of businesses, 89% of employees, 97% of value.

## Limitations

- Ends in 2013; current dollars; "Makanan Segera" may have existed uncounted before 2013.
- Head-counts differ between two tables; the district table is used for totals.
- Processed food only, not farm production.

---
Analysis by Muhd Lai Razi with AI assistance (Claude). Not an official publication of the Government of Brunei Darussalam.
