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
3. **Raw data stays local.** `data/raw/` is gitignored. The public repo holds code, the catalogue and our own outputs, and links back to the original dataset pages. *(Redistributing raw files is not addressed by the terms; this rule stands until EGNC confirms otherwise.)*
4. **Mark every transformation.** Steps live in code, with a plain-language summary in each output.
5. **Attribute every output** using the template below.
6. **Add the disclaimer to every output**, including dashboards, the portfolio case studies and the README.
7. **Protect privacy.** Brunei's Personal Data Protection Order 2025 (fully in force 1 Jan 2026) applies to personal data. Published sets are aggregates, but we do not try to re-identify individuals or join datasets in ways that could. We suppress or merge very small cells (e.g. counts below 5) when cross-tabulating.
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
