# Design Brief — Brunei Analytics

How the site looks, reads and behaves, and why. Design decisions are checked against this file.
Principles draw on [Laws of UX](https://lawsofux.com/) (§10).

- **Status:** accepted as the working draft, 15 Oct 2026. Refined through testing (§11).
- **Scope:** the Quarto site in `dashboard/` (landing page, case studies, sources, policy)

---

## 1. Design goal

> **A first-time visitor understands what a page is telling them within 10 seconds,
> and can confirm where the numbers came from within one click.**

### Principles

1. **Finding first, detail deeper.** Each page opens with the answer, and each layer below goes
   more specific: overview → breakdown → explanation → method (the inverted pyramid; "overview
   first, details on demand"). See §1.1.
2. **One idea per block.** One chart makes one point, and one section answers one question.
3. **Nothing unexplained.** Every number has a unit, a period and a source. Every term a non-analyst may not know is explained where it appears.
4. **Familiar over clever.** Standard layouts and controls, so nothing has to be learned.
5. **Honest and credited.** No chart exaggerates, and every chart shows its source (DATA_USE_POLICY.md).
6. **Light and accessible.** Fast on a phone, usable with a keyboard and a screen reader.

### 1.1 Layers of depth

| Layer | Reader's question | Page blocks |
|---|---|---|
| 1. Overview | What happened? | Headline, stat tiles, hero chart |
| 2. Breakdown | Where, when, for whom? | Supporting sections (by time, district, group, item) |
| 3. Explanation | Why, and how sure are we? | Drivers, comparisons, caveats |
| 4. Method | How do we know? | Method, sources, code (collapsed) |

Rules:
- **Stop anywhere.** A reader who leaves after any layer has a correct, complete takeaway. Each
  layer summarises the one below it, and no layer depends on the next.
- **Order by the reader's questions, not the analysis workflow.** Cleaning and exploration
  steps belong in layer 4.
- **Caveats travel with claims.** A limitation that changes how a layer-1 number should be read
  sits beside that number. Deeper means more detail, never more important information.

---

## 2. Audiences

| | Recruiter / hiring manager | Curious Bruneian | Analyst / peer |
|---|---|---|---|
| Arrives from | Portfolio, CV, LinkedIn | Shared link, social media | GitHub, portfolio |
| Time on page | 30–60 seconds | 2–3 minutes | 5+ minutes |
| Device | Laptop | **Phone** | Laptop |
| Wants to know | "Can this person turn data into clear insight?" | "What does this mean for me?" | "Is the method sound? Can I trust it?" |
| Reads | Headline, hero number, first chart | Headline, charts, plain-English takeaways | Method, sources, code |
| Success | Remembers one finding and the quality of the work | Understands the finding without jargon | Finds sources, steps and limitations in one click |

The page is ordered for all three: the recruiter stops at the top, the Bruneian reads the middle,
and the analyst reaches the end. Nobody has to wade through someone else's section to get to theirs.

### Top tasks (used for testing, §11)

1. Say what a case study found, after a 30-second look.
2. Find out how much a value changed over a given period.
3. Find which agency published the data, and when it was accessed.
4. Get from a case study to the next one, or back to the list.
5. Read a chart's values without relying on colour (table view).

---

## 3. Site structure

```
Home
├── Case studies          list of all studies
│   └── NN · {study}      one page per study
├── Data sources          approved sources and licences
├── Data use policy       how data is credited and handled
├── Glossary              every term with a pop-up definition, A–Z
└── About this site       design notes (this brief, summarised) and contact
```

- **Navigation:** 6 items at most, the same on every page (Hick's Law, Jakob's Law). Glossary
  was added as the sixth on 16 Oct 2026; on phones they collapse into the menu.
- **Portfolio link** at the top right, where people expect an "about the author" link.
- **URLs** are short and readable: `/case-studies/01-cost-of-living.html`.
- **Footer** on every page: disclaimer, policy link, author.

---

## 4. Page templates (low-fidelity)

### 4.1 Case study page — the main template

```
┌───────────────────────────────────────────────────────────┐
│ NAV  Brunei Analytics   Home  Case studies  Sources  …    │
├───────────────────────────────────────────────────────────┤
│ Case studies › 01                                         │  breadcrumb
│                                                           │
│ HEADLINE: the finding as a sentence                       │  ① answer
│ "Food prices rose 3× faster than overall prices in 2025"  │
│ Subtitle: the question · data period · 4-min read         │
│                                                           │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐                    │  ② key numbers
│ │ +4.1%    │ │ +1.3%    │ │ 12 of 14 │  ≤ 3 stat tiles    │
│ │ food CPI │ │ all CPI  │ │ items up │  label · value ·   │
│ └──────────┘ └──────────┘ └──────────┘  comparison        │
│                                                           │
│ ┌───────────────────────────────────────────────────────┐ │  ③ hero chart
│ │ Takeaway heading for the chart                        │ │  (chart card)
│ │ [ chart: one highlighted series, rest grey ]          │ │
│ │ Source: … (accessed …) · Analysis by … ; not official │ │
│ │ ▸ Show data table                                     │ │
│ └───────────────────────────────────────────────────────┘ │
│                                                           │
│ ## Section heading = takeaway                             │  ④ supporting
│ 2–4 short paragraphs + 1 chart card                       │     sections
│ (repeat: 2–4 sections)                                    │     (2–4)
│                                                           │
│ ⓘ What this doesn't tell us                               │  ⑤ caveats
│   limitations in plain words                              │     (callout)
│                                                           │
│ ▸ Method (collapsed)                                      │  ⑥ for analysts
│ ▸ Sources and full attributions (collapsed)               │
│ ▸ Code on GitHub                                          │
│                                                           │
│ ┌──────────────────────┐ ┌──────────────────────┐         │  ⑦ what next
│ │ ← Previous study     │ │ Next study →         │         │
│ └──────────────────────┘ └──────────────────────┘         │
├───────────────────────────────────────────────────────────┤
│ FOOTER  disclaimer · policy · author                      │
└───────────────────────────────────────────────────────────┘
```

**Standard structure (every case study; enforced by `tests/test_case_study_format.py`):**

| # | Part | How |
|---|---|---|
| 1 | Title | Front matter `title`: the finding, with the data year |
| 2 | Introduction | `::: {.study-intro}`: what, which data and years, scope, and **the questions the study asks** |
| 3 | Key numbers + main chart | `stat_tiles(...)`, then the hero `chart_card(...)` |
| 4 | Body | 2–4 `##` sections: the **investigation**. Headings name what is examined; chart titles state what the chart shows; no verdicts |
| 5 | Conclusion | `## Conclusion`: **the answers**, one per question in the introduction |
| 6 | Side note | `callout-caution` titled "What this doesn't tell us": what the study does and doesn't indicate |
| 7 | Method and references | `method_and_sources(...)`, references in APA 7 |

Comparisons always name their range ("2019 → 2025"), never just "since 2019".

**Rules**
- ①b **Intro (lede):** 2–3 sentences directly under the header: what the study looks at, which
  data and years, and its scope (e.g. "when and what changed, not why"). It sits between the
  header and the tiles, so it never pushes the hero chart far down.
- ① The headline is a finding, not a topic. "Food prices rose 3× faster…", not "Consumer Price Index Analysis".
- ② At most 3 stat tiles. Each has a label, a value and a comparison ("vs 2024"). No tile without a comparison.
- ③ The hero chart sits above the fold on a laptop. On a phone it comes straight after the tiles.
- ④ At most 4 sections. If there's more to say, it becomes another case study.
- ⑤ Caveats are always shown, never hidden. Being upfront about limits builds trust.
- ⑥ Method and sources are collapsed by default but always present.
- Reading time is shown in the subtitle, and a contents list sits in the side margin on desktop.

**On a phone:** a single column. Tiles stack 1 per row, or 3 compact tiles in one row if each value is 6 characters or fewer. Charts are full width with their legend above. The contents list moves to the top as a collapsible menu.

### 4.2 Home

```
HEADLINE   Brunei, explained with public data
One sentence: what the site is, who made it, that it's independent.

LATEST CASE STUDIES (5 newest)
[ Newest study — large card: headline finding, question, data period, read time ]
┌────────────┐ ┌────────────┐
│ 02 Theme   │ │ 01 Theme   │   next 4 newest: number, theme tag,
│ Headline   │ │ Headline   │   headline finding, data period, date
│ finding    │ │ finding    │
└────────────┘ └────────────┘
[ See all case studies → ]   (button to the case study list)

How this works: 3 short points (open data · credited · independent) → policy link
```

- Cards show the **finding**, not just the topic, so the home page is useful on its own.
- The home page shows only the 5 newest studies (Hick's Law); the full list is one click away.
- "Coming soon" cards (one at most, Zeigarnik Effect) appear on the case study list, not the home page.

### 4.3 Case study list

The same cards as the home page, newest first, with (`case-studies/_study-filters.html`):

- **Search box** over number, title, question, theme and data period.
- **Theme chips** built from the themes in use, "All topics" first. One active at a time
  (`aria-pressed`).
- **Sort:** newest published (default), latest data (last year of the data period), study number.
- A live count ("Showing 2 of 3 case studies") for screen readers.
- Controls stay hidden without JavaScript, so the plain list still works.

### 4.4 Sources, Policy, About

Plain reading pages with a contents list. Text at most 70 characters per line.

---

### 4.5 Machine learning case studies (later)

Same layers, with three additions:

| Layer | Content |
|---|---|
| 1. Overview | The result in plain words, **always with a range**, e.g. "likely 30–34k tonnes in 2027", and labelled *projection*. |
| 2–3. Breakdown and explanation | Main drivers, and accuracy **compared with a naive baseline** (e.g. "same as last year"). |
| 4. Method | Model choice, features, validation approach, code. |

- A model is only shown if it beats the naive baseline. Otherwise the case study says so, which is a finding too.
- Brunei series are often short (10–30 yearly points), so prefer simple, explainable models.
- Projections are our own analysis, never presented as official figures (policy M3, M5).

## 5. Components

Each component is built once (Quarto shortcode, Python helper or SCSS class) and reused.

| Component | Contents | Rules |
|---|---|---|
| **Stat tile** | label · value · comparison | Value in large semibold type. The comparison is signed ("+1.3 pts vs 2024") and its colour shows direction plus whether that's good or bad, always with an ▲/▼ icon, never colour alone. Max 3 per row. |
| **Chart card** | takeaway heading · chart · credit line · table toggle | One bordered card per chart (Common Region). The heading states the takeaway. The credit is generated by `shared/` and never typed by hand. |
| **Table toggle** | "Show data table" disclosure | Present on every chart. Keyboard-operable. The table carries units in its column headers. |
| **Callout** | icon · title · 1–3 sentences (or a short list with **bold lead-ins**) | Three uses: *Note* (context next to a number), *What was reported at the time* (news and studies, policy §7) and *Caveat* (limitation). Not used for decoration. The single most important sentence in a callout is bold. |
| **Glossary term** | dotted underline · pop-up with definition and "Not the same as" | Mark the first use on a page of a term readers may confuse: `[share of businesses]{.term term="share-of-businesses"}`. Definitions live once in `dashboard/glossary.yml`; terms that are easy to mix up list each other under `compare`, so the pop-up shows both. Opens on click/tap or keyboard (native `popover`); plain tooltip in older browsers. Every case study ends with `glossary_popovers(...)`; tests check every marked term exists. Not usable inside chart titles (they are plain text). |
| **Study card** | number · theme tag · headline finding · date | The whole card is clickable (Fitts's Law). |
| **Prev/next** | two cards | At the end of every case study. |
| **Breadcrumb** | Case studies › NN | At the top of case study pages. |

---

## 6. Writing rules

- **Plain English.** Write for a smart 15-year-old. Short sentences, active voice.
- **Headlines state findings**, and section headings state takeaways.
- **Always say when the data is from.** Headlines include the data year ("…in 2025"), and every
  study card and page header shows `Data: {period}` next to the publish date, so a reader never
  mistakes the publish date for the data date.
- **Byline with AI disclosure:** "Muhd Lai Razi Muhd Silmi with AI assistance (Claude)" in credit lines, and the
  fuller version in the footer, linking to "How AI was used" on the About page (policy rule 10).
- **Numbers:** always with unit and period, e.g. "BND 4.20 per kg (Mar 2025)" or "+3.1% year on year".
  Round to what the data supports: one decimal place for percentages, and no false precision.
- **Comparisons beat raw values.** "Up 12% since 2020" says more than "BND 4.20".
- **Dates:** "Mar 2025" in charts, "14 Oct 2026" in credits.
- **Names:** use the agency's own name, as the Data Source Owner, with the abbreviation after the first use.
- **Language:** English. Malay terms (e.g. *mukim*) are kept and explained the first time they appear.
- **No hedging stacks.** Say it once in the Caveats callout, rather than "may possibly suggest" in every paragraph.

---

## 7. Visual foundations

**Colour: turquoise theme** (chosen 15 Oct 2026). Tokens live in `docs/design/mockups/theme.css`.
Every text pair meets WCAG AA (≥ 4.5:1) and every chart mark ≥ 3:1. Chart palettes were checked
with the dataviz validator.

Turquoise is used in **three shades by job**, because classic turquoise (`#40e0d0`) is only 1.6:1
on white and can't carry text or thin marks:

| Token | Value | Contrast on surface | Use |
|---|---|---|---|
| teal-50 / teal-100 | `#e6f6f4` / `#ccefea` | — | tinted backgrounds (note callout, active nav, hover) |
| teal-500 | `#0d9488` | 3.65:1 | **brand mark**: highlighted chart series, accents, the logo |
| teal-700 | `#0f766e` | 5.33:1 | **text-safe**: links, buttons, active filter, kickers |
| teal-900 | `#134e4a` | 9.23:1 | footer band, strong text on tints |
| page / surface | `#f4f5f3` / `#fcfcfb` | — | page background / cards |
| ink / ink-2 | `#0b0b0b` / `#52514e` | 19.2 / 7.7:1 | body text / secondary text |
| muted | `#6b6863` | 5.40:1 | captions, credit lines, axis labels *(was `#898781`, 3.5:1, too faint for small text)* |
| line | `#e1e0d9` | — | gridlines, card borders |
| context | `#c3c2b7` | — | non-highlighted chart series |
| good / bad | `#006300` / `#b42318` | 7.35 / 6.40:1 | stat tile changes, always with ▲/▼ |
| caution | `#8a5a00` on `#fdf6e3` | 5.49:1 | caveat callout |

**Chart colours**

- **Default:** one series in teal-500, the rest in context grey (§8).
- **Categorical, when every series matters:** teal `#0d9488` → violet `#6250d6` → yellow `#eda100` →
  red `#e34948`, maximum 4. All pairs pass the colour-blind check (worst ΔE 11.9) and the
  normal-vision floor (20.8). Yellow is under 3:1, so those charts need direct labels or the table view.
  Red sits close to "bad", so it is the last slot and never used next to stat-tile status colours.
- **Sequential (magnitude, e.g. maps):** `#5ec4b8 → #2aa898 → #0d9488 → #0f766e → #134e4a`, validated.
- **Not used:** Brunei's flag colours (yellow, black, red, white) as the brand. Turquoise keeps
  the site visibly independent rather than official-looking (policy M3).
- **Dark mode:** later, with its own validated steps.

**Type:** the system sans font (fast, no web-font download).

| Role | Size / weight |
|---|---|
| Headline | 2rem / 700 |
| Section heading | 1.4rem / 650 |
| Stat value | 2.25rem / 600 |
| Body | 1.0625rem (17px) / 400, line-height 1.6 |
| Caption, credit | 0.8rem / 400, muted |

**Space:** 4px base scale (4, 8, 12, 16, 24, 32, 48, 64). Cards: 16px padding desktop, 12px mobile, 8px radius, 1px border in `grid`.
**Width:** body text at most 70ch, charts up to 960px, the page centred.

**Dark mode:** later. It needs its own validated palette (dataviz skill) rather than an automatic flip.

---

## 8. Chart rules

- **One chart, one message.** The takeaway heading says what to see.
- **Highlight one series** in teal-500, with the rest in the context grey (Von Restorff).
  Use full categorical colour only when every series matters equally, and then at most 4.
- **Label directly** at the line end or bar tip. Use a legend only when there are 2+ series and direct labels collide.
- **Bars start at zero.** Lines may zoom in, but the axis must say so.
- **No dual axes, no 3D, no pie charts with more than 3 slices.**
- **Hover tooltips** show exact value, unit and period. Interactivity is optional; no finding should need it.
- **Every chart** carries the credit line and the table view.
- **Alt text:** each chart has a one-sentence text summary of its takeaway for screen readers.
- **Item status.** When the items in a series change between the years compared, show each
  item's status with `shared.charts.item_status`: **continued** (in both years: normal colour),
  **new** (only in the later year: grey with diagonal stripes, label "(new in YYYY)") and
  **discontinued** (only in the earlier year: outline only, label "(not counted in YYYY)").
  Pattern plus label, never colour alone. New items are never counted as growth, nor
  discontinued items as decline: compare the continued items like for like. Patterned bars
  need Plotly's `fillmode="overlay"` (`NEW_PATTERN`), or they render transparent.

---

## 9. Accessibility and performance targets

| Target | Measure |
|---|---|
| WCAG 2.2 AA | Text contrast ≥ 4.5:1, interface elements ≥ 3:1, focus visible, keyboard-only navigation works |
| Lighthouse | Accessibility ≥ 95, Performance ≥ 90 (mobile) |
| Touch targets | ≥ 44 × 44 px |
| Colour independence | No information carried by colour alone (icons, labels, table view) |
| Page weight | Case study page ≤ 1.5 MB including Plotly, data ≤ 100 KB per chart |
| Response | Interactions (toggles, hover) feel instant, < 400 ms (Doherty Threshold) |
| Reduced motion | No animation beyond hover states, and none when `prefers-reduced-motion` is set |

---

## 10. Laws of UX → decisions

| Law | Decision in this site |
|---|---|
| Jakob's Law | Standard top nav, cards, breadcrumbs, "Show data table" disclosure. Nothing novel to learn. |
| Mental Model | Every case study follows the same order: answer → numbers → chart → detail → method. |
| Paradox of the Active User | No instructions needed. Findings stand on their own without filters or hovering. |
| Serial Position Effect | Finding first (headline), next step last (prev/next cards). |
| Peak-End Rule | Strongest chart early, and a clear ending with a caveat and a next study rather than a code dump. |
| Von Restorff Effect | One highlighted series per chart. One hero number per page. |
| Selective Attention | Takeaway headings tell readers what to look at. Context series fade to grey. |
| Pareto Principle | Design effort goes to the case study template, which most visits land on. |
| Hick's Law / Choice Overload | ≤ 5 nav items, ≤ 3 stat tiles, ≤ 5 theme filters, ≤ 2 chart controls. |
| Miller's Law / Working Memory | ≤ 4 sections per study, and at most 4 coloured series per chart. |
| Chunking | Short sections with takeaway headings. Method and sources tucked away in collapsible sections. |
| Cognitive Load | Plain English, glossary on first use, units on every number. |
| Law of Proximity | Credit line and table toggle sit directly under their chart. |
| Law of Common Region | Each chart and its parts live in one card. |
| Law of Similarity | Every stat tile, card and callout looks the same across the site. |
| Law of Uniform Connectedness | Prev/next cards and study cards share one style that signals "link". |
| Law of Prägnanz | Simple shapes, plenty of whitespace, no decoration. |
| Aesthetic-Usability Effect | A consistent, polished visual system makes readers more willing to trust the numbers. |
| Doherty Threshold | Static site and pre-computed data, so pages and interactions respond instantly. |
| Fitts's Law | Whole cards clickable, ≥ 44px targets, prev/next at the natural end of reading. |
| Postel's Law | Works on any screen size, browser, keyboard or screen reader. |
| Tesler's Law | Data cleaning, caveats and credits are handled by `shared/`. The reader sees one tidy credit line. |
| Occam's Razor | The simplest chart that makes the point. Remove anything that doesn't serve a reader task. |
| Goal-Gradient Effect | Reading time and a contents list show progress through longer studies. |
| Zeigarnik Effect | One "coming soon" card hints that the series continues. |
| Flow | No pop-ups or interruptions. Detail expands in place rather than opening new pages. |
| Cognitive Bias | Honest scales, stated caveats, no cherry-picked periods (policy M5). |
| Parkinson's Law | Applied to the work, not the UI: each case study is scoped to one question. |

---

## 11. Validation

Before launch, and again after each new template change:

1. **Automated:** Lighthouse (mobile) and an axe accessibility scan on Home and one case study.
2. **Keyboard pass:** reach every link, toggle and chart table without a mouse.
3. **Hallway test:** 5 people, at least 1 per audience, at least 2 on a phone. Each gets the top tasks in §2.
   We note task success, time, and where they hesitated. **Target:** 4 of 5 people complete
   tasks 1–3 without help.
4. **5-second test:** show the case study page for 5 seconds, then ask "what was this page about?"
   **Target:** 4 of 5 people recall the finding, not just the topic.

Findings and fixes go into a changelog at the end of this file. That log becomes evidence for the UX portfolio piece.

---

## 12. Open decisions

- [x] Wireframe tool: **HTML mock-ups** in `docs/design/mockups/` (15 Oct 2026; Figma considered first). Real pages that can be resized, tabbed through and opened on a phone, and their CSS carries over to the Quarto theme.
- [ ] Site name and tagline. "Brunei Analytics" and "Brunei, explained with public data" are placeholders.
- [ ] Theme filter on the list page: from launch, or only once there are 5+ studies
- [ ] Dark mode: when to add it
- [ ] Small multiples and long labels need a phone layout: `chart_card(mobile_fig=…)` swaps in a
  narrower version under 720px (first used in case study 01).
- [ ] Phone contents list: Quarto hides "On this page" on narrow screens. §4.1 asks for a collapsible list at the top.
- [x] First case study: **Cost of living in 2025: prices and subsidised items** (confirmed 15 Oct 2026).

## Changelog

| Date | Change | Reason |
|---|---|---|
| 15 Oct 2026 | First draft | — |
| 15 Oct 2026 | Accepted as working draft. Added layers of depth (§1.1) and ML case study layout (§4.5). | Confirmed the overview → detail order from the user's experience. Prepares for ML case studies. |
| 15 Oct 2026 | Low-fidelity HTML wireframes of Case study and Home pages (`docs/design/mockups/`). | First visual check of §4 layouts at desktop and phone widths. Thumbnail charts get a credit line too (policy M1). |
| 15 Oct 2026 | Turquoise theme: styled mock-ups (`theme.css`) with a Styled/Wireframe toggle. Colour tokens and chart palettes in §7. Muted text darkened to `#6b6863`. | User chose turquoise. Contrast checks showed it needs three shades by job, and the old muted grey failed AA for small text. |
| 15 Oct 2026 | Quarto theme built from the mock-ups: `dashboard/theme.scss`, case study title block, study card listings, and `shared/components.py`. Plotly's basic bundle is loaded once per case study page (1.2 MB vs 4.8 MB). | Moves the design into the live site. Charts use real-text credit lines rather than text drawn inside the image. |
| 15 Oct 2026 | AI-assistance disclosure in every byline and credit line, plus "How AI was used" on the About page. Study cards and headers show the data period. | The user asked for transparency that the work is made with AI assistance. Data year shown so readers don't confuse it with the publish date. |
| 15 Oct 2026 | First case study page. Added the intro (lede, §4.1 ①b), small multiples on one shared scale, a phone variant for charts that need one, and negative bar labels placed right of zero. | The user asked for a category timeline and a short introduction. Screenshot checks at 390px found overlapping titles and labels. |
| 15 Oct 2026 | Standard case study structure (§4.1) with a test. APA 7 references (publication year + retrieval date). Explicit ranges ("2019 → 2025"). Data tables scroll in their own box. "All items" explained where first used. | User review of case study 01. |
| 15 Oct 2026 | Questions in the introduction, evidence in the body, answers in the conclusion. | User's review: keeps verdicts in one place and makes the body an investigation. |
| 16 Oct 2026 | Home shows the 5 newest studies (1 large + 4 cards) and a "See all case studies" button. Case study list gets search, theme chips and sort (newest published, latest data, number). | User request. Search added before 10 studies by the user's choice; "latest data" sort because some datasets end years before they were published. |
| 16 Oct 2026 | Callouts are the standard way to highlight important points and context: bold lead-ins on list items, and the key sentence in bold. "What was reported at the time" added as a note callout for context sources. | The user likes highlighted points and notes because they help readers focus. |
| 16 Oct 2026 | Glossary: `dashboard/glossary.yml`, pop-up terms on case study pages (with "Not the same as" for easily confused pairs), and a Glossary page in the navbar. Item status (continued / new / discontinued) as a shared chart rule. | User requests: distinguish terms like share of businesses vs share of market value; keep separating staples from new additions, and show removed items too. |
