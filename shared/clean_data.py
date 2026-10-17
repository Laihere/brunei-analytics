"""Full cleaned tables, kept locally for future reference (DATA_USE_POLICY.md §4, rule 3).

`write_clean` saves a case study's tidy tables straight from clean.py, at full precision and
before anything is merged, suppressed or rounded for publication, to
data/clean/<study>/<name>.csv. Each has a .meta.json sidecar: the datasets behind it, what
was done to them, and the code that made it, so a table can be traced and rebuilt.

data/clean/ is gitignored and never published. These tables are not the published datasets
and not this project's findings; they are working copies (see data/clean/README.md).
"""

import hashlib
import json
import subprocess
from datetime import date
from pathlib import Path

import pandas as pd

from shared.paths import ROOT
from shared.provenance import Provenance, meta_path, read_meta, write_meta

CLEAN = ROOT / "data" / "clean"
STATUS = "Local working copy, not for publication (DATA_USE_POLICY.md §4 rule 3, §8)."


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


def _code_version() -> str:
    """Current commit, marked "+changes" if the working tree differs from it."""
    try:
        changed = "+changes" if _git("status", "--short") else ""
        return _git("rev-parse", "--short", "HEAD") + changed
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def write_clean(
    df: pd.DataFrame,
    build_script: str | Path,
    name: str,
    provenance: list[Provenance],
    notes: str,
    root: Path = CLEAN,
) -> Path:
    """Save one cleaned table for the study whose build.py is `build_script` (pass __file__)."""
    if not provenance:
        raise ValueError("Cleaned tables must list the datasets they were built from.")
    if not notes.strip():
        raise ValueError("Cleaned tables must describe what was done to the data.")
    analysis = Path(build_script).resolve().parent
    study = analysis.parent.name
    path = root / study / f"{name}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    write_meta(path, list(dict.fromkeys(provenance)), notes)

    meta = json.loads(meta_path(path).read_text())
    clean_py = analysis / "clean.py"
    meta |= {
        "status": STATUS,
        "study": study,
        "rows": len(df),
        "columns": list(df.columns),
        "created": date.today().isoformat(),
        "code_version": _code_version(),
        "clean_py_sha256": hashlib.sha256(clean_py.read_bytes()).hexdigest()
        if clean_py.exists()
        else "",
    }
    meta_path(path).write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")
    return path


def read_clean(study: str, name: str, root: Path = CLEAN) -> tuple[pd.DataFrame, list, str]:
    path = root / study / f"{name}.csv"
    provenance, notes = read_meta(path)
    return pd.read_csv(path), provenance, notes
