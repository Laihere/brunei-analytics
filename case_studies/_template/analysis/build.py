"""Build this case study's outputs from data/raw/.

Run from the repo root:  uv run python case_studies/{NN_name}/analysis/build.py
"""

from pathlib import Path

from shared.fetch import download
from shared.outputs import write_output
from shared.provenance import read_meta

OUT = Path(__file__).resolve().parents[1] / "outputs"


def main():
    raw = download(
        source="datagovbn",
        file_url="{file URL from catalogue/datagovbn_catalogue.csv}",
        title="{dataset title}",
        page_url="{dataset page URL}",
        edition="{year in the dataset title, else year published}",
        owner="{Data Source Owner, copied exactly}",
        coverage="{period the data covers, e.g. 2015–2025}",
    )
    provenance, _ = read_meta(raw)

    df = ...  # read, clean and analyse

    write_output(df, OUT / "{name}.csv", provenance, notes="{what was done to the data}")


if __name__ == "__main__":
    main()
