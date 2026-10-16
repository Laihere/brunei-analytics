# 02 — Crime statistics, 2012–2013

**Question:** What kinds of offences made up police cases in 2012 and 2013, how many were
solved, and what changed between the two years?

## Sources

| Dataset | Source | Owner | Licence | Accessed |
|---|---|---|---|---|
| Crime Statistics (2012 table) | data.gov.bn | Royal Brunei Police Force | Data.gov.bn Data Policy | 16 Oct 2026 |
| Crime Statistics (2013 table) | data.gov.bn | Royal Brunei Police Force | Data.gov.bn Data Policy | 16 Oct 2026 |

Full attributions are generated from `outputs/*.meta.json`. Both datasets have the same owner,
year and title, so the APA references are 2025a (2012 table) and 2025b (2013 table).

## Method

1. Files downloaded with `shared.fetch` into `data/raw/` (see DATA_SOURCES.md). `build.py`
   lists the editions in `EDITIONS`; a newer table can be added there.
2. `analysis/clean.py`:
   - Reads each yearbook table by its labels (not fixed rows), keeping the Malay and English
     names. Uses the stored values of the Excel formulas.
   - Checks that the rows add up to the published totals in every year.
   - Reads "-" as missing. Merges other-agency Acts with fewer than 5 cases in any year into
     "Other Acts" (SOP 7).
3. `analysis/build.py`: computes each type's share of cases and share solved, validates both
   outputs, and writes the CSVs in `outputs/`.
4. `analysis/figures.py`: three grouped bar charts, each returning its data table.

Run: `uv run python case_studies/02_crime_statistics/analysis/build.py`

The full record (each step, why it was done, and the decision log) is in [PROCESS.md](PROCESS.md).

## Findings

Published as *"Property offences made up nearly two-thirds of police cases in Brunei in
2012–2013"* (`dashboard/case-studies/02-crime-statistics.qmd`).

- Police cases: 5,037 (2012) → 5,503 (2013), +9.3%. Property offences: 63% → 64% of cases,
  and 393 of the 466 extra cases.
- Solved: about 22% of police cases in both years; 82% of offences against the human body vs
  14% of property offences (2013).
- Other agencies: 852 → 939 cases. Drug cases 283 → 360; customs and excise 366 → 356.

Scope: what was recorded, not why. Changes between two single years are not described as trends.

## Limitations

- Only 2012 and 2013 are published; nothing about crime today and no trend.
- Recorded cases only; no districts, months, specific offences or population rates.
- "-" cells are unexplained; solved/arrest counts for the Labour Act and "Other Acts" are incomplete.
- "Solved" isn't defined in the source.

---
Analysis by Muhd Lai Razi with AI assistance (Claude). Not an official publication of the Government of Brunei Darussalam.
