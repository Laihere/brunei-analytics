"""District shapes for maps (DATA_USE_POLICY.md §6, geoBoundaries).

Reads the simplified geoBoundaries file for Brunei's four districts from data/raw/ and writes
case_studies/_shared/outputs/brunei_districts.csv: one SVG path per district, projected and
scaled to a 1000-unit-wide box, plus a label position. The raw file stays local like every
download; this small output is committed so the site can draw maps without it.

Run: uv run python case_studies/_shared/build_maps.py
"""

import json
import math
from dataclasses import replace

import pandas as pd

from shared.outputs import write_output
from shared.paths import CASE_STUDIES, RAW
from shared.provenance import read_meta

RAW_FILE = (
    RAW
    / "geoboundaries/2023/brunei-darussalam-adm1-districts-boundaries-simplified"
    / "geoBoundaries-BRN-ADM1_simplified.geojson"
)
OUT = CASE_STUDIES / "_shared" / "outputs" / "brunei_districts.csv"
WIDTH = 1000
DISTRICTS = {"Belait", "Brunei-Muara", "Temburong", "Tutong"}  # spelt as in our outputs


def _polygons(geometry: dict) -> list:
    return (
        geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    )


def _area_centroid(ring: list) -> tuple[float, float, float]:
    """Signed area and centroid of a ring (shoelace formula), in projected units."""
    a = cx = cy = 0.0
    for (x0, y0), (x1, y1) in zip(ring, ring[1:] + ring[:1], strict=True):
        cross = x0 * y1 - x1 * y0
        a += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    a /= 2
    return abs(a), cx / (6 * a), cy / (6 * a)


def build() -> pd.DataFrame:
    geo = json.loads(RAW_FILE.read_text())
    features = geo["features"]
    names = {f["properties"]["shapeName"] for f in features}
    assert names == DISTRICTS, f"Unexpected district names: {names}"

    points = [
        pt for f in features for poly in _polygons(f["geometry"]) for ring in poly for pt in ring
    ]
    lon0, lon1 = min(p[0] for p in points), max(p[0] for p in points)
    lat0, lat1 = min(p[1] for p in points), max(p[1] for p in points)
    # Equirectangular, with longitude scaled by cos(latitude): accurate enough at Brunei's size.
    k = math.cos(math.radians((lat0 + lat1) / 2))
    scale = WIDTH / ((lon1 - lon0) * k)
    height = (lat1 - lat0) * scale

    def project(pt):
        return ((pt[0] - lon0) * k * scale, (lat1 - pt[1]) * scale)

    rows = []
    for f in features:
        rings = [[project(pt) for pt in ring] for poly in _polygons(f["geometry"]) for ring in poly]
        path = "".join(
            "M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in ring[:-1]) + "Z" for ring in rings
        )
        # Label at the centroid of the largest ring (e.g. Brunei-Muara's mainland, not islands).
        _, lx, ly = max((_area_centroid(r[:-1]) for r in rings), key=lambda t: t[0])
        rows.append(
            {
                "district": f["properties"]["shapeName"],
                "path": path,
                "label_x": round(lx, 1),
                "label_y": round(ly, 1),
            }
        )
    df = pd.DataFrame(rows).sort_values("district")
    df["box_w"], df["box_h"] = WIDTH, round(height, 1)

    prov = [
        replace(p, owner="", original_source="Wikimedia Commons (user Tachymetre)")
        for p in read_meta(RAW_FILE)[0]
    ]
    write_output(
        df,
        OUT,
        prov,
        notes=(
            "District boundaries from geoBoundaries (simplified Brunei ADM1 file), projected "
            "(equirectangular, longitude scaled by cos of the mid-latitude) to SVG paths in a "
            f"{WIDTH}-unit-wide box; label at the centroid of each district's largest polygon. "
            "Boundaries are approximate and for illustration only; not an official map."
        ),
    )
    return df


if __name__ == "__main__":
    print(build()[["district", "label_x", "label_y", "box_w", "box_h"]])
