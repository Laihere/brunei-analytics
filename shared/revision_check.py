"""Check whether the data.gov.bn datasets behind published case studies have changed
(DATA_USE_POLICY §4 rule 11; the portal has no change log or notifications).

For every data.gov.bn file credited in case_studies/*/outputs/*.meta.json:
  - the dataset page still loads and still links the same file;
  - the "Data Source Owner" on the page matches what we credit;
  - the file still downloads and its sha256 matches the one recorded when we used it;
  - the post's "modified" date from the WordPress API (shown for information).

Files are hashed in memory and not saved. One request at a time, with a delay (SOP rule 9).

    uv run python -m shared.revision_check            # print the report
    uv run python -m shared.revision_check --log      # also append a summary to docs/REVISION_CHECKS.md
"""

import hashlib
import html
import json
import re
import sys
import time
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import requests

from shared.fetch import DELAY_S, HEADERS

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "docs" / "REVISION_CHECKS.md"
API = "https://www.data.gov.bn/wp-json/wp/v2/posts"


def sources_in_use() -> dict[str, dict]:
    """Unique data.gov.bn files credited by published outputs, with the studies using them."""
    found: dict[str, dict] = {}
    for meta in sorted(ROOT.glob("case_studies/*/outputs/*.meta.json")):
        study = meta.parts[-3]
        for s in json.loads(meta.read_text())["sources"]:
            if s["source"] != "datagovbn":
                continue
            entry = found.setdefault(s["file_url"], {**s, "studies": set()})
            entry["studies"].add(study)
    return found


def page_owner(text: str) -> str:
    lines = [html.unescape(x).strip() for x in re.sub(r"<[^>]+>", "\n", text).splitlines()]
    lines = [x for x in lines if x]
    for i, line in enumerate(lines):
        if line == "Data Source Owner" and i + 1 < len(lines):
            return lines[i + 1]
    return ""


def _get(url: str) -> requests.Response:
    resp = requests.get(url, headers=HEADERS, timeout=60)
    time.sleep(DELAY_S)
    return resp


def check(s: dict) -> dict:
    row = {"title": s["title"], "studies": ", ".join(sorted(s["studies"])), "issues": []}
    page = _get(s["page_url"])
    if page.status_code != 200:
        row["issues"].append(f"page returned HTTP {page.status_code}")
    else:
        path = urlparse(s["file_url"]).path
        if path not in page.text and path.lstrip("/") not in page.text:
            row["issues"].append("page no longer links the file we used")
        owner = page_owner(page.text)
        if owner != s["owner"]:
            row["issues"].append(f"owner on page is {owner!r}, we credit {s['owner']!r}")
    slug = urlparse(s["page_url"]).path.strip("/").split("/")[-1]
    api = _get(f"{API}?slug={slug}&_fields=modified")
    row["modified"] = api.json()[0]["modified"][:10] if api.ok and api.json() else "?"
    f = _get(s["file_url"])
    if f.status_code != 200:
        row["issues"].append(f"file returned HTTP {f.status_code}")
    elif hashlib.sha256(f.content).hexdigest() != s["sha256"]:
        row["issues"].append("file content changed (sha256 differs)")
    return row


def main(log: bool = False) -> int:
    sources = sources_in_use()
    rows = []
    for i, s in enumerate(sources.values(), 1):
        print(f"[{i}/{len(sources)}] {s['title']}", file=sys.stderr)
        rows.append(check(s))
    changed = [r for r in rows if r["issues"]]
    print(f"\n{len(rows)} files checked, {len(changed)} with differences.\n")
    for r in rows:
        status = "; ".join(r["issues"]) or "unchanged"
        print(f"- {r['title']} ({r['studies']}; page modified {r['modified']}): {status}")
    if log:
        today = date.today().isoformat()
        lines = [f"\n## {today}\n", f"{len(rows)} files checked, {len(changed)} with differences.\n"]
        lines += [f"- {r['title']} ({r['studies']}): {'; '.join(r['issues'])}" for r in changed]
        if not LOG.exists():
            LOG.write_text(
                "# Revision checks\n\nResults of `shared.revision_check` "
                "(DATA_USE_POLICY §4 rule 11). Newest last.\n"
            )
        with LOG.open("a") as fh:
            fh.write("\n".join(lines) + "\n")
    return 1 if changed else 0


if __name__ == "__main__":
    sys.exit(main(log="--log" in sys.argv))
