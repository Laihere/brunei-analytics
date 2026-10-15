"""Build a catalogue of data.gov.bn datasets.

Uses the portal's public WordPress API for dataset and file listings, and each
dataset page for its "Data Source Owner". Responses are cached in CACHE_DIR so
the site is only hit once per item.

    python3 -I catalogue/build_catalogue.py CACHE_DIR OUT_CSV
"""

import csv
import html
import json
import re
import sys
import time
import urllib.request
from collections import defaultdict
from pathlib import Path

BASE = "https://www.data.gov.bn"
DELAY_S = 1.0
UA = {"User-Agent": "Mozilla/5.0 (brunei_analytics catalogue; personal research)"}


def fetch(url, path):
    if path.exists():
        return path.read_bytes()
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as resp:
        body = resp.read()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    time.sleep(DELAY_S)
    return body


def fetch_paged(endpoint, prefix, cache, fields):
    items, page = [], 1
    while True:
        url = f"{BASE}/wp-json/wp/v2/{endpoint}?per_page=100&page={page}&_fields={fields}"
        batch = json.loads(fetch(url, cache / f"{prefix}{page}.json"))
        items += batch
        if len(batch) < 100:
            return items
        page += 1


def page_owner(raw):
    text = re.sub(r"<[^>]+>", "\n", raw.decode("utf-8", "replace"))
    lines = [html.unescape(line).strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    for i, line in enumerate(lines):
        if line == "Data Source Owner" and i + 1 < len(lines):
            return lines[i + 1]
    return ""


def main(cache_dir, out_csv):
    cache = Path(cache_dir)
    cats = json.loads(
        fetch(f"{BASE}/wp-json/wp/v2/categories?per_page=100&_fields=id,name", cache / "cats.json")
    )
    cat_name = {c["id"]: c["name"] for c in cats if c["name"] != "Dataset"}

    post_fields = "id,date,modified,slug,link,title,categories,content"
    posts = fetch_paged("posts", "full", cache, post_fields)
    media = fetch_paged("media", "media", cache, "id,post,date,mime_type,source_url")

    files = defaultdict(list)
    for m in media:
        if m.get("post"):
            files[m["post"]].append(m["source_url"])

    rows = []
    for p in posts:
        owner = page_owner(fetch(p["link"], cache / "pages" / f"{p['id']}.html"))
        urls = [BASE + u if u.startswith("/") else u for u in files[p["id"]]]
        rows.append(
            {
                "id": p["id"],
                "title": html.unescape(p["title"]["rendered"]).strip(),
                "category": "; ".join(cat_name[c] for c in p["categories"] if c in cat_name),
                "owner": owner,
                "published": p["date"][:10],
                "modified": p["modified"][:10],
                "n_files": len(urls),
                "formats": "; ".join(sorted({Path(u).suffix.lower().lstrip(".") for u in urls})),
                "page_url": p["link"],
                "file_urls": " | ".join(urls),
            }
        )

    rows.sort(key=lambda r: (r["category"], r["owner"], r["title"], r["published"]))
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} datasets -> {out_csv}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
