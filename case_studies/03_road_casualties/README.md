# 03 — Road casualties, 2009–2017

**Question:** Did road accidents, injuries and deaths go up or down from 2009 to 2017, and did
accidents become less likely to injure or kill?

## Sources

| Dataset | Source | Owner | Licence | Accessed |
|---|---|---|---|---|
| Road Casualties | data.gov.bn | Royal Brunei Police Force | Data.gov.bn Data Policy | 16 Oct 2026 |
| Statistics of Road Traffic Accidents (cross-check only) | data.gov.bn | Fire and Rescue Department Brunei Darussalam | Data.gov.bn Data Policy | 16 Oct 2026 |

Full attributions are generated from `outputs/*.meta.json`. Background sources (two journal
articles and a Borneo Bulletin report) are in `context.yml` and `CONTEXT_SOURCES.md`; they
supply no charted numbers.

## Method

1. Files downloaded with `shared.fetch` into `data/raw/` (see DATA_SOURCES.md).
2. `analysis/clean.py`:
   - Police table reshaped from one "Type" column to one column per measure; the build stops
     if a type changes, a measure is missing or a year is skipped.
   - Injuries per 100 accidents and deaths per 1,000 accidents; averages over three 3-year
     periods (period ratios use period totals).
   - Fire and Rescue table: year filled down, both call types summed.
3. `analysis/build.py`: validates, checks that Fire and Rescue's counts (a subset) never exceed
   the police totals, and writes the CSVs in `outputs/`.
4. `analysis/figures.py`: three charts, each returning its data table.

Run: `uv run python case_studies/03_road_casualties/analysis/build.py`

The full record (each step, why it was done, and the decision log) is in [PROCESS.md](PROCESS.md).

## Findings

Published as *"Brunei's road injuries and deaths fell by about a quarter in 2009–2017, while
accidents held steady"* (`dashboard/case-studies/03-road-casualties.qmd`).

- Accidents a year: 3,374 (2009–2011), 3,338 (2012–2014), 3,412 (2015–2017).
- Injuries a year: 668 → 477 → 487 (−27% first to last period). Deaths: 37 → 28 → 27 (−26%).
- Most of the fall came in one step, 2011 → 2012: injuries −30%, deaths −40%, accidents −8%.
- Injured per 100 accidents 19.8 → 14.3; killed per 1,000 accidents 11.0 → 8.0.

Scope: what changed and when, not why.

## Limitations

- Data ends in 2017; the 2012 step is not explained by the source.
- No definitions of injury or road death; no districts, road users, ages or times.
- Counts only, not adjusted for population or vehicle numbers.

---
Analysis by Muhd Lai Razi with AI assistance (Claude). Not an official publication of the Government of Brunei Darussalam.
