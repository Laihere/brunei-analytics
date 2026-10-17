"""Fail if the rendered site loads anything from another site (DATA_USE_POLICY.md §8, rule 2).

Run after rendering: `uv run python -m shared.site_check dashboard/_site`. Links to other
sites (<a href>) are fine; scripts, styles, fonts, images and frames must be served from here.
"""

import re
import sys
from pathlib import Path

_EXTERNAL = r"(?:https?:)?//"
_HTML_LOADS = re.compile(
    rf"<(?:script|img|iframe|source|audio|video|embed)\b[^>]*\bsrc=[\"']?({_EXTERNAL}[^\"'\s>]+)"
    rf"|<link\b[^>]*\bhref=[\"']?({_EXTERNAL}[^\"'\s>]+)",
    re.IGNORECASE,
)
_CSS_LOADS = re.compile(rf"(?:@import\s+|url\()\s*[\"']?({_EXTERNAL}[^\"')\s]+)", re.IGNORECASE)
# <link> tags that only point elsewhere and load nothing.
_LINK_ONLY = re.compile(r"\brel=[\"']?(?:canonical|alternate|me|author)\b", re.IGNORECASE)


def external_loads(site: Path) -> list[tuple[str, str]]:
    found = []
    for path in sorted(site.rglob("*.html")):
        text = path.read_text(errors="ignore")
        for m in _HTML_LOADS.finditer(text):
            if m.group(2) and _LINK_ONLY.search(m.group(0)):
                continue
            found.append((str(path.relative_to(site)), m.group(1) or m.group(2)))
    for path in sorted(site.rglob("*.css")):
        for m in _CSS_LOADS.finditer(path.read_text(errors="ignore")):
            found.append((str(path.relative_to(site)), m.group(1)))
    return found


def main(site: str) -> int:
    found = external_loads(Path(site))
    for page, url in found:
        print(f"{page}: loads {url}")
    if found:
        print(f"{len(found)} resource(s) from other sites; serve them locally (policy §8).")
        return 1
    print("No resources loaded from other sites.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "dashboard/_site"))
