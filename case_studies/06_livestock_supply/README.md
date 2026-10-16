# 06 — Livestock supply: chicken, eggs and beef, 1992–2020

**Question:** How much of Brunei's chicken, eggs and beef was produced locally from 1992 to
2020, and how local is the chicken supply chain, from hatching eggs to meat?

Part (b) of the agrimakanan topic (part (a) is case study 05).

## Sources

All from data.gov.bn, Data.gov.bn Data Policy, accessed 16 Oct 2026.

| Dataset | Owner (as listed) | Edition | Used for |
|---|---|---|---|
| Broiler, Egg, Beef, Day Old Chick, Fertilized Eggs Industry tables | Agriculture and Agrifood Department | 2020 | Local production and imports |
| Number Of Slaughtered Broilers, 2011-2020 | Agriculture and Agrifood Department | 2020 | Cross-check (1.5 kg per bird) |
| Broiler, Egg, Beef, Day Old Chick, Fertilized Eggs Industry tables | Department of Agriculture and Agrifood, Ministry of Primary Resources and Tourism | 2015 | Cross-check of shared years |

Full attributions are generated from `outputs/*.meta.json`. Background sources (three
peer-reviewed studies and two institutional reports) are in `context.yml` and
`CONTEXT_SOURCES.md`.

## Method

1. Files downloaded with `shared.fetch` into `data/raw/` (see DATA_SOURCES.md).
2. `analysis/clean.py`: one long table of local production and imports per product and year;
   "n/a" years dropped (beef before 2000); local share = local ÷ (local + imports); the 2020
   and 2015 editions compared (the build stops on an unlogged difference); chicken tonnes
   checked against birds slaughtered.
3. `analysis/build.py`: writes the supply table, the slaughter check and the edition revisions.
4. `analysis/figures.py`: four charts; teal is always "produced locally".

Run: `uv run python case_studies/06_livestock_supply/analysis/build.py`

The full record (each step, why it was done, and the decision log) is in [PROCESS.md](PROCESS.md).

## Findings

Published as *"By 2020, Brunei produced 97% of its chicken and nearly all its eggs, but under 2%
of its beef"* (`dashboard/case-studies/06-livestock-supply.qmd`).

- Chicken meat: 32% local (1992) → 97% (2020); above 90% from 2001; lowest since then 83.5% (2018).
  In 2020 imports fell from 3,223 t to 715 t.
- Eggs: never below 97% local; 62 → 172 million eggs a year.
- Beef: 1.9% local in 2020 (3,475 t supply); imports live and, from 2005, chilled & frozen.
- Chicken chain 2020: meat 97% local, day-old chicks 90%, hatching eggs 56%; chicks and hatching
  eggs less local than in 2010.
- Local chicken tonnes = birds slaughtered × 1.5 kg in every year 2011–2020.

## Limitations

- No exports or stocks, so the local share isn't a full self-sufficiency ratio.
- Chicken tonnes estimated from bird counts; beef chilled & frozen imports not recorded before 2005.
- Ends in 2020; feed and other inputs not covered.

---
Analysis by Muhd Lai Razi with AI assistance (Claude). Not an official publication of the Government of Brunei Darussalam.
