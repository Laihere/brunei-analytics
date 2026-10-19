# Choosing a chart type

Repo-only notes (not rendered on the site), started 19 Oct 2026. Bar and line charts stay the
default. The less common types below are used **only when the data has the shape they need**;
otherwise they mislead. The general chart rules are in `DESIGN.md` §8.

## Which shape each chart needs

| Chart | Data shape it needs | Don't use it when |
|---|---|---|
| Sunburst / treemap | Values that **add up** to a meaningful total, nested 1–2+ levels (BND, counts, people) | Values are prices, rates or indexes (they don't add up) |
| Hierarchy tree (collapsible, equal-size nodes) | A category → item structure; colour can show a value such as % change | Node size would be read as an amount the data doesn't have |
| Network / node-link | Rows that are **links**: from A → to B, with a value | Items are just listed together (no real links) |
| Sankey | Quantities **flowing** through stages or from source to destination | Stages don't conserve quantity and the gap isn't explained |
| Radial / polar time chart | **Monthly** (or finer) data with a yearly cycle, several years | Data is annual only |
| Map (choropleth) | Values by **district** (4) or mukim | Only one area, or counts that should be rates (shade by share or per person, not raw totals of unlike areas) |
| Infographic (icons, waffles, big numbers) | One or two plain facts, e.g. "7 in 10 businesses are in Brunei-Muara" | It would replace the chart and table; it is an extra, never the only view |

Quick test for any dataset:
- Do the numbers add up to a meaningful total? If so, use a sunburst or treemap.
- Is each row "A → B"? If so, use a network or Sankey.
- Is it monthly with a yearly cycle? If so, use a radial time chart.
- Is it by district? If so, use a map.

### Map rules

Boundaries: geoBoundaries district file, approved 19 Oct 2026 (policy §6). Shapes are built once
by `case_studies/_shared/build_maps.py` into `_shared/outputs/brunei_districts.csv`; draw with
`shared.svg.district_map`. Each page with a map links geoBoundaries, cites Runfola et al.
(2020) and says the boundaries are approximate and not an official map.

- Boundary files must come from a source with clear reuse terms. Add it to `DATA_USE_POLICY.md`
  §6 (approved sources) and `shared/sources.py` first, and credit it.
- Self-host the boundary file (GeoJSON in the repo). No third-party map tiles or map scripts,
  because the site collects nothing and loads nothing from third parties (policy §8).
- Temburong is small in population, so district shading should use shares or rates, never
  raw counts of people. Keep the small-count rule (no published cell ≤ 5).
- Always show the same numbers in a table, as with every chart.

## Candidates on data.gov.bn (checked 19 Oct 2026)

From the portal sitemap (535 unique titles) and a look inside each file. "Shape" is what
was actually in the file.

| Dataset (owner as listed) | Years | Shape in the file | Fits |
|---|---|---|---|
| Monthly Import By Port & Country (CIF value) and (Quantity) (MIPR) | 2010 | category × entry port × country × month | Radial (monthly), Sankey (port → category), map of entry points |
| Import Of Agriculture Product By Types And Country (MIPR) | 2013 | category → country, BND | Network / Sankey (country → category), treemap |
| Import By Country Of Origin (DEPD, yearbook 6.9) | 2009–2013 | region → country, BND million | Treemap / sunburst (region → country), network to Brunei |
| Tourists Arrival By Country Residence (Immigration, yearbook 22.1) | 2009–2013 | region → country, persons | Treemap / sunburst, map of origins |
| Arrivals By Nationality And Purpose Of Visit (Tourism Development Dept) | 2013 | region → country → purpose, persons | Sankey (region → purpose), sunburst (3 levels) |
| Total Population By Racial Groups And Districts (DEPD) | 2001–2013 | year × race, year × district | District map, treemap of shares |
| Mid-Year Population Estimate By District, Race And Sex (DEPD) | 2013 | district × race × sex | Map + sunburst (district → race → sex) |
| Registered Live Births By District (DEPS) | 2000–2018 | year × district | District map, small multiples |
| Overall Yield Of Rice By Season And District (Agriculture and Agrifood Dept) | 2012/13 | season × district: farmers, hectares, kg | District map |
| Number Of Schools By Level And District (MOE) | — | level × district (has a definitions sheet) | District map, treemap |
| Temperature, Humidity, Rainfall and Sunshine, Brunei International Airport (Meteorological Dept) | annual | year × measure | Line charts only (annual, so not radial) |
| Government Health Budget And Expenditure (MOH) | 2017/18 on | indicators by year | Line / bar only |

Also seen but not opened: monthly local chicken meat, vegetable and cut-flower production
by district (2011, 2014), registered deaths and marriages by district, notifiable infectious
diseases, hospital morbidity, passenger movement, arrivals by air/sea/land.

## Existing case studies that could take a second chart type

| Study | Data | Possible extra view |
|---|---|---|
| 04 Fire occurrences | fires by district by year | District map (share of fires): **on hold**. Shares of fires mostly follow where people live, so a map would need fires per person, which needs a population series for 2009–2020 |
| 05 Agrifood processing | businesses, employees, value by district, 2013 | **Done 19 Oct 2026:** three district maps (chart 5). Infographic still possible |
| 06 Livestock supply | local vs imported; day-old chick → broiler → slaughter | **Not suitable (checked 19 Oct 2026):** the stages don't conserve quantity (2020: 19.5M hatching eggs, 19.4M chicks, 17.6M birds slaughtered; meat in tonnes) and the tables don't say what fills the gaps, so a Sankey would invent flows |
| 07 Trade | trade by SITC section, BND (adds up) | **Done 19 Oct 2026:** import treemaps, 2018 vs 2021, same scale (chart 5) |
| 02 Crime statistics | cases by offence group (counts add up) | **Not suitable (checked 19 Oct 2026):** police and other-agency tables count different kinds of cases, so one treemap would imply an "all crime" total the source doesn't give; police-only would repeat chart 1 |
| 01 Cost of living | CPI by group (indexes, don't add up) | Hierarchy tree coloured by % change only; no sunburst |

New chart types are drawn as static SVG with `shared/svg.py` (DESIGN.md §8). Any extra view
is added with a dated "Update" note and an `updated:` date in the front matter (see `docs/WORKFLOW.md`); the original
findings are not rewritten.
