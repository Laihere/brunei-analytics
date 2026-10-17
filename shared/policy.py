"""Public version of DATA_USE_POLICY.md for the site.

Readers see what the data terms say and how they are followed. Internal working notes (the
SOP, open questions for EGNC, code notes) stay in the full policy on GitHub.
"""

import re

# free for all? · must do · accept · approved · context · privacy
PUBLIC_SECTIONS = [1, 2, 3, 6, 7, 8]
INTERNAL_SUBSECTIONS = ["### How the code applies this policy"]
INTERNAL_REFS = [  # point to notes that aren't on the site
    " (§4)",
    " See the review notes from 14 Oct 2026.",
]


def _link_repo_files(text: str, repo_url: str) -> str:
    """`DATA_SOURCES.md` or `shared/sources.py` → link to the file on GitHub."""
    text = text.replace("`brunei_analytics`", "this project")
    return re.sub(
        r"`([\w./-]+\.(?:md|py))`",
        lambda m: f"[{m.group(1)}]({repo_url}/blob/main/{m.group(1)})",
        text,
    )


def public_policy(text: str, repo_url: str) -> str:
    full_policy_url = f"{repo_url}/blob/main/DATA_USE_POLICY.md"
    body = text.split("\n", 1)[1]  # drop the document's own H1; the page has a title
    head, *sections = re.split(r"(?m)^(?=## \d+\. )", body)
    kept = []
    for section in sections:
        number = int(re.match(r"## (\d+)\.", section).group(1))
        if number not in PUBLIC_SECTIONS:
            continue
        for sub in INTERNAL_SUBSECTIONS:
            section = section.split(sub)[0]
        new_number = PUBLIC_SECTIONS.index(number) + 1
        section = re.sub(r"^## \d+\.", f"## {new_number}.", section, count=1)
        kept.append(section.rstrip().rstrip("-").rstrip() + "\n\n")
    out = head + "".join(kept)
    for ref in INTERNAL_REFS:
        out = out.replace(ref, "")
    # Sections are renumbered on the site, so cross-references follow them.
    out = re.sub(
        r"§(\d+)",
        lambda m: (
            f"§{PUBLIC_SECTIONS.index(n) + 1}"
            if (n := int(m.group(1))) in PUBLIC_SECTIONS
            else m.group(0)
        ),
        out,
    )
    out = _link_repo_files(out, repo_url)
    return (
        out.rstrip()
        + "\n\n---\n\nThis page shows the parts of the policy that concern readers. The "
        f"[full policy]({full_policy_url}), including the project's working rules, is on GitHub.\n"
    )
