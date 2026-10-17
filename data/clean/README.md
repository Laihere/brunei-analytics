# data/clean/ (local only)

Full cleaned tables for each case study, saved by its `analysis/build.py` through
`shared/clean_data.py`. They are kept for future reference: follow-up case studies, newer
editions and cross-checks can start from them instead of cleaning the raw files again.

**Everything here except this README is gitignored and is never published.** These tables:

- are **not** the datasets published on data.gov.bn or by the other approved sources. They
  are reshaped, renamed and sometimes repaired copies of parts of them;
- are **not** this project's findings. The published results are the case study pages and
  their `outputs/` tables;
- may hold detail that is deliberately left out of the published outputs, such as small
  counts (DATA_USE_POLICY.md §8, rule 3).

To use the data, get it from the original dataset pages linked in each case study.

## Layout

    data/clean/<NN_study>/<table>.csv
    data/clean/<NN_study>/<table>.csv.meta.json   sources, notes, code version, clean.py hash

Rebuild a study's tables (and its outputs) with
`uv run python case_studies/<NN_study>/analysis/build.py`; it needs that study's raw files in
`data/raw/`. Back up `data/` privately (an encrypted drive or a private cloud folder, not a
GitHub repository): neither raw nor clean data is stored anywhere else.
