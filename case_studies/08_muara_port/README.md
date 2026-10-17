# 08 — Muara Port: containers and loose cargo, 2004–2015

**Question:** How many containers and how much loose cargo did Muara Port handle from 2004 to 2015?

## Sources

| Dataset | Source | Owner | Licence | Accessed |
|---|---|---|---|---|
| MUARA CONTAINER TERMINAL, MUARA PORT 2004-2015 (table + data definition) | data.gov.bn | Berthing Section and Statistic Unit, Ports Department | Data.gov.bn Data Policy | 17 Oct 2026 |
| MUARA CONVENTIONAL TERMINAL, MUARA PORT 2004-2015 (table + data definition) | data.gov.bn | Berthing Section and Statistic Unit, Ports Department | Data.gov.bn Data Policy | 17 Oct 2026 |
| VESSEL CALLING, IMPORT VESSELS, EXPORT VESSELS (2004–2015) | data.gov.bn | Berthing Section and Statistic Unit, Ports Department | Data.gov.bn Data Policy | 17 Oct 2026 (inspected, not used) |

Full attributions are generated from `outputs/*.meta.json`. Every file is listed in
[DATA_SOURCES.md](../../DATA_SOURCES.md).

## Method

1. `analysis/sources.py` downloads each table and its data definition once with `shared.fetch.download`.
2. `analysis/clean.py` drops spacer columns, checks every year appears once, and computes local +
   transhipment (the definition of total containers) beside the published total.
3. `analysis/build.py` checks the gap stays under 2.5%, computes the transhipment share and the yearly
   change in loose cargo, and writes the outputs and the local cleaned tables.

The full record is in [PROCESS.md](PROCESS.md).

## Findings

- Containers: 101,186 TEU in 2004 and 102,799 in 2015 (local + transhipment). Local containers grew 38%
  (peak 114,096 in 2012); transhipment fell from 26,985 (27%) to zero in 2009 and stayed under 3,200.
- Loose cargo: 1.89 million tonnes in 2004, about 0.85–1.2 million from 2006 to 2014, 1.93 million in 2015.

## Limitations

- Published container totals differ from local + transhipment by up to 2.4%; the 2015 cargo jump is
  unexplained; Muara only, to 2015. The page shows what changed, not why.

---
Analysis by Muhd Lai Razi with AI assistance (Claude). Not an official publication of the Government of Brunei Darussalam.
