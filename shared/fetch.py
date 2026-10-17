"""Downloads into data/raw/, organised by source, edition and dataset, with a provenance sidecar.

    data/raw/<source>/<edition>/<dataset-slug>/<original filename>
    data/raw/<source>/<edition>/<dataset-slug>/<original filename>.meta.json

`edition` is the year in the dataset title ("Consumer Price Index 2025" → "2025"), or the year
it was published when the title has none. It is not the period the data covers: "CPI 2025"
covers 2015–2025, so that goes in `coverage`. `published` is the date the publisher released it
(the APA citation year). Each file is fetched once (SOP rule 9).

`variant` separates copies of one table that share a title and edition but come from different
owners (e.g. the trade tables published by DEPS, JPES and the Department of Statistics, JPES):
the folder becomes <dataset-slug>--<variant>.
"""

import hashlib
import re
import shutil
import time
from collections.abc import Callable
from datetime import date
from pathlib import Path
from urllib.parse import unquote, urlparse

import pandas as pd
import requests

from shared.paths import RAW
from shared.provenance import Provenance, meta_path, read_meta, write_meta
from shared.sources import get_source

DELAY_S = 1.0
HEADERS = {"User-Agent": "brunei_analytics (personal, non-commercial research)"}
_YEAR = re.compile(r"\b(19|20)\d{2}\b")


def edition_of(title: str, published: str = "") -> str:
    """Year in the title, else the year published (ISO date)."""
    match = _YEAR.search(title)
    if match:
        return match.group(0)
    if published:
        return str(date.fromisoformat(published[:10]).year)
    raise ValueError(f"No year in '{title}'; pass the published date to set the edition.")


def slug_of(title: str) -> str:
    """Dataset title without its year, as a folder name."""
    text = _YEAR.sub("", title).lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def dataset_dir(
    source: str, edition: str, title: str, raw_dir: Path = RAW, variant: str = ""
) -> Path:
    get_source(source)
    if not re.fullmatch(r"\d{4}", edition):
        raise ValueError(f"Edition must be a year, got '{edition}'.")
    slug = slug_of(title) + (f"--{slug_of(variant)}" if variant else "")
    return raw_dir / source / edition / slug


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def download(
    source: str,
    file_url: str,
    title: str,
    page_url: str,
    edition: str,
    owner: str = "",
    coverage: str = "",
    licence: str = "",
    published: str = "",
    raw_dir: Path = RAW,
    title_translation: str = "",
    variant: str = "",
) -> Path:
    """Download a file once and record where it came from."""
    folder = dataset_dir(source, edition, title, raw_dir, variant)
    dest = folder / unquote(Path(urlparse(file_url).path).name)
    if dest.exists() and meta_path(dest).exists():
        return dest

    resp = requests.get(file_url, headers=HEADERS, timeout=60)
    resp.raise_for_status()
    folder.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(resp.content)
    prov = Provenance(
        source=source,
        title=title,
        page_url=page_url,
        accessed=date.today().isoformat(),
        file_url=file_url,
        owner=owner,
        licence=licence,
        edition=edition,
        coverage=coverage,
        sha256=sha256_of(dest),
        published=published,
        title_translation=title_translation,
    )
    write_meta(dest, [prov])
    time.sleep(DELAY_S)
    return dest


def adopt(
    path: Path,
    source: str,
    file_url: str,
    title: str,
    page_url: str,
    edition: str,
    accessed: str,
    owner: str = "",
    coverage: str = "",
    licence: str = "",
    published: str = "",
    raw_dir: Path = RAW,
) -> Path:
    """File a manually downloaded copy into the layout and record its provenance.

    `accessed` is the date it was downloaded by hand (ISO). The original file is moved, not copied.
    """
    folder = dataset_dir(source, edition, title, raw_dir)
    dest = folder / path.name
    if dest.exists():
        raise FileExistsError(f"{dest} already exists.")
    folder.mkdir(parents=True, exist_ok=True)
    shutil.move(path, dest)
    prov = Provenance(
        source=source,
        title=title,
        page_url=page_url,
        accessed=accessed,
        file_url=file_url,
        owner=owner,
        licence=licence,
        edition=edition,
        coverage=coverage,
        sha256=sha256_of(dest),
        published=published,
    )
    write_meta(dest, [prov])
    return dest


def cached_frame(
    source: str,
    name: str,
    title: str,
    page_url: str,
    loader: Callable[[], pd.DataFrame],
    coverage: str = "",
    licence: str = "",
    folder: str = "",
    raw_dir: Path = RAW,
) -> tuple[pd.DataFrame, Provenance]:
    """Cache an API pull (e.g. wbgapi) as CSV, calling `loader` only on first use.

    API data has no edition, so it is filed under the year it was first pulled. `folder`
    overrides the folder name when the title is long (e.g. an indicator name).
    """
    slug = folder or slug_of(title)
    existing = sorted((raw_dir / source).glob(f"*/{slug}/{name}.csv"))
    if existing and meta_path(existing[-1]).exists():
        dest = existing[-1]
    else:
        today = date.today()
        target = dataset_dir(source, str(today.year), slug, raw_dir)
        target.mkdir(parents=True, exist_ok=True)
        dest = target / f"{name}.csv"
        loader().to_csv(dest, index=False)
        prov = Provenance(
            source=source,
            title=title,
            page_url=page_url,
            accessed=today.isoformat(),
            licence=licence,
            edition=str(today.year),
            coverage=coverage,
            sha256=sha256_of(dest),
        )
        write_meta(dest, [prov])
    return pd.read_csv(dest), read_meta(dest)[0][0]
