# Brunei Analytics

Case studies and dashboards on Brunei Darussalam's public data, by Muhd Lai Razi,
built with AI assistance (Claude by Anthropic). See [DATA_USE_POLICY.md](DATA_USE_POLICY.md) rule 10.

Every dataset is used under its published terms. See [DATA_USE_POLICY.md](DATA_USE_POLICY.md).
Independent analysis, not an official publication of the Government of Brunei Darussalam.

## Sources

data.gov.bn, World Bank WDI, FAOSTAT and ILOSTAT only (policy §6). Raw files are not
included in this repo. Each case study links to the original datasets.

## Layout

```
DATA_USE_POLICY.md    how data is credited and handled
DATA_SOURCES.md       log of every download
catalogue/            index of all data.gov.bn datasets (metadata only)
shared/               approved sources, cached downloads, provenance, chart style
case_studies/NN_*/    one folder per study: analysis/, outputs/ and PROCESS.md
docs/WORKFLOW.md      the standard pipeline every case study follows
dashboard/            Quarto site, built from case study outputs only
data/raw/             local downloads (gitignored): <source>/<edition>/<dataset-slug>/
```

## Setup

Requires [uv](https://docs.astral.sh/uv/) and [Quarto](https://quarto.org/).

```sh
uv sync
uv run pytest
```

## Workflow

The full pipeline, with its diagram and checks, is in [docs/WORKFLOW.md](docs/WORKFLOW.md).
Each study records how it followed it in its `PROCESS.md` (repo only, not on the site).

1. Copy `case_studies/_template` to `case_studies/NN_name`, and `dashboard/case-studies/_template.qmd`
   to `dashboard/case-studies/NN-name.qmd`. Fill in the front matter (`number`, `topic`, `read-time`…).
2. Find datasets in `catalogue/datagovbn_catalogue.csv`.
3. Run the study's build script locally: `uv run python case_studies/NN_name/analysis/build.py`.
   It downloads to `data/raw/` once and writes small CSVs with `.meta.json` provenance to `outputs/`.
4. Build the page with the components in `shared/components.py` (stat tiles, chart cards,
   method and sources, prev/next) and `shared/charts.highlight`.
5. Log the downloads in `DATA_SOURCES.md`, and fill in the study's `PROCESS.md` as you go.
6. Preview: `uv run quarto preview dashboard`. Use the preview server rather than opening
   `_site/*.html` directly, since browsers block some of Quarto's scripts on `file://` pages
   (e.g. the contents list stays empty).
   If a local render fails with `NotFound … rename … index.html`, delete `dashboard/_site`
   and `dashboard/.quarto` and render again (intermittent Quarto issue; CI always renders clean).
7. Commit the code and `outputs/`. GitHub Actions tests and deploys the site to Pages.

## Design

`DESIGN.md` is the design brief. `docs/design/mockups/` holds the HTML mock-ups
(Styled/Wireframe toggle and design notes) that the Quarto theme (`dashboard/theme.scss`)
was built from.
