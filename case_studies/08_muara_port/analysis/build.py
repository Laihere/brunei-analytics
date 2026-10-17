"""Build case study 08 outputs from data/raw/.

Run from the repo root:  uv run python case_studies/08_muara_port/analysis/build.py
"""

import sys
import warnings
from pathlib import Path

import pandas as pd
import pandera.pandas as pa

sys.path.insert(0, str(Path(__file__).parent))
from clean import load_cargo, load_containers  # noqa: E402
from sources import fetch  # noqa: E402

from shared.clean_data import write_clean  # noqa: E402
from shared.outputs import write_output  # noqa: E402
from shared.provenance import read_meta  # noqa: E402

warnings.filterwarnings("ignore", message="Unknown extension")  # openpyxl, harmless
OUT = Path(__file__).resolve().parents[1] / "outputs"
MAX_GAP_PCT = 2.5  # published total vs local + transhipment; larger would need a closer look

CONTAINER_SCHEMA = pa.DataFrameSchema(
    {
        "year": pa.Column(int, unique=True),
        **{
            c: pa.Column(float, pa.Check.ge(0))
            for c in ["local_teu", "transhipment_teu", "total_teu", "total_published_teu"]
        },
        "gap_teu": pa.Column(float),
        "transhipment_share_pct": pa.Column(float, pa.Check.in_range(0, 100)),
    }
)
CARGO_SCHEMA = pa.DataFrameSchema(
    {"year": pa.Column(int, unique=True), "cargo_tonnes": pa.Column(float, pa.Check.gt(0))}
)


def prov(path: Path):
    return read_meta(path)[0]


def main():
    p = fetch()
    containers = load_containers(p["container"][0])
    CONTAINER_SCHEMA.validate(containers)
    gap_pct = (containers.gap_teu / containers.total_published_teu * 100).abs()
    if (gap_pct > MAX_GAP_PCT).any():
        raise ValueError(f"Published total differs from local + transhipment by >{MAX_GAP_PCT}%.")
    cargo = load_cargo(p["conventional"][0])
    CARGO_SCHEMA.validate(cargo)
    if containers.year.tolist() != cargo.year.tolist():
        raise ValueError("The two terminal tables cover different years.")
    first, last = containers.year.min(), containers.year.max()

    write_output(
        containers.round({"transhipment_share_pct": 2}),
        OUT / "port_containers.csv",
        prov(p["container"][0]),
        notes=(
            f"Containers handled at Muara Container Terminal, {first}–{last}, in TEUs, as "
            "published: local (bound for or from Brunei) and transhipment (transiting). "
            "'total_teu' is local + transhipment, as the Ports Department's data definition "
            "describes; the published total ('total_published_teu') differs from it in most "
            "years ('gap_teu', at most 2.4%). Two values are published with a half TEU. "
            "Transhipment share computed by the author."
        ),
    )
    cargo["change_pct"] = cargo.cargo_tonnes.pct_change() * 100
    write_output(
        cargo.round({"change_pct": 1}),
        OUT / "port_cargo.csv",
        prov(p["conventional"][0]),
        notes=(
            f"Uncontainerised (loose) cargo handled at Muara Conventional Terminal, {first}–"
            f"{last}, tonnes, as published. Change on the previous year computed by the author."
        ),
    )

    # Full cleaned tables, local only (data/clean/, policy §4 rule 3).
    write_clean(
        containers,
        __file__,
        "port_containers",
        prov(p["container"][0]),
        notes="Containers by year in TEUs: published columns, sum, gap and transhipment share.",
    )
    write_clean(
        cargo,
        __file__,
        "port_cargo",
        prov(p["conventional"][0]),
        notes="Uncontainerised cargo by year, tonnes, with change on the previous year.",
    )
    report(containers, cargo)


def report(containers: pd.DataFrame, cargo: pd.DataFrame):
    pd.set_option("display.width", 160)
    print("\n== Containers (TEU)")
    print(containers.round(1).to_string(index=False))
    print("\n== Uncontainerised cargo (tonnes)")
    print(cargo.round(1).to_string(index=False))


if __name__ == "__main__":
    main()
