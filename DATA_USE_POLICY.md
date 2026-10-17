# Data Use Policy — Brunei Open Data (data.gov.bn)

Our working reference for using datasets from [data.gov.bn](https://www.data.gov.bn/) in this project.
Every analysis, chart, dashboard and write-up in `brunei_analytics` follows this note.

- **Terms reviewed:** 14 Oct 2026
- **Governing document:** [Data Policy: Terms of Use](https://www.data.gov.bn/data-policy-terms-of-use/)
- **Supporting pages:** [FAQ](https://www.data.gov.bn/frequentlyaskedquestion/), [Principles](https://www.data.gov.bn/principles/), [About](https://www.data.gov.bn/about-us/)
- **Contact:** E-Government National Centre (EGNC), Simpang 69-18, Jalan E-Kerajaan, Gadong, BE1110 — data@egnc.gov.bn

> The terms "may change from time to time without notice". Re-read them before each data download
> and before each publication, and update the review date above.

---

## 1. Is it free for all?

Yes. The portal states this in three places:

| Source | Statement |
|---|---|
| Terms of Use | "data available on Data.gov.bn is offered free and without other restrictions" (subject to the conditions in §2) |
| FAQ | "everyone and anyone would be able to freely download any data that has been published on the portal"; users "range from the general public to businesses or even other government agencies" |
| FAQ | data may be analysed, fed into "business intelligence systems, data mining tools, or other analytical tools", and "multiple datasets could be combined to create new knowledge and insight" |
| Principles | published data adopts the Data Policy "to ensure that it can be used freely"; datasets are chosen to "promote analysis and reuse" |

No registration is required. The terms do not name a standard licence (e.g. Creative Commons).

**Ownership:** "all datasets uploaded onto the portal are still owned by the respective agency and not EGNC or DEPS" (FAQ).
Each dataset page names its owner under **Data Source Owner**. That owner is the one we credit.

- Copy the owner exactly as shown on the page. Spellings vary across datasets (e.g. "JPES" vs "Department of Statistics, JPES"), so don't normalise them.
- 37 datasets (mostly GDP series) show "Dataset owner not available". Credit those as *"Brunei Open Data (data.gov.bn); data source owner not stated"*.

---

## 2. What we MUST do (from the Terms of Use)

| # | Condition (quoted) | How we comply |
|---|---|---|
| M1 | "must contain the proper attribution detailing the source of the datasets and the date the datasets were accessed or downloaded" | Every chart, dashboard and write-up carries a source line with the owning agency, data.gov.bn, the dataset title and the download date (§3). Download dates are logged in `DATA_SOURCES.md`. |
| M2 | "should clearly indicate any analysis or transformation of data made by the use" | Each output states what we did (cleaning, aggregation, derived metrics, joins). The transformation steps are kept in code and summarised in `DATA_SOURCES.md`. |
| M3 | "and shall not be attributed to the Government of Brunei Darussalam" | Every output has a "not an official publication" disclaimer. No government logos or crests, and no wording that implies endorsement. |
| M4 | "Upon the request of the Government of Brunei Darussalam, all users must cease to use the datasets and remove them" | `DATA_SOURCES.md` records where each dataset is used, so it can be removed quickly. Raw files are not committed (§4), which keeps removal simple. |
| M5 | "must not use the data for purposes deemed inappropriate and/or misleading to the general public" | Honest charts: zero-based bar axes, stated units and periods, gaps and series breaks flagged, no cherry-picked windows, and correlation not presented as causation. |

**Breach:** breaking any condition cancels our licence to use the datasets. The disclaimer, indemnity and governing-law terms still apply after that.

## 3. What we accept by using the data

- **Acceptance:** "By accessing and using the datasets … you shall be deemed to have accepted to be legally bound by these Terms of Use."
- **As-is:** no warranty of accuracy, timeliness or fitness for purpose. We validate the data ourselves and note known issues.
- **No liability:** the government is not liable for loss from use of, or inability to use, the data.
- **Removal:** datasets can disappear without notice. We keep our own dated copy locally (§4).
- **Indemnity:** we indemnify the government against claims arising from our use, our breach, or third-party use of our derived analyses or applications. Another reason to keep outputs accurate and clearly unofficial.
- **Law:** Brunei law governs, with exclusive jurisdiction of Brunei courts.

---

## 4. Our working rules (SOP)

1. **Read the terms first.** Before downloading, re-check the Terms of Use page for changes.
2. **Log every download** in `DATA_SOURCES.md`: dataset title, URL, Data Source Owner, edition, coverage, file name, download date, and where it is used. Files are stored as `data/raw/<source>/<edition>/<dataset-slug>/` with a `.meta.json` record. Problems found in source data go in its "Known issues" section before any correction.
3. **Raw data stays local.** `data/raw/` is gitignored. So is `data/clean/`, our full cleaned tables (kept for follow-ups and new editions; they are neither the published datasets nor our findings, and may hold small counts). The public repo holds code, the catalogue and our own outputs, and links back to the original dataset pages. *(Redistributing raw files is not addressed by the terms; this rule stands until EGNC confirms otherwise.)*
4. **Mark every transformation.** Steps live in code, with a plain-language summary in each output.
5. **Attribute every output** using the template below.
6. **Add the disclaimer to every output**, including dashboards, the portfolio case studies and the README.
7. **Protect privacy.** Brunei's Personal Data Protection Order 2025 (fully in force 1 Jan 2026) applies to personal data. Published sets are aggregates, but we do not try to re-identify individuals or join datasets in ways that could. We merge or suppress small cells (counts of 1 to 5) in breakdowns by place, year or category; see §8.
8. **Stay neutral.** Present findings factually and avoid political commentary or claims about government performance that the data does not support.
9. **Respect the server.** Fetch the catalogue through the site's public API, add delays between requests, and download each file once.
10. **Disclose AI assistance.** This project is built with an AI assistant (Claude, by Anthropic).
    Every byline and credit line says so, and the site's About page explains what the AI did and
    what the author did. The author reviews every finding and is responsible for what is published.

### Attribution template (APA 7)

References use APA 7 for datasets, with the retrieval date that the data.gov.bn terms require (M1).
They are generated by `shared.provenance.apa_reference`:

> Department of Statistics, JPES. (2026). *Consumer price index 2025* [Data set]. Brunei Open Data. Retrieved October 15, 2026, from https://www.data.gov.bn/consumer-price-index-2025/

The year is when the dataset was published on the portal (n.d. if unknown); the retrieval date is
when we downloaded it. When one reference list has several works by the same author in the same year,
APA adds a, b, c in title order (2026a, 2026b; n.d.-a), and identical titles follow edition
order. `shared.provenance.apa_year_labels` does this. CC BY sources add "Licensed under CC BY 4.0." and redistributed data adds
"Original data from …". Chart notes use the short form: "Source: {owner} ({year}), via data.gov.bn,
retrieved {date}. Analysis by … with AI assistance (Claude); not an official government publication."

#### Earlier plain-text template (kept for reference)

> **Source:** {Data Source Owner}, "{Dataset title}", Brunei Open Data (data.gov.bn), {dataset URL}, accessed {DD Mon YYYY}.
> **Notes:** {transformations, e.g. "Annual totals aggregated from monthly figures; 2020–2021 rebased by the author."}
> Analysis by Muhd Lai Razi with AI assistance (Claude). Not an official publication of the Government of Brunei Darussalam.

Short form for chart footers:

> Source: {Data Source Owner} via data.gov.bn (accessed {DD Mon YYYY}). Analysis by Muhd Lai Razi with AI assistance (Claude); not an official government publication.

---

## 5. Open questions for EGNC

Questions for the enquiry email to data@egnc.gov.bn:

1. May cleaned or raw copies of datasets be published in a public GitHub repository, or should we only link to data.gov.bn?
2. Does our attribution template meet the "proper attribution" requirement, or is there a preferred format?
3. Do the owning agency's own website terms (e.g. DEPS: www.deps.gov.bn/terms-of-use) also apply to files downloaded from data.gov.bn?
4. Is a personal, non-commercial portfolio with public dashboards within the intended use? (The FAQ suggests yes.)
5. For datasets marked "Dataset owner not available" (e.g. the GDP series), who should be credited?

| Date | Status |
|---|---|
| 14 Oct 2026 | Draft prepared; not yet sent |

---

## 6. Approved sources

Only these sources are used, chosen for clear terms that allow free reuse with credit.
Each is registered in `shared/sources.py`, and the code refuses to download from or
credit anything else. Adding a source means updating this table first.

| Source | Licence | Terms | Specific conditions |
|---|---|---|---|
| Brunei Open Data (data.gov.bn) | Data.gov.bn Data Policy | [Terms of Use](https://www.data.gov.bn/data-policy-terms-of-use/) | Everything in §2. Credit the Data Source Owner and the access date. |
| World Bank, World Development Indicators | CC BY 4.0 | [Summary Terms of Use](https://data.worldbank.org/summary-terms-of-use) | Some indicators come from other organisations and carry their own licence. Check each indicator's page and record any exception in the `licence` field. No World Bank logo, and no implied endorsement. **Indicators originally from the IMF** (e.g. CPI and inflation, from IMF International Financial Statistics) are allowed when the World Bank metadata states CC BY 4.0: credit "original source: IMF International Financial Statistics" and show values unaltered (decided 15 Oct 2026). |
| FAO, FAOSTAT | CC BY 4.0 (FAO Open Data Licensing policy, 2025) | [Database Terms of Use](https://www.fao.org/contact-us/terms/db-terms-of-use) | Cite FAO, the database, the access date and the URL. No attempts to de-anonymise data. Show FAO's estimate/imputed flags, since many Brunei values are estimates. |
| ILO, ILOSTAT | CC BY 4.0 (datasets from 3 May 2023) | [Rights and permissions](https://www.ilo.org/node/9321) | Use national survey series rather than ILO modelled estimates where both exist. Microdata is not covered. |

Not approved for now: IMF directly (only via World Bank, above), WHO, BDCB, UN Comtrade, ASEANstats, Our World in Data,
OpenStreetMap, ADB, Open-Meteo and geoBoundaries. See the review notes from 14 Oct 2026.
Open-Meteo and geoBoundaries (Brunei boundaries are public domain) are the first
candidates to add if a case study needs weather history or maps.

### How the code applies this policy

- `shared/fetch.py` saves each download once to `data/raw/<source>/`, with a `.meta.json`
  record of the title, page URL, owner and access date.
- `shared/outputs.py` refuses to save a case study output without its source records and
  a note of the transformations (M1, M2).
- `shared/provenance.py` builds the full attribution (§4) and the chart footer from
  those records, so credit lines never have to be typed by hand.
- `shared/charts.py` adds the footer to every chart and provides the table view.
- Case study outputs (small processed CSVs and their `.meta.json` files) are committed.
  Raw downloads are not.

---

## 7. Context sources (news, articles, journals)

Agreed 16 Oct 2026. Context sources help explain *what was happening* around a finding. They are
not data sources: §6 still decides where every charted number comes from.

### Rules

1. **No numbers from context sources in charts, tiles or calculations.** A figure quoted in a
   news article may be mentioned in the text, attributed to that article, but it never replaces
   or adds to the data.
2. **Never name or point to individuals.** Cite articles about policies, laws, campaigns and
   official statements, not reports of specific crimes, crashes or victims (Personal Data Protection Order 2025).
3. **Use the most authoritative source available**, in this order (updated 16 Oct 2026: the
   author prefers peer-reviewed sources):
   1. Peer-reviewed journals and university publications, preferably including Brunei-based
      scholars (e.g. Universiti Brunei Darussalam, Universiti Teknologi Brunei).
   2. Official publications and press releases: ministries, departments, the Royal Brunei
      Police Force, the Government Gazette, official agency websites (`*.gov.bn`), and
      intergovernmental bodies such as ASEAN. Best for facts about what the government did
      (dates, launches, laws).
   3. Established news outlets, e.g. Borneo Bulletin, Pelita Brunei, RTB News, The Scoop.
      Used when neither of the above covers the point, ideally alongside one that does.

   Not used: blogs, social media, forums, or anything without a named publisher.
4. **Report, don't conclude.** Write "In 2012, X was reported (Source, 2012)", not "the fall was
   caused by X". The data still can't show causes, and the page says so.
5. **Every source is opened and checked** before it is cited, including the date and that it
   says what we report. Nothing is cited from memory, including by the AI assistant. Important
   points need two independent sources, or are marked as reported by one.
6. **Paraphrase; quote little.** At most a short quote in quotation marks. No copied images,
   tables or long passages.
7. **Keep it findable.** Record the access date, and save an archived copy (Internet Archive,
   web.archive.org) for news pages, since Brunei news links often move or disappear.
8. **Separate from findings on the page.** Context appears in a callout titled "What was
   reported at the time", never in the stat tiles or the conclusion's answers.

### References (APA 7)

Context sources go in the same reference list as the datasets, for example:

> Author, A. (2012, March 5). Title of the article in sentence case. *Borneo Bulletin*. URL

> Royal Brunei Police Force. (2012, March 5). *Title of the press release* [Press release]. URL

> Author, A., & Author, B. (2015). Title of the article. *Journal Name, 12*(3), 45–67. https://doi.org/…

Each source is logged in `CONTEXT_SOURCES.md` with its URL, archive link, access date and the
case study it supports.

**Names.** Author names are written exactly as published, including honorifics such as
"Hajah", "Haji", "Dato" or "Pengiran" (author's decision, 16 Oct 2026). Malay names usually
have no family name, so the full name stands in the author position and the in-text citation.

---

## 8. Privacy and security

Agreed 17 Oct 2026. The site is read-only: it has no forms, accounts, comments or search box
that sends anything anywhere (the site search runs in the browser).

1. **The site collects nothing.** No cookies, analytics, tracking pixels, ads or embedded
   social media. The site is hosted on GitHub Pages, and GitHub may log visitors' IP addresses
   for security, as described in the
   [GitHub Privacy Statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement).
   If analytics are ever added, a privacy notice comes first (Personal Data Protection Order 2025).
   **No cookies are set.** Quarto, which builds the site, can save a display setting in the
   browser's local storage, but only for features this site doesn't use (reader mode, tabs,
   announcement bars), so in practice nothing is stored, and nothing would ever be used for
   tracking. That is why there is no cookie banner.
2. **No scripts from other sites.** Every script, style and font is served from this site
   (Plotly is a copy of the official file, checked by its SHA-256 hash), so no other server
   learns who reads which page, and a compromised CDN cannot change the pages.
3. **No small counts.** Counts of people, incidents or businesses between 1 and 5 are not
   published in a breakdown by place, year or category, because a small number can point to a
   real person or business. Such cells are merged (e.g. into "Other" or a longer period) or
   shown as "5 or fewer". Totals for the whole country are not affected. Zero is shown as zero.
4. **No personal data from any source.** We use published aggregates only, never try to
   re-identify anyone, and never name or point to individuals (§7, rule 2).
5. **No pop-ups or dark patterns.** No sign-ups, consent walls, ads or prompts. The "not
   official, not peer-reviewed" notice is a line under every case study title, always visible,
   so it is seen even by readers who arrive from a shared link.

### Software and licences

Everything the site sends to a visitor's browser, checked 17 Oct 2026. All are permissive
open-source licences. The site uses the visitor's own system fonts and has no images.

| Component | Used for | Licence |
|---|---|---|
| [Plotly.js](https://github.com/plotly/plotly.js) 4.1.1 (basic bundle) | charts | MIT |
| [Quarto](https://quarto.org) 1.10 page scripts | navigation, search, contents | MIT |
| [Bootstrap](https://getbootstrap.com) 5.3 | layout and styles | MIT |
| [Bootstrap Icons](https://icons.getbootstrap.com) 1.13 (icon font) | GitHub, profile and search icons | MIT |
| [Popper](https://popper.js.org) 2.11 and [Tippy.js](https://github.com/atomiks/tippyjs) | glossary and footnote pop-ups | MIT |
| [Fuse.js](https://www.fusejs.io) 6.6 and [Algolia Autocomplete](https://github.com/algolia/autocomplete) 1.19 | site search (runs in the browser) | Apache 2.0 / MIT |
| [List.js](https://github.com/javve/list.js), [Headroom.js](https://github.com/WickyNilliams/headroom.js) 0.12, [clipboard.js](https://clipboardjs.com) 2.0 | case study list, header, copy buttons | MIT |

The Python packages used to build the site (pandas, Plotly, pandera and others in
`pyproject.toml`) run only on the author's computer and in GitHub Actions; they are checked
for known vulnerabilities with `pip-audit`, and Dependabot proposes updates.

### How the code applies this policy

- `tests/test_privacy.py` fails if a committed output has a count between 1 and 5, unless the
  cell is listed there with a reason.
- `shared/html.py` keeps page components from pulling in RequireJS and jQuery from a CDN.
- The GitHub Actions workflow fails the build if any rendered page loads a script, style or
  font from another site. Workflow actions are pinned to commit SHAs and kept up to date by
  Dependabot (`.github/dependabot.yml`).
- Raw downloads (`data/raw/`) and full cleaned tables (`data/clean/`) stay local and are
  gitignored. Keep a private backup of `data/` (an encrypted drive or private cloud folder,
  not a GitHub repository).

---

## 9. Corrections and removal requests

Agreed 17 Oct 2026. Contact: **laihere281@gmail.com**.

1. **Corrections.** Anyone can report a mistake. Each report is checked against the source
   data; if it is right, the page is corrected and gains a dated note saying what changed.
   Findings are not silently rewritten.
2. **Removal at the request of the Government or a data owner** (e.g. EGNC or the agency that
   owns a dataset) is always honoured, as the data.gov.bn terms require. Before acting, the
   request is confirmed as genuine: it must come from an official government email address
   (ending in `.gov.bn`), or be confirmed through contact details on the agency's own
   official website. A request from a personal email address, or one that can't be confirmed,
   is answered by asking for that confirmation, not acted on.
3. **A person who believes a page identifies them** is taken seriously even though only
   published aggregates are used: the page is reviewed, and anything that could point to a
   person is merged or removed (§8, rule 3). Nobody is asked for identity documents.
4. **The author** may remove any case study at any time.
5. **What removal involves.** The page, its outputs and its reference entries are deleted
   from the site and the repository. If the content must also leave the public Git history,
   the history is rewritten and GitHub is asked to clear cached copies; the requester is told
   when that is done.

### Request log

Record each request here: date received, who (organisation, not personal details), how it
was confirmed, what was asked, what was done and when.

| Received | From | Confirmed by | Request | Action and date |
|---|---|---|---|---|
| | | | | |
