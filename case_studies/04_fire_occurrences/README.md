# 04 — Fire occurrences by district, 2009–2020

**Question:** How did the number of fires change from 2009 to 2020, which years stood out, and
did the peak years affect every district?

## Sources

| Dataset | Source | Owner (as listed) | Licence | Accessed |
|---|---|---|---|---|
| Fire Occurances By Districts (2009–2020) | data.gov.bn | Brunei Darussalam Central Bank | Data.gov.bn Data Policy | 16 Oct 2026 |
| Fire Occurances By Districts (2009–2013, cross-check only) | data.gov.bn | Brunei Fire and Rescue Department | Data.gov.bn Data Policy | 16 Oct 2026 |
| Statistic of Forest and Grass/Peat Fire (2012–2021) | data.gov.bn | Fire and Rescue Department Brunei Darussalam | Data.gov.bn Data Policy | 16 Oct 2026 |

Full attributions are generated from `outputs/*.meta.json`. Background sources (two
peer-reviewed studies) are in `context.yml` and `CONTEXT_SOURCES.md`; they supply no charted
numbers.

## Method

1. Files downloaded with `shared.fetch` into `data/raw/` (see DATA_SOURCES.md).
2. `analysis/clean.py`: districts checked (all four, once per year, no gaps) and spelt
   officially; the two editions compared (the build stops if they differ outside 2013); the
   forest and grass/peat table summed per year.
3. `analysis/build.py`: yearly totals, each year ÷ the median year, district shares; hectares
   burned joined by year (never added to fire counts).
4. `analysis/figures.py`: three charts, with the three highest years in teal throughout.

Run: `uv run python case_studies/04_fire_occurrences/analysis/build.py`

The full record (each step, why it was done, and the decision log) is in [PROCESS.md](PROCESS.md).

## Findings

Published as *"Brunei's fire peaks in 2009–2020 hit all four districts in the same years"*
(`dashboard/case-studies/04-fire-occurrences.qmd`).

- Typical (median) year: 1,187 fires (1,186.5). 2010: 4,299 (3.6×); 2019: 2,053; 2016: 1,852.
- 2012–2020: fires and hectares burned move together (correlation 0.97, 9 years).
- Brunei-Muara 54% of fires (41–64% each year), Belait 25%, Tutong 19%, Temburong 2%.
- In every district the three highest years were 2010, 2016 and 2019.

## Limitations

- "Fire occurrence" isn't defined; no causes, damage or casualties; data ends 2020.
- Counts not adjusted for population or area.
- The two editions disagree for 2013 (791 vs 265); the longer edition is used.

---
Analysis by Muhd Lai Razi Muhd Silmi with AI assistance (Claude). Not an official publication of the Government of Brunei Darussalam.
